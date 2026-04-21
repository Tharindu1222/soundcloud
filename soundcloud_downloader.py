import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import subprocess
import sys
import os
import shutil


def _bundle_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

BG = "#0f0f0f"
SURFACE = "#1a1a1a"
CARD = "#222222"
ACCENT = "#ff5500"
ACCENT2 = "#ff7733"
TEXT = "#f0f0f0"
MUTED = "#888888"
SUCCESS = "#22c55e"
ERROR = "#ef4444"
BORDER = "#2e2e2e"

class SoundCloudDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("SC Downloader")
        self.root.geometry("620x560")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)

        self.output_dir = os.path.join(os.path.expanduser("~"), "Music", "SoundCloud")
        self.is_downloading = False

        self._build_ui()
        self._check_dependencies()

    def _build_ui(self):
        # Top bar
        topbar = tk.Frame(self.root, bg=ACCENT, height=3)
        topbar.pack(fill="x")

        # Header
        header = tk.Frame(self.root, bg=BG, pady=28)
        header.pack(fill="x", padx=32)

        title_frame = tk.Frame(header, bg=BG)
        title_frame.pack(side="left")

        tk.Label(title_frame, text="SC", font=("Courier New", 28, "bold"),
                 bg=BG, fg=ACCENT).pack(side="left")
        tk.Label(title_frame, text=" Downloader", font=("Courier New", 22),
                 bg=BG, fg=TEXT).pack(side="left", pady=4)

        tk.Label(header, text="WAV · LOSSLESS",
                 font=("Courier New", 9), bg=BG, fg=MUTED).pack(side="right", pady=8)

        # Divider
        tk.Frame(self.root, bg=BORDER, height=1).pack(fill="x", padx=32)

        # Main card
        card = tk.Frame(self.root, bg=CARD, padx=28, pady=28)
        card.pack(fill="x", padx=32, pady=20)

        # URL input label
        tk.Label(card, text="SOUNDCLOUD URL", font=("Courier New", 9, "bold"),
                 bg=CARD, fg=MUTED).pack(anchor="w", pady=(0, 8))

        # URL input frame
        url_frame = tk.Frame(card, bg=BORDER, pady=1, padx=1)
        url_frame.pack(fill="x")

        url_inner = tk.Frame(url_frame, bg=SURFACE)
        url_inner.pack(fill="x")

        self.url_var = tk.StringVar()
        self.url_entry = tk.Entry(url_inner, textvariable=self.url_var,
                                  font=("Courier New", 11), bg=SURFACE, fg=TEXT,
                                  insertbackground=ACCENT, relief="flat",
                                  bd=0)
        self.url_entry.pack(fill="x", padx=14, pady=12)
        self.url_entry.insert(0, "https://soundcloud.com/artist/track")
        self.url_entry.bind("<FocusIn>", self._clear_placeholder)
        self.url_entry.bind("<FocusOut>", self._restore_placeholder)
        self.url_entry.config(fg=MUTED)

        # Format + Quality row
        opt_frame = tk.Frame(card, bg=CARD)
        opt_frame.pack(fill="x", pady=(16, 0))

        # Format
        fmt_col = tk.Frame(opt_frame, bg=CARD)
        fmt_col.pack(side="left", expand=True, fill="x")
        tk.Label(fmt_col, text="FORMAT", font=("Courier New", 9, "bold"),
                 bg=CARD, fg=MUTED).pack(anchor="w", pady=(0, 6))
        self.format_var = tk.StringVar(value="wav")
        for fmt in ["wav", "mp3", "flac", "m4a"]:
            rb = tk.Radiobutton(fmt_col, text=fmt.upper(), variable=self.format_var,
                                value=fmt, font=("Courier New", 10),
                                bg=CARD, fg=TEXT, selectcolor=CARD,
                                activebackground=CARD, activeforeground=ACCENT,
                                indicatoron=0, relief="flat", bd=0,
                                command=lambda f=fmt: self._select_format(f))
            rb.pack(side="left", padx=(0, 12))

        # Quality
        qual_col = tk.Frame(opt_frame, bg=CARD)
        qual_col.pack(side="right")
        tk.Label(qual_col, text="QUALITY", font=("Courier New", 9, "bold"),
                 bg=CARD, fg=MUTED).pack(anchor="w", pady=(0, 6))
        self.quality_var = tk.StringVar(value="0 (best)")
        qual_menu = ttk.Combobox(qual_col, textvariable=self.quality_var,
                                  values=["0 (best)", "1", "2", "3 (smaller)"],
                                  font=("Courier New", 10), width=14, state="readonly")
        qual_menu.pack()

        # Output folder
        tk.Label(card, text="SAVE TO", font=("Courier New", 9, "bold"),
                 bg=CARD, fg=MUTED).pack(anchor="w", pady=(16, 6))

        dir_frame = tk.Frame(card, bg=SURFACE)
        dir_frame.pack(fill="x")

        self.dir_label = tk.Label(dir_frame, text=self.output_dir,
                                   font=("Courier New", 9), bg=SURFACE, fg=MUTED,
                                   anchor="w", padx=12, pady=10)
        self.dir_label.pack(side="left", fill="x", expand=True)

        browse_btn = tk.Button(dir_frame, text="BROWSE",
                               font=("Courier New", 9, "bold"),
                               bg=ACCENT, fg="white", relief="flat", bd=0,
                               padx=14, pady=10, cursor="hand2",
                               command=self._browse_dir,
                               activebackground=ACCENT2, activeforeground="white")
        browse_btn.pack(side="right")

        # Download button
        self.dl_btn = tk.Button(self.root, text="⬇  DOWNLOAD WAV",
                                font=("Courier New", 13, "bold"),
                                bg=ACCENT, fg="white", relief="flat", bd=0,
                                pady=16, cursor="hand2",
                                command=self._start_download,
                                activebackground=ACCENT2, activeforeground="white")
        self.dl_btn.pack(fill="x", padx=32)

        # Progress bar
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Custom.Horizontal.TProgressbar",
                        troughcolor=SURFACE, background=ACCENT,
                        lightcolor=ACCENT, darkcolor=ACCENT,
                        borderwidth=0, thickness=4)

        self.progress = ttk.Progressbar(self.root, style="Custom.Horizontal.TProgressbar",
                                         mode="indeterminate")
        self.progress.pack(fill="x", padx=32, pady=(8, 0))

        # Status log
        log_frame = tk.Frame(self.root, bg=SURFACE, padx=14, pady=10)
        log_frame.pack(fill="both", expand=True, padx=32, pady=(10, 24))

        self.log_text = tk.Text(log_frame, font=("Courier New", 9),
                                bg=SURFACE, fg=MUTED, relief="flat",
                                bd=0, state="disabled", wrap="word",
                                insertbackground=ACCENT, height=5)
        self.log_text.pack(fill="both", expand=True)

        scrollbar = tk.Scrollbar(log_frame, command=self.log_text.yview,
                                  bg=SURFACE, troughcolor=SURFACE, relief="flat")
        self.log_text.configure(yscrollcommand=scrollbar.set)

        self._log("Ready. Paste a SoundCloud URL and click Download.", MUTED)

        # Format button references for highlight
        self._format_buttons = {}
        for widget in fmt_col.winfo_children():
            if isinstance(widget, tk.Radiobutton):
                self._format_buttons[widget.cget("text").lower()] = widget
        self._select_format("wav")

    def _select_format(self, fmt):
        if getattr(self, "dl_btn", None) and not self.is_downloading:
            self.dl_btn.config(text=f"⬇  DOWNLOAD {fmt.upper()}")

    def _clear_placeholder(self, e):
        if self.url_entry.cget("fg") == MUTED:
            self.url_entry.delete(0, "end")
            self.url_entry.config(fg=TEXT)

    def _restore_placeholder(self, e):
        if not self.url_var.get():
            self.url_entry.insert(0, "https://soundcloud.com/artist/track")
            self.url_entry.config(fg=MUTED)

    def _browse_dir(self):
        d = filedialog.askdirectory(initialdir=self.output_dir)
        if d:
            self.output_dir = d
            self.dir_label.config(text=d)

    def _log(self, msg, color=TEXT):
        self.log_text.config(state="normal")
        self.log_text.tag_configure(color, foreground=color)
        self.log_text.insert("end", f"› {msg}\n", color)
        self.log_text.see("end")
        self.log_text.config(state="disabled")

    def _try_import_ytdlp(self):
        try:
            import yt_dlp  # noqa: E402 — bundled in EXE; optional when running from source

            return yt_dlp
        except ImportError:
            return None

    def _yt_dlp_prefix(self):
        """CLI fallback: ['yt-dlp'] or [python, '-m', 'yt_dlp'], or None. Not used when frozen."""
        if getattr(sys, "frozen", False):
            return None
        if shutil.which("yt-dlp"):
            return ["yt-dlp"]
        try:
            proc = subprocess.run(
                [sys.executable, "-m", "yt_dlp", "--version"],
                capture_output=True,
                text=True,
                timeout=20,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
            )
            if proc.returncode == 0:
                return [sys.executable, "-m", "yt_dlp"]
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        return None

    def _local_ffmpeg(self):
        base = _bundle_dir()
        for name in ("ffmpeg.exe", "ffmpeg"):
            p = os.path.join(base, name)
            if os.path.isfile(p):
                return p
        return None

    def _ffmpeg_path(self):
        local = self._local_ffmpeg()
        if local:
            return local
        return shutil.which("ffmpeg")

    class _YtdlpLogger:
        __slots__ = ("_app",)

        def __init__(self, app):
            self._app = app

        def debug(self, msg):
            pass

        def info(self, msg):
            self._app.root.after(0, lambda m=str(msg): self._app._log(m.strip(), MUTED))

        def warning(self, msg):
            self._app.root.after(0, lambda m=str(msg): self._app._log(m.strip(), ERROR))

        def error(self, msg):
            self._app.root.after(0, lambda m=str(msg): self._app._log(m.strip(), ERROR))

    def _normalize_soundcloud_url(self, raw):
        """Accept browser URLs, api links, and app-style '...::user:TRACK_ID' pastes."""
        raw = (raw or "").strip()
        if not raw:
            return ""
        low = raw.lower()
        if "soundcloud.com" in low:
            if not raw.startswith(("http://", "https://")):
                return "https://" + raw.lstrip("/")
            return raw
        # e.g. "playlist-tracks::artist-USERID:2110518087" from some clients
        if "::" in raw:
            tail = raw.rsplit(":", 1)[-1].strip()
            if tail.isdigit():
                return f"https://api.soundcloud.com/tracks/{tail}"
        return raw

    def _is_valid_soundcloud_input(self, url):
        if not url:
            return False
        low = url.lower()
        return "soundcloud.com" in low

    def _check_dependencies(self):
        missing = []
        if self._try_import_ytdlp() is None and not self._yt_dlp_prefix():
            missing.append("yt-dlp (pip install yt-dlp)")
        if not self._ffmpeg_path():
            missing.append("ffmpeg (PATH හෝ app folder එකේ ffmpeg.exe)")
        if missing:
            self._log(f"Missing: {', '.join(missing)} — install them first!", ERROR)
        else:
            self._log("yt-dlp + ffmpeg OK. Ready to download.", SUCCESS)

    def _start_download(self):
        if self.is_downloading:
            return

        url = self._normalize_soundcloud_url(self.url_var.get())
        if not url or url == "https://soundcloud.com/artist/track":
            messagebox.showwarning("URL නැහැ", "SoundCloud link එකක් paste කරන්න.")
            return

        if not self._is_valid_soundcloud_input(url):
            messagebox.showwarning(
                "Invalid URL",
                "https://soundcloud.com/... browser address bar එකෙන් copy කරන්න,\n"
                "හෝ app එකෙන් internal ID එකක් නම් (අවසානයේ අංකය) එය paste කරන්න.",
            )
            return

        if self._try_import_ytdlp() is None and not self._yt_dlp_prefix():
            messagebox.showerror("yt-dlp", "yt-dlp සොයාගත නැහැ.\nPowerShell: pip install yt-dlp")
            return

        if not self._ffmpeg_path():
            messagebox.showerror(
                "ffmpeg",
                "ffmpeg සොයාගත නැහැ.\n"
                "Windows: ffmpeg.exe එක EXE එක තියෙන folder එකට දාන්න හෝ PATH එකට දාන්න.",
            )
            return

        os.makedirs(self.output_dir, exist_ok=True)

        self.is_downloading = True
        fmt_up = self.format_var.get().upper()
        self.dl_btn.config(text=f"⏳  DOWNLOADING {fmt_up}...", state="disabled", bg="#555")
        self.progress.start(8)
        self._log(f"Starting download: {url[:60]}...", MUTED)

        thread = threading.Thread(target=self._download, args=(url,), daemon=True)
        thread.start()

    def _download(self, url):
        fmt = self.format_var.get()
        quality = self.quality_var.get().split()[0]

        mod = self._try_import_ytdlp()
        if mod is not None:
            self._download_ytdlp_module(url, fmt, quality, mod)
            return

        prefix = self._yt_dlp_prefix()
        if not prefix:
            self.root.after(0, lambda: self._finish(False, "yt-dlp not found. Run: pip install yt-dlp"))
            return

        cmd = prefix + [
            "-x",
            "--audio-format", fmt,
            "--audio-quality", quality,
            "--no-playlist",
            "-o", os.path.join(self.output_dir, "%(title)s.%(ext)s"),
            url,
        ]

        try:
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
            )

            for line in proc.stdout:
                line = line.strip()
                if line:
                    color = SUCCESS if "[download]" in line or "Destination" in line else MUTED
                    if "ERROR" in line or "error" in line.lower():
                        color = ERROR
                    self.root.after(0, lambda l=line, c=color: self._log(l, c))

            proc.wait()
            success = proc.returncode == 0
            msg = f"Saved to: {self.output_dir}" if success else "Download failed. Check the URL."
            self.root.after(0, lambda: self._finish(success, msg))

        except FileNotFoundError:
            self.root.after(0, lambda: self._finish(False, "yt-dlp not found. Run: pip install yt-dlp"))
        except Exception as ex:
            self.root.after(0, lambda: self._finish(False, str(ex)))

    def _download_ytdlp_module(self, url, fmt, quality, mod):
        from yt_dlp import YoutubeDL

        ffmpeg = self._ffmpeg_path()
        if not ffmpeg:
            self.root.after(0, lambda: self._finish(False, "ffmpeg not found."))
            return

        ffmpeg_dir = os.path.dirname(os.path.abspath(ffmpeg))

        def progress_hook(d):
            if d.get("status") != "finished":
                return
            fn = d.get("filename") or ""

            def log_done(f=fn):
                self._log(f"Converting: {os.path.basename(f)}", SUCCESS)

            self.root.after(0, log_done)

        outtmpl = os.path.join(self.output_dir, "%(title)s.%(ext)s")
        ydl_opts = {
            "ffmpeg_location": ffmpeg_dir,
            "format": "bestaudio/best",
            "outtmpl": outtmpl,
            "noplaylist": True,
            "quiet": True,
            "no_warnings": False,
            "logger": SoundCloudDownloader._YtdlpLogger(self),
            "progress_hooks": [progress_hook],
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": fmt,
                    "preferredquality": quality,
                }
            ],
        }

        try:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            self.root.after(0, lambda: self._finish(True, f"Saved to: {self.output_dir}"))
        except mod.utils.DownloadError as e:
            self.root.after(0, lambda: self._finish(False, str(e)))
        except Exception as ex:
            self.root.after(0, lambda: self._finish(False, str(ex)))

    def _finish(self, success, msg):
        self.is_downloading = False
        self.progress.stop()
        fmt_up = self.format_var.get().upper()
        self.dl_btn.config(text=f"⬇  DOWNLOAD {fmt_up}", state="normal", bg=ACCENT)
        color = SUCCESS if success else ERROR
        self._log(msg, color)
        if success:
            if messagebox.askyesno("Download Complete!",
                                    f"File saved!\n\n{self.output_dir}\n\nFolder open කරන්නද?"):
                os.startfile(self.output_dir)

if __name__ == "__main__":
    root = tk.Tk()
    app = SoundCloudDownloader(root)
    root.mainloop()
