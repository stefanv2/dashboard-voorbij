import express from "express";
import crypto from "crypto";

const app = express();

const PORT = process.env.PORT || 3000;

const NAVIDROME_URL = (process.env.NAVIDROME_URL || "").replace(/\/$/, "");
const NAVIDROME_USER = process.env.NAVIDROME_USER || "";
const NAVIDROME_PASSWORD = process.env.NAVIDROME_PASSWORD || "";

if (!NAVIDROME_URL || !NAVIDROME_USER || !NAVIDROME_PASSWORD) {
  console.error("Missing required environment variables:");
  console.error("NAVIDROME_URL, NAVIDROME_USER, NAVIDROME_PASSWORD");
  process.exit(1);
}

function buildAuthParams(extra = {}, includeJson = true) {
  const salt = crypto.randomBytes(6).toString("hex");
  const token = crypto
    .createHash("md5")
    .update(`${NAVIDROME_PASSWORD}${salt}`)
    .digest("hex");

  const params = new URLSearchParams();

  params.set("u", NAVIDROME_USER);
  params.set("t", token);
  params.set("s", salt);
  params.set("v", "1.16.1");
  params.set("c", "dashboard-voorbij");

  if (includeJson) {
    params.set("f", "json");
  }

  for (const [key, value] of Object.entries(extra)) {
    if (value !== undefined && value !== null) {
      params.set(key, String(value));
    }
  }

  return params;
}

function subsonicUrl(endpoint, extra = {}, includeJson = true) {
  const params = buildAuthParams(extra, includeJson);
  return `${NAVIDROME_URL}/rest/${endpoint}.view?${params.toString()}`;
}

async function fetchSubsonicJson(endpoint, extra = {}) {
  const url = subsonicUrl(endpoint, extra, true);

  const response = await fetch(url);

  if (!response.ok) {
    throw new Error(`Navidrome HTTP error: ${response.status}`);
  }

  const data = await response.json();
  const subsonic = data["subsonic-response"];

  if (!subsonic) {
    throw new Error("Invalid Navidrome response");
  }

  if (subsonic.status !== "ok") {
    const message = subsonic.error?.message || "Unknown Navidrome error";
    throw new Error(message);
  }

  return subsonic;
}

function formatDuration(seconds) {
  if (!seconds || Number.isNaN(Number(seconds))) {
    return "";
  }

  const total = Number(seconds);
  const minutes = Math.floor(total / 60);
  const rest = total % 60;

  return `${minutes}:${String(rest).padStart(2, "0")}`;
}

function albumLink(albumId) {
  if (!albumId) {
    return NAVIDROME_URL;
  }

  return `${NAVIDROME_URL}/#/album/${encodeURIComponent(albumId)}/show`;
}

function normalizeSong(song) {
  return {
    type: "song",
    id: song.id,
    title: song.title || "Onbekende titel",
    artist: song.artist || song.displayArtist || "Onbekende artiest",
    album: song.album || "",
    duration: formatDuration(song.duration),
    cover: song.coverArt
      ? `/api/music/cover/${encodeURIComponent(song.coverArt)}`
      : "/img/no-cover.png",
    link: albumLink(song.albumId)
  };
}

function normalizeAlbum(album) {
  return {
    type: "album",
    id: album.id,
    title: album.name || album.title || "Onbekend album",
    artist: album.artist || album.displayArtist || "Onbekende artiest",
    album: "Album",
    duration: album.songCount ? `${album.songCount} nummers` : "",
    cover: album.coverArt
      ? `/api/music/cover/${encodeURIComponent(album.coverArt)}`
      : "/img/no-cover.png",
    link: albumLink(album.id)
  };
}

app.get("/health", (req, res) => {
  res.json({
    status: "ok",
    service: "dashboard-api"
  });
});

app.get("/api/music", async (req, res) => {
  try {
    const query = String(req.query.query || "favorites").trim();

    let items = [];

    if (query === "favorites") {
      const data = await fetchSubsonicJson("getStarred2");
      const starred = data.starred2 || {};

      const albums = Array.isArray(starred.album) ? starred.album : [];
      const songs = Array.isArray(starred.song) ? starred.song : [];

      items = [
        ...albums.map(normalizeAlbum),
        ...songs.map(normalizeSong)
      ];
    } else if (query === "random") {
      const data = await fetchSubsonicJson("getRandomSongs", {
        size: 8
      });

      const songs = data.randomSongs?.song || [];
      items = songs.map(normalizeSong);
    } else {
      const data = await fetchSubsonicJson("search3", {
        query,
        songCount: 8,
        albumCount: 4,
        artistCount: 0
      });

      const result = data.searchResult3 || {};
      const songs = Array.isArray(result.song) ? result.song : [];
      const albums = Array.isArray(result.album) ? result.album : [];

      items = [
        ...songs.map(normalizeSong),
        ...albums.map(normalizeAlbum)
      ];
    }

    res.json(items.slice(0, 8));
  } catch (error) {
    console.error("Music API error:", error.message);

    res.status(500).json({
      error: "Music API failed",
      message: error.message
    });
  }
});

app.get("/api/music/cover/:coverId", async (req, res) => {
  try {
    const coverId = req.params.coverId;

    const url = subsonicUrl(
      "getCoverArt",
      {
        id: coverId
      },
      false
    );

    const response = await fetch(url);

    if (!response.ok) {
      throw new Error(`Cover HTTP error: ${response.status}`);
    }

    const contentType = response.headers.get("content-type") || "image/jpeg";
    const buffer = Buffer.from(await response.arrayBuffer());

    res.setHeader("Content-Type", contentType);
    res.setHeader("Cache-Control", "public, max-age=86400");

    res.send(buffer);
  } catch (error) {
    console.error("Cover API error:", error.message);
    res.status(404).send("Cover not found");
  }
});

app.listen(PORT, "0.0.0.0", () => {
  console.log(`dashboard-api listening on port ${PORT}`);
});
