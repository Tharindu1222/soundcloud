/** Match desktop soundcloud_downloader.py URL rules. */
export function normalizeSoundcloudUrl(raw: string): string {
  const s = (raw || "").trim();
  if (!s) return "";
  const low = s.toLowerCase();
  if (low.includes("soundcloud.com")) {
    if (!s.startsWith("http://") && !s.startsWith("https://")) {
      return `https://${s.replace(/^\/+/, "")}`;
    }
    return s;
  }
  if (s.includes("::")) {
    const tail = s.split(":").pop()?.trim() ?? "";
    if (/^\d+$/.test(tail)) {
      return `https://api.soundcloud.com/tracks/${tail}`;
    }
  }
  return s;
}

export function isValidSoundcloudInput(url: string): boolean {
  if (!url) return false;
  return url.toLowerCase().includes("soundcloud.com");
}
