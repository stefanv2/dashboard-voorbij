#!/usr/bin/env python3
from __future__ import annotations

import argparse
import configparser
import gzip
import ipaddress
import json
import math
import os
import re
import tempfile
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import unquote, urlsplit
from zoneinfo import ZoneInfo


LOG_RE = re.compile(
    r'^\[(?P<timestamp>[^\]]+)\]\s+-\s+'
    r'(?P<upstream>\S+)\s+(?P<status>\d{3})\s+-\s+'
    r'(?P<method>[A-Z]+)\s+(?P<scheme>\S+)\s+(?P<host>\S+)\s+'
    r'"(?P<path>[^"]*)"\s+\[Client (?P<ip>[^\]]+)\]\s+'
    r'\[Length [^\]]+\]\s+\[Gzip [^\]]+\]\s+\[Sent-to [^\]]+\]\s+'
    r'"(?P<ua>[^"]*)"\s+"(?P<referrer>[^"]*)"$'
)

STATIC_EXTENSIONS = {
    ".css", ".js", ".mjs", ".map", ".png", ".jpg", ".jpeg", ".gif",
    ".svg", ".webp", ".ico", ".avif", ".woff", ".woff2", ".ttf",
    ".otf", ".eot", ".mp3", ".wav", ".ogg", ".mp4", ".webm", ".pdf",
    ".zip",
}

BACKGROUND_PREFIXES = (
    "/minecraft-status/status.json",
    "/minecraft-status/visitors.json",
    "/api/music",
    "/api/health",
)

BOT_RE = re.compile(
    r"bot|spider|crawler|crawl|scan|slurp|curl|wget|python-requests|"
    r"go-http-client|libwww|zgrab|masscan|nmap|censys|shodan|expanse|"
    r"internetmeasurement|semrush|ahrefs|mj12bot|bytespider|"
    r"headlesschrome|uptimerobot|statuscake|probe",
    re.I,
)

THREAT_PATTERNS = (
    ("Environment leak", "high", re.compile(
        r"(?:^|/)\\.env(?:[./]|$)|/(?:config|settings|secrets?|credentials?)"
        r"(?:[._/-]|$)", re.I)),
    ("Git exposure", "high", re.compile(
        r"(?:^|/)\\.git(?:[./]|$)|(?:^|/)\\.svn(?:[./]|$)", re.I)),
    ("WordPress probe", "medium", re.compile(
        r"/(?:wp-admin|wp-login\\.php|wp-content|wp-includes|xmlrpc\\.php)"
        r"(?:/|$)", re.I)),
    ("Database admin probe", "medium", re.compile(
        r"/(?:phpmyadmin|pma|adminer|mysql|dbadmin)(?:/|$)", re.I)),
    ("PHPUnit/Laravel RCE probe", "critical", re.compile(
        r"/vendor/phpunit|/laravel|/_ignition|/telescope", re.I)),
    ("Web shell probe", "critical", re.compile(
        r"(?:^|/)(?:shell|cmd|webshell|eval|upload|file\\d*)\\."
        r"(?:php|phtml|asp|aspx|jsp)(?:$|\\?)", re.I)),
    ("CGI exploit probe", "high", re.compile(
        r"/cgi-bin/|/boaform/|/HNAP1", re.I)),
    ("Path traversal", "critical", re.compile(
        r"\\.\\./|%2e%2e|%252e|/etc/passwd|/proc/self", re.I)),
    ("SQL injection probe", "critical", re.compile(
        r"(?:union(?:%20|\s)+select|or(?:%20|\s)+1=1|sleep\(|benchmark\(|"
        r"information_schema|%27|')", re.I)),
    ("XSS probe", "high", re.compile(
        r"<script|%3cscript|javascript:|onerror=|onload=", re.I)),
    ("Backup/config probe", "medium", re.compile(
        r"\\.(?:sql|bak|old|swp|tar|tgz|gz|7z)(?:$|\\?)|"
        r"/(?:backup|dump|database)(?:[._/-]|$)", re.I)),
    ("Generic PHP probe", "low", re.compile(
        r"/(?:index|test|info|admin|login|file\\d+)\\.php(?:$|\\?)", re.I)),
)

SEVERITY_WEIGHT = {
    "low": 1,
    "medium": 2,
    "high": 4,
    "critical": 7,
}



@dataclass(frozen=True)
class Event:
    timestamp: datetime
    status: int
    method: str
    scheme: str
    host: str
    raw_path: str
    path: str
    ip: str
    ua: str
    referrer: str


@dataclass
class Session:
    first: datetime
    last: datetime
    ip: str
    ua: str
    host: str
    pages: list[str]


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        default="/etc/dashboard-voorbij/visitors.ini",
    )
    parser.add_argument("--date")
    return parser.parse_args()


def read_config(path: Path) -> dict[str, object]:
    parser = configparser.ConfigParser()
    if not path.is_file():
        raise FileNotFoundError(f"Configuratie ontbreekt: {path}")
    parser.read(path, encoding="utf-8")
    section = parser["collector"]
    own_ips = {
        value.strip()
        for value in section.get("own_ips", "").replace("\n", ",").split(",")
        if value.strip()
    }
    return {
        "log_glob": section.get(
            "log_glob",
            "/var/log/nginx-proxy-manager/proxy-host-*_access.log*",
        ),
        "public_output": Path(section.get(
            "public_output",
            "/var/lib/dashboard-voorbij/public/visitors.json",
        )),
        "private_output": Path(section.get(
            "private_output",
            "/var/lib/dashboard-voorbij/private/visitors-private.json",
        )),
        "timezone": section.get("timezone", "Europe/Amsterdam"),
        "session_minutes": section.getint("session_minutes", 30),
        "recent_visits": section.getint("recent_visits", 8),
        "recent_scans": section.getint("recent_scans", 8),
        "own_ips": own_ips,
        "geoip_db": Path(section.get(
            "geoip_db",
            "/var/lib/dashboard-voorbij/GeoLite2-Country.mmdb",
        )),
    }


def log_paths(pattern: str) -> list[Path]:
    import glob
    paths = [Path(value) for value in glob.glob(pattern)]
    paths = [path for path in paths if path.is_file()]
    return sorted(paths, key=lambda path: (path.stat().st_mtime, str(path)))


def lines_from(path: Path):
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8", errors="replace") as handle:
        yield from handle


def normalise_ip(value: str) -> str:
    try:
        address = ipaddress.ip_address(value.strip())
        if isinstance(address, ipaddress.IPv6Address) and address.ipv4_mapped:
            return str(address.ipv4_mapped)
        return str(address)
    except ValueError:
        return value.strip()


def parse_line(line: str) -> Event | None:
    match = LOG_RE.match(line.rstrip("\n"))
    if not match:
        return None
    data = match.groupdict()
    try:
        timestamp = datetime.strptime(
            data["timestamp"], "%d/%b/%Y:%H:%M:%S %z")
    except ValueError:
        return None
    split = urlsplit(data["path"])
    path = unquote(split.path or "/")
    path = "".join(char for char in path if char >= " " and char != "\x7f")
    if not path.startswith("/"):
        path = "/" + path
    return Event(
        timestamp=timestamp,
        status=int(data["status"]),
        method=data["method"],
        scheme=data["scheme"],
        host=data["host"],
        raw_path=data["path"],
        path=path[:500],
        ip=normalise_ip(data["ip"]),
        ua=data["ua"],
        referrer=data["referrer"],
    )


def masked_ip(value: str) -> str:
    try:
        address = ipaddress.ip_address(value)
    except ValueError:
        return "onbekend"
    if isinstance(address, ipaddress.IPv4Address):
        parts = value.split(".")
        return f"{parts[0]}.{parts[1]}.x.x"
    return ":".join(address.exploded.split(":")[:3]) + ":…"


def browser(ua: str) -> str:
    value = ua.lower()
    if "edg/" in value:
        return "Edge"
    if "opr/" in value or "opera" in value:
        return "Opera"
    if "firefox/" in value:
        return "Firefox"
    if "chrome/" in value or "chromium/" in value:
        return "Chrome"
    if "safari/" in value and "chrome/" not in value:
        return "Safari"
    if BOT_RE.search(ua):
        return "Bot"
    return "Andere browser"


def device(ua: str) -> str:
    value = ua.lower()
    if BOT_RE.search(ua):
        return "bot"
    if "ipad" in value or "tablet" in value:
        return "tablet"
    if "mobile" in value or "android" in value or "iphone" in value:
        return "mobiel"
    return "desktop"


def suspicious_details(path: str) -> tuple[str, str] | None:
    for label, severity, pattern in THREAT_PATTERNS:
        if pattern.search(path):
            return label, severity
    return None


def suspicious_label(path: str) -> str | None:
    details = suspicious_details(path)
    return details[0] if details else None


def background(path: str) -> bool:
    return any(path.startswith(prefix) for prefix in BACKGROUND_PREFIXES)


def static(path: str) -> bool:
    return Path(path.lower()).suffix in STATIC_EXTENSIONS


def bot(event: Event) -> bool:
    return bool(BOT_RE.search(event.ua))


def country_reader(path: Path):
    if not path.is_file():
        return None
    try:
        import geoip2.database  # type: ignore
        return geoip2.database.Reader(str(path))
    except (ImportError, OSError):
        return None


def country_for(ip: str, reader) -> tuple[str, str]:
    if reader is None:
        return "ZZ", "Onbekend"
    try:
        result = reader.country(ip)
        code = result.country.iso_code or "ZZ"
        name = result.country.names.get("nl") or result.country.name or "Onbekend"
        return code, name
    except Exception:
        return "ZZ", "Onbekend"


def flag_for(code: str) -> str:
    code = code.upper()
    if len(code) != 2 or not code.isalpha() or code == "ZZ":
        return "🌍"
    return "".join(chr(127397 + ord(char)) for char in code)


def page_candidate(event: Event) -> bool:
    return (
        event.method == "GET"
        and event.status < 400
        and not background(event.path)
        and not static(event.path)
        and not event.path.startswith("/api/")
        and suspicious_label(event.path) is None
        and not bot(event)
    )


def make_sessions(events: list[Event], minutes: int) -> list[Session]:
    timeout = timedelta(minutes=minutes)
    active: dict[tuple[str, str], Session] = {}
    complete: list[Session] = []
    for event in sorted(events, key=lambda item: item.timestamp):
        key = (event.host, event.ip, event.ua)
        session = active.get(key)
        if session is None or event.timestamp - session.last > timeout:
            if session is not None:
                complete.append(session)
            active[key] = Session(
                first=event.timestamp,
                last=event.timestamp,
                ip=event.ip,
                ua=event.ua,
                host=event.host,
                pages=[event.path],
            )
        else:
            session.last = event.timestamp
            if session.pages[-1] != event.path:
                session.pages.append(event.path)
    complete.extend(active.values())
    return sorted(complete, key=lambda item: item.last)


def atomic_json(path: Path, value: object, mode: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temp_name = tempfile.mkstemp(
        prefix=f".{path.name}.", dir=str(path.parent))
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temp_name, mode)
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def public_session(session: Session, timezone: ZoneInfo) -> dict[str, object]:
    pages = session.pages[-5:]
    return {
        "time": session.last.astimezone(timezone).strftime("%H:%M"),
        "first_time": session.first.astimezone(timezone).strftime("%H:%M"),
        "masked_ip": masked_ip(session.ip),
        "host": session.host,
        "device": device(session.ua),
        "browser": browser(session.ua),
        "last_page": pages[-1] if pages else "/",
        "pages": pages,
        "page_count": len(session.pages),
    }


def main() -> int:
    args = arguments()
    config = read_config(Path(args.config))
    timezone = ZoneInfo(str(config["timezone"]))
    target_date = (
        datetime.strptime(args.date, "%Y-%m-%d").date()
        if args.date else datetime.now(timezone).date()
    )

    paths = log_paths(str(config["log_glob"]))
    if not paths:
        raise FileNotFoundError(
            f"Geen logs gevonden voor {config['log_glob']}")

    events: list[Event] = []
    seen: set[tuple[object, ...]] = set()
    unparsed = 0

    for path in paths:
        for line in lines_from(path):
            event = parse_line(line)
            if event is None:
                if line.strip():
                    unparsed += 1
                continue
            if event.timestamp.astimezone(timezone).date() != target_date:
                continue
            key = (
                event.timestamp, event.ip, event.method,
                event.raw_path, event.status, event.ua,
            )
            if key in seen:
                continue
            seen.add(key)
            events.append(event)

    events.sort(key=lambda item: item.timestamp)
    own_ips = set(config["own_ips"])

    scans: list[tuple[Event, str, str]] = []
    bot_ips: set[str] = set()
    scan_ips: set[str] = set()

    for event in events:
        details = suspicious_details(event.path)
        if details:
            label, severity = details
            scans.append((event, label, severity))
            scan_ips.add(event.ip)
        if bot(event):
            bot_ips.add(event.ip)

    # Een IP dat dezelfde dag een aanvalspatroon probeert, wordt niet als
    # menselijke bezoeker meegeteld. Dit voorkomt sessies als /file11.php.
    non_human_ips = bot_ips | scan_ips
    sessions = make_sessions(
        [
            event for event in events
            if page_candidate(event) and event.ip not in non_human_ips
        ],
        int(config["session_minutes"]),
    )
    own_sessions = [session for session in sessions if session.ip in own_ips]
    external_sessions = [
        session for session in sessions if session.ip not in own_ips]

    top_pages = Counter()
    for session in external_sessions:
        for page in session.pages:
            top_pages[page] += 1

    blocked_statuses = {401, 403, 404, 410, 444}

    site_sessions = Counter(session.host for session in external_sessions)
    site_unique_ips: dict[str, set[str]] = {}
    site_last_visit: dict[str, datetime] = {}
    for session in external_sessions:
        site_unique_ips.setdefault(session.host, set()).add(session.ip)
        current = site_last_visit.get(session.host)
        if current is None or session.last > current:
            site_last_visit[session.host] = session.last

    # Hosts worden automatisch uit de aangetroffen logs ontdekt.
    known_hosts = sorted(
        set(site_sessions)
        | set(site_unique_ips)
        | set(site_last_visit)
    )

    geo_reader = country_reader(Path(config["geoip_db"]))
    country_cache: dict[str, tuple[str, str]] = {}

    def geo(ip: str) -> tuple[str, str]:
        if ip not in country_cache:
            country_cache[ip] = country_for(ip, geo_reader)
        return country_cache[ip]

    attack_types = Counter(label for _, label, _ in scans)
    severities = Counter(severity for _, _, severity in scans)
    attack_targets = Counter(event.host for event, _, _ in scans)
    attack_paths = Counter(event.path for event, _, _ in scans)
    attacker_requests = Counter(event.ip for event, _, _ in scans)
    attacker_categories: dict[str, Counter[str]] = defaultdict(Counter)
    attacker_targets: dict[str, Counter[str]] = defaultdict(Counter)
    attacker_last: dict[str, datetime] = {}
    countries = Counter()

    for event, label, _severity in scans:
        attacker_categories[event.ip][label] += 1
        attacker_targets[event.ip][event.host] += 1
        attacker_last[event.ip] = max(
            event.timestamp, attacker_last.get(event.ip, event.timestamp))
        code, name = geo(event.ip)
        countries[(code, name)] += 1

    suspicious_success = sum(
        1 for event, _, _ in scans if 200 <= event.status < 400)
    blocked_suspicious = sum(
        1 for event, _, _ in scans if event.status in blocked_statuses)
    unique_attackers = len(scan_ips - own_ips)
    severity_points = sum(
        SEVERITY_WEIGHT.get(severity, 1) for _, _, severity in scans)

    threat_score = min(100, round(
        min(len(scans) / 8, 25)
        + min(unique_attackers * 2.2, 22)
        + min(severity_points / 6, 33)
        + min(suspicious_success * 1.5, 12)
        + min(sum(1 for event in events if event.status >= 500) / 25, 8)
    ))

    if threat_score < 25:
        threat_level = "LOW"
        threat_state = "low"
    elif threat_score < 50:
        threat_level = "GUARDED"
        threat_state = "guarded"
    elif threat_score < 75:
        threat_level = "ELEVATED"
        threat_state = "elevated"
    else:
        threat_level = "HIGH"
        threat_state = "high"

    generated = datetime.now(timezone)
    recent_visits = int(config["recent_visits"])
    recent_scans = int(config["recent_scans"])

    public = {
        "schema_version": 6.1,
        "generated_at": generated.isoformat(timespec="seconds"),
        "generated_time": generated.strftime("%H:%M"),
        "date": target_date.isoformat(),
        "session_minutes": int(config["session_minutes"]),
        "summary": {
            "requests_total": len(events),
            "external_sessions": len(external_sessions),
            "own_sessions": len(own_sessions),
            "unique_external_ips": len(
                {session.ip for session in external_sessions}),
            "bots_scanners_unique": len((bot_ips | scan_ips) - own_ips),
            "suspicious_requests": len(scans),
            "blocked_suspicious_requests": sum(
                1 for event, _, _ in scans if event.status in blocked_statuses),
            "background_requests": sum(
                1 for event in events if background(event.path)),
            "static_requests": sum(
                1 for event in events if static(event.path)),
            "api_requests": sum(
                1 for event in events
                if event.path.startswith("/api/")
                and not background(event.path)),
            "http_4xx": sum(
                1 for event in events if 400 <= event.status < 500),
            "http_5xx": sum(
                1 for event in events if event.status >= 500),
        },
        "sites": [
            {
                "host": host,
                "sessions": site_sessions.get(host, 0),
                "unique_ips": len(site_unique_ips.get(host, set())),
                "last_visit": (
                    site_last_visit[host].astimezone(timezone).strftime("%H:%M")
                    if host in site_last_visit else None
                ),
            }
            for host in known_hosts
        ],
        "security": {
            "score": threat_score,
            "level": threat_level,
            "state": threat_state,
            "explanation": (
                "Activiteitsscore van inkomende probes; dit is geen bewijs "
                "van een succesvolle inbraak."
            ),
            "geoip_enabled": geo_reader is not None,
            "unique_attackers": unique_attackers,
            "suspicious_requests": len(scans),
            "blocked_requests": blocked_suspicious,
            "successful_responses": suspicious_success,
            "severity_counts": dict(severities),
            "attack_types": [
                {"name": name, "count": count}
                for name, count in attack_types.most_common(8)
            ],
            "target_sites": [
                {"host": host, "count": count}
                for host, count in attack_targets.most_common(8)
            ],
            "countries": [
                {
                    "code": code,
                    "name": name,
                    "flag": flag_for(code),
                    "count": count,
                }
                for (code, name), count in countries.most_common(8)
            ],
            "top_paths": [
                {"path": path, "count": count}
                for path, count in attack_paths.most_common(8)
            ],
            "top_attackers": [
                {
                    "masked_ip": masked_ip(ip),
                    "country_code": geo(ip)[0],
                    "country": geo(ip)[1],
                    "flag": flag_for(geo(ip)[0]),
                    "requests": count,
                    "categories": [
                        name for name, _ in attacker_categories[ip].most_common(3)
                    ],
                    "targets": [
                        host for host, _ in attacker_targets[ip].most_common(3)
                    ],
                    "last_seen": attacker_last[ip].astimezone(timezone).strftime("%H:%M"),
                }
                for ip, count in attacker_requests.most_common(8)
                if ip not in own_ips
            ],
            "recent_events": [
                {
                    "time": event.timestamp.astimezone(timezone).strftime("%H:%M"),
                    "masked_ip": masked_ip(event.ip),
                    "country": geo(event.ip)[1],
                    "flag": flag_for(geo(event.ip)[0]),
                    "category": label,
                    "severity": severity,
                    "host": event.host,
                    "path": event.path[:120],
                    "status": event.status,
                    "blocked": event.status in blocked_statuses,
                }
                for event, label, severity in reversed(scans[-15:])
                if event.ip not in own_ips
            ],
        },
        "latest_external_visit": (
            public_session(external_sessions[-1], timezone)
            if external_sessions else None
        ),
        "recent_external_visits": [
            public_session(session, timezone)
            for session in reversed(external_sessions[-recent_visits:])
        ],
        "recent_scans": [
            {
                "time": event.timestamp.astimezone(timezone).strftime("%H:%M"),
                "masked_ip": masked_ip(event.ip),
                "category": label,
                "status": event.status,
                "blocked": event.status in blocked_statuses,
            }
            for event, label, _ in reversed(scans[-recent_scans:])
        ],
        "top_pages": [
            {"path": path, "sessions": count}
            for path, count in top_pages.most_common(5)
        ],
        "note": (
            "IP-adressen zijn gemaskeerd; achtergrondverzoeken tellen "
            "niet als bezoek."
        ),
    }

    private = {
        "schema_version": 6.1,
        "generated_at": generated.isoformat(timespec="seconds"),
        "date": target_date.isoformat(),
        "source_files": [str(path) for path in paths],
        "unparsed_lines": unparsed,
        "own_ips": sorted(own_ips),
        "external_sessions": [
            {
                "first": session.first.isoformat(),
                "last": session.last.isoformat(),
                "ip": session.ip,
                "host": session.host,
                "ua": session.ua,
                "pages": session.pages,
            }
            for session in external_sessions[-50:]
        ],
        "recent_scans": [
            {
                "timestamp": event.timestamp.isoformat(),
                "ip": event.ip,
                "path": event.path,
                "status": event.status,
                "category": label,
                "severity": severity,
                "ua": event.ua,
            }
            for event, label, severity in scans[-100:]
        ],
    }

    atomic_json(Path(config["public_output"]), public, 0o644)
    atomic_json(Path(config["private_output"]), private, 0o600)

    summary = public["summary"]
    print(
        f"{target_date}: {summary['external_sessions']} externe sessies, "
        f"{summary['bots_scanners_unique']} bots/scanners, "
        f"{summary['suspicious_requests']} verdachte verzoeken, threat={threat_level} {threat_score}/100; "
        f"publicatie={config['public_output']}"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, configparser.Error) as error:
        import sys
        print(f"FOUT: {error}", file=sys.stderr)
        raise SystemExit(1)
