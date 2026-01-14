# YouTube Downloader GTK

A lightweight, modern, and intuitive graphical interface for downloading videos and audio from YouTube. This tool is designed to be simple yet powerful, providing a seamless experience for Linux users.

## Features

* **Versatile Downloads:** Download videos in various resolutions (from 360p up to Full HD 1080p).
* **Audio Extraction:** High-quality MP3 conversion for your favorite music and podcasts.
* **Smart Clipboard:** Automatically detects YouTube links from your clipboard upon startup.
* **Download History:** Keep track of your previous downloads with a built-in history log, including dates, quality, and status.
* **Proxy Support:** Integrated proxy settings to bypass network restrictions.
* **Modern Interface:** A clean, responsive GTK3 interface that adheres to system localization (e.g., automatically using your local "Downloads" folder).

## Requirements

This project is specifically tailored for **Debian 12 (Bookworm)** and newer distributions.

### Dependencies
The following packages are required for the application to function correctly:
* python3
* python3-gi (GObject Introspection)
* gir1.2-gtk-3.0
* yt-dlp (The core engine)
* ffmpeg (Required for 1080p video merging and MP3 conversion)

You can install them via terminal:

    sudo apt update
    sudo apt install python3-gi gir1.2-gtk-3.0 yt-dlp ffmpeg

## Installation

### Download pre-built package

You can download the ready-to-use [.deb package][deb] with latest version and install using:

    sudo apt install ./yt-dlp-gtk_0.7.1_all.deb

### Running from source

Alternatively, you can run the script directly:

    python3 yt_downloader.py

## Acknowledgments

This project is based on [yt-dlp](https://github.com/yt-dlp/yt-dlp). I am grateful to its authors and contributors 
for developing and maintaining such a reliable core engine, which made this graphical interface possible.

## Contributing

**Contributions are welcome**! To keep the project clean and manageable, please follow these simple rules:

1.  Keep it Simple: Avoid adding bloated features that deviate from the "minimalist" goal.
2.  Follow Style: Maintain the existing Python and GTK coding style.
3.  Test Your Changes: Ensure the app runs on Debian 12 before submitting a Pull Request.
4.  One Thing at a Time: Submit separate PRs for different fixes or features.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

[deb]: https://github.com/ashtokalo/yt-dlp-gtk/releases/download/0.7.1/yt-dlp-gtk_0.7.1_all.deb
