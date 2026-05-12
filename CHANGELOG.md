# Changelog

## 0.2.0

- Switch from calling yt-dlp via subprocess to using the yt-dlp Python library directly
- Accurate download progress display via progress_hook
- Add connection mode selection: direct / via proxy (radio buttons in settings)
- Improved download cancellation: instant stop via flag instead of terminating an external process

## 0.1.7

- Download history with URL copy
- Deb package build via Makefile

## 0.1.6

- Quality selection: best, 1080p, 720p, 480p, 360p, MP3
- Clipboard auto-detection of YouTube URLs

## 0.1.0

- Initial release
- GTK 3 interface for downloading videos via yt-dlp
- Proxy support
- Configurable download path
