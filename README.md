# SC Downloader

SoundCloud helper: **desktop** (Python + Tkinter) and **web** (Next.js for Vercel).

## Deploy the web app to Vercel (from GitHub)

1. Push this repository to GitHub (if it is not already):

   ```bash
   git add .
   git commit -m "Add Vercel web app"
   git push -u origin master
   ```

   (This repo uses branch **`master`**.)

2. In [Vercel](https://vercel.com): **Add New Project** → import your GitHub repo.

3. **Critical setting — Root Directory:** set to `web` (not the repository root).  
   Framework Preset should detect **Next.js**.

4. Leave default **Build Command** (`next build`) and **Output** as Vercel suggests.

5. Save → Vercel will build and assign a URL like `https://your-project.vercel.app`.  
   In **Project → Settings → Git**, set **Production Branch** to **`master`** if it is not already.  
   Every push to **`master`** triggers a production deployment.

### Vercel + `python3` error

If you see **`env: 'python3': No such file or directory`**, the app was using the wrong yt-dlp asset. This repo sets **`YOUTUBE_DL_FILENAME=yt-dlp_linux`** and **`YOUTUBE_DL_SKIP_PYTHON_CHECK=1`** in `web/vercel.json` so the **standalone** Linux binary is installed (no Python on Vercel). Redeploy after pulling the latest `master`. If you created the project before that change, add the same two variables under **Project → Settings → Environment Variables** (all environments), then **Redeploy**.

### Limits (important)

- **Hobby** serverless functions time out after **10 seconds**. The first resolve may be slow while `yt-dlp` is prepared; if it times out, try again or upgrade Vercel / use the **desktop** app for heavy use.
- The web UI resolves a **direct stream URL** for saving in the browser. **WAV / FLAC transcoding** (ffmpeg) is not offered on Vercel here; use the **desktop** build for that.

## Desktop app

- Run: `python soundcloud_downloader.py` (requires Python, `yt-dlp`, `ffmpeg`).
- Windows EXE: run `.\build.ps1` (see `vendor\README.txt` for bundling `ffmpeg.exe`).

## Local web dev

```bash
cd web
npm install
npm run dev
```

Open `http://localhost:3000`.

## CI

GitHub Actions runs `npm ci` and `npm run build` in `web/` on pushes and pull requests targeting **`master`**.
