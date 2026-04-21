"use client";

import { useState } from "react";

type ResolveOk = {
  title: string;
  streamUrl: string;
  ext: string;
  suggestedFilename: string;
};

export default function HomePage() {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ResolveOk | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setResult(null);
    setLoading(true);
    try {
      const res = await fetch("/api/resolve", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: url.trim() }),
      });
      const data = await res.json();
      if (!res.ok) {
        setError(data.error || res.statusText);
        return;
      }
      setResult(data as ResolveOk);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Request failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main>
      <h1>
        <span className="sc">SC</span> Downloader
      </h1>
      <p className="sub">Web · resolve stream link (same rules as desktop app)</p>

      <form className="card" onSubmit={onSubmit}>
        <label htmlFor="url">SOUNDCLOUD URL</label>
        <input
          id="url"
          name="url"
          type="text"
          placeholder="https://soundcloud.com/artist/track"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          autoComplete="off"
        />
        <button className="primary" type="submit" disabled={loading}>
          {loading ? "Resolving…" : "Resolve download link"}
        </button>
      </form>

      {error && (
        <div className="result err" role="alert">
          {error}
        </div>
      )}

      {result && (
        <div className="result ok">
          <strong>{result.title}</strong>
          <p style={{ margin: "0.75rem 0" }}>
            <a href={result.streamUrl} download={result.suggestedFilename} rel="noopener noreferrer">
              Open / save audio ({result.ext})
            </a>
          </p>
          <p className="note" style={{ margin: 0 }}>
            If the browser only plays the file, use right-click → Save as, or use the desktop app for WAV/FLAC
            conversion.
          </p>
        </div>
      )}

      <p className="note">
        Deploy: connect this GitHub repo to Vercel and set the project <strong>Root Directory</strong> to{" "}
        <code>web</code>. Each push to the default branch triggers a production deploy.
      </p>
    </main>
  );
}
