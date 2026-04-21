import { NextRequest, NextResponse } from "next/server";
import youtubedl from "youtube-dl-exec";
import { isValidSoundcloudInput, normalizeSoundcloudUrl } from "@/lib/normalize-sc-url";

export const runtime = "nodejs";

type YtdlpJson = {
  title?: string;
  ext?: string;
  url?: string;
  vcodec?: string;
  acodec?: string;
  requested_formats?: Array<{ url?: string; ext?: string }>;
  formats?: Array<{ format_id?: string; url?: string; ext?: string; acodec?: string }>;
};

function pickStreamUrl(data: YtdlpJson): { url: string; ext: string } | null {
  if (data.url && typeof data.url === "string" && data.url.startsWith("http")) {
    return { url: data.url, ext: data.ext || "audio" };
  }
  const rf = data.requested_formats?.[0];
  if (rf?.url) return { url: rf.url, ext: rf.ext || "audio" };
  const fmts = data.formats || [];
  const withUrl = fmts.filter((f) => f.url && f.url.startsWith("http"));
  const audio = withUrl.filter((f) => f.acodec && f.acodec !== "none").pop();
  if (audio?.url) return { url: audio.url, ext: audio.ext || "audio" };
  const last = withUrl.pop();
  if (last?.url) return { url: last.url, ext: last.ext || "audio" };
  return null;
}

export async function POST(req: NextRequest) {
  let body: { url?: string };
  try {
    body = await req.json();
  } catch {
    return NextResponse.json({ error: "Invalid JSON body" }, { status: 400 });
  }

  const raw = (body.url || "").trim();
  const url = normalizeSoundcloudUrl(raw);
  if (!url || !isValidSoundcloudInput(url)) {
    return NextResponse.json(
      { error: "Paste a full soundcloud.com link or an app id ending with ::…:TRACK_ID" },
      { status: 400 },
    );
  }

  try {
    const data = (await youtubedl(url, {
      dumpSingleJson: true,
      noWarnings: true,
      quiet: true,
      skipDownload: true,
      noPlaylist: true,
      format: "bestaudio/best",
    })) as YtdlpJson;
    const picked = pickStreamUrl(data);
    if (!picked) {
      return NextResponse.json(
        { error: "Could not resolve a direct stream URL. Try the desktop app for this track." },
        { status: 422 },
      );
    }

    const safeTitle = (data.title || "soundcloud-track").replace(/[/\\?%*:|"<>]/g, "-").slice(0, 120);
    return NextResponse.json({
      title: data.title || "Track",
      streamUrl: picked.url,
      ext: picked.ext,
      suggestedFilename: `${safeTitle}.${picked.ext}`,
    });
  } catch (e) {
    const msg = e instanceof Error ? e.message : String(e);
    return NextResponse.json({ error: msg }, { status: 502 });
  }
}
