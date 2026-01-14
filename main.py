#!/usr/bin/python3
import datetime
import json
import os
import re
import shutil
import subprocess
import threading

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk, GLib, Gio, Gdk

APP_NAME = "yt-dlp-gtk"
VERSION = "0.7.1"
CONFIG_DIR = os.path.expanduser(f"~/.config/{APP_NAME}")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
HISTORY_FILE = os.path.join(CONFIG_DIR, "history.json")
DEFAULT_DOWNLOADS = GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_DOWNLOAD) or os.path.expanduser("~/")

class App():

    def __init__(self):
        self.process = None
        self.has_ffmpeg = shutil.which("ffmpeg") is not None

        # Загружаем настройки приложения
        if not os.path.exists(CONFIG_DIR):
            os.makedirs(CONFIG_DIR)
        self.settings = {"download_path": DEFAULT_DOWNLOADS, "proxy": "", "last_quality": "720"}
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    self.settings.update(json.load(f))
            except:
                pass

        # Загружаем историю
        self.history = []
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, 'r') as f:
                    self.history = json.load(f)
            except:
                pass

        # Главное окно
        self.window = Gtk.Window(title="Загрузчик с You Tube")
        GLib.set_application_name(self.window.get_title())
        self.window.set_icon_name("video-x-generic")
        self.window.set_default_icon_name("video-x-generic")
        self.window.set_default_size(550, -1)
        self.window.set_border_width(15)
        self.window.connect("delete-event", self.on_main_window_delete)
        self.window.connect("key-press-event", self.on_key_press)

        header = Gtk.HeaderBar(title="Загрузчик с You Tube", show_close_button=True)
        self.window.set_titlebar(header)

        for icon, handler, tooltip in [
            ("preferences-system-symbolic", self.show_settings_dialog, "Настройки"),
            ("document-open-recent-symbolic", self.show_history_dialog, "История"),
            ("help-about-symbolic", self.show_info_dialog, "О программе")
        ]:
            btn = Gtk.Button.new_from_icon_name(icon, Gtk.IconSize.BUTTON)
            btn.set_tooltip_text(tooltip)
            btn.connect("clicked", handler)
            header.pack_end(btn)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        self.window.add(vbox)

        # Адресная строка
        self.entry_url = Gtk.Entry(placeholder_text="Вставьте ссылку на You Tube видео...")
        self.entry_url.set_tooltip_text(self.entry_url.get_placeholder_text())
        self.entry_url.connect("changed", self.on_url_changed)
        self.entry_url.connect("activate", lambda e: self.on_download_clicked(None))
        vbox.pack_start(self.entry_url, False, False, 0)

        # Индикатор загрузки
        self.progress_bar = Gtk.ProgressBar()
        vbox.pack_start(self.progress_bar, False, False, 0)

        self.hbox_controls = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)

        # Выбор качества
        self.quality_combo = Gtk.ComboBoxText()
        self.quality_combo.set_tooltip_text("Выберите качество загрузки")
        options = [("best", "Макс."), ("1080", "1080p"), ("720", "720p"), ("480", "480p"), ("360", "360p"), ("mp3", "MP3")]
        for k, l in options:
            label = l + (" (нужен ffmpeg)" if k in ["1080", "mp3"] and not self.has_ffmpeg else "")
            self.quality_combo.append(k, label)

        self.quality_combo.set_active_id(self.settings.get("last_quality", "720"))
        self.quality_combo.connect("changed", self.on_quality_changed)
        self.hbox_controls.pack_start(self.quality_combo, False, False, 0)

        # Кнопка "Загрузить"
        self.btn_download = Gtk.Button(label="Загрузить видео с You Tube")
        self.btn_download.connect("clicked", self.on_download_clicked)
        self.btn_download.set_sensitive(False)
        self.hbox_controls.pack_end(self.btn_download, True, True, 0)

        # Кнопка "Отмена"
        self.btn_cancel = Gtk.Button(label="Отмена")
        self.btn_cancel.connect("clicked", self.on_cancel_clicked)
        self.btn_cancel.set_no_show_all(True)
        self.hbox_controls.pack_end(self.btn_cancel, True, True, 0)

        vbox.pack_start(self.hbox_controls, False, False, 0)
        self.window.show_all()
        self.btn_cancel.hide()

        # Задержка для инициализации буфера обмена
        GLib.timeout_add(300, self.check_clipboard_for_url)

    def save_settings(self):
        with open(CONFIG_FILE, 'w') as f: json.dump(self.settings, f)

    def save_history(self):
        with open(HISTORY_FILE, 'w') as f: json.dump(self.history, f)

    def check_clipboard_for_url(self):
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        clipboard.request_text(self._on_clipboard_received)
        return False

    def _on_clipboard_received(self, clipboard, text):
        if text is not None:
            match = re.search(r'(https?://(?:www\.)?(?:youtube\.com|youtu\.be)/\S+)', text)
            if match:
                self.entry_url.set_text(match.group(1).strip())

    def on_key_press(self, widget, event):
        if event.keyval == Gdk.KEY_Escape:
            self.on_main_window_delete(widget, event, strict_exit=False)
            return True
        return False

    def on_main_window_delete(self, widget, event, strict_exit=True):
        if self.process is not None:
            dialog = Gtk.MessageDialog(transient_for=self.window, modal=True, message_type=Gtk.MessageType.QUESTION,
                buttons=Gtk.ButtonsType.YES_NO, text="Идет загрузка. Отменить и выйти?" if strict_exit else "Отменить загрузку?")
            res = dialog.run()
            dialog.destroy()
            if res == Gtk.ResponseType.YES:
                self.on_cancel_clicked(None)
                if strict_exit: Gtk.main_quit()
                return False
            return True
        Gtk.main_quit()
        return False

    def on_url_changed(self, entry):
        url = entry.get_text()
        self.btn_download.set_sensitive("youtube.com" in url or "youtu.be" in url)

    def on_quality_changed(self, combo):
        self.settings["last_quality"] = combo.get_active_id()
        self.save_settings()

    def on_cancel_clicked(self, widget):
        if self.process:
            self.process.terminate()
            self.process = None

    def on_download_clicked(self, widget):
        if not self.btn_download.get_sensitive(): return
        url = self.entry_url.get_text()
        quality = self.quality_combo.get_active_id()
        self.entry_url.set_editable(False)
        self.btn_download.hide()
        self.btn_cancel.show()
        threading.Thread(target=self.download, args=(url, self.settings['download_path'], quality), daemon=True).start()

    def show_settings_dialog(self, widget):
        # Исправлено: default_size убран из конструктора
        win = Gtk.Window(title="Настройки", transient_for=self.window, modal=True)
        win.set_border_width(15)
        win.set_default_size(450, -1)
        win.connect("key-press-event", lambda w, e: win.destroy() if e.keyval == Gdk.KEY_Escape else False)

        v = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        win.add(v)
        v.pack_start(Gtk.Label(label="Путь сохранения загруженного видео:", xalign=0), 0, 0, 0)
        h1 = Gtk.Box(spacing=5)
        en = Gtk.Entry(text=self.settings['download_path'])
        en.connect("changed", lambda e: self.update_setting('download_path', e.get_text()))
        h1.pack_start(en, 1, 1, 0)
        btn_b = Gtk.Button(label="Обзор")
        btn_b.connect("clicked", self.on_browse_clicked, en)
        h1.pack_start(btn_b, 0, 0, 0)
        v.pack_start(h1, 0, 0, 0)
        v.pack_start(Gtk.Label(label="Прокси (например, socks5://user:pass@host:port):", xalign=0), 0, 0, 0)
        pe = Gtk.Entry(text=self.settings['proxy'])
        pe.connect("changed", lambda e: self.update_setting('proxy', e.get_text()))
        v.pack_start(pe, 0, 0, 0)
        win.show_all()

    def update_setting(self, k, v):
        self.settings[k] = v
        self.save_settings()

    def on_browse_clicked(self, b, en):
        d = Gtk.FileChooserDialog(title="Папка", transient_for=self.window, action=Gtk.FileChooserAction.SELECT_FOLDER)
        d.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK)
        if d.run() == Gtk.ResponseType.OK:
            path = d.get_filename()
            en.set_text(path)
            self.update_setting('download_path', path)
        d.destroy()

    def show_history_dialog(self, widget):
        win = Gtk.Window(title="История загрузок", transient_for=self.window, modal=True)
        win.set_default_size(500, 400)
        win.connect("key-press-event", lambda w, e: win.destroy() if e.keyval == Gdk.KEY_Escape else False)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10, border_width=10)
        win.add(vbox)
        scrolled = Gtk.ScrolledWindow()
        vbox.pack_start(scrolled, True, True, 0)
        listbox = Gtk.ListBox()
        listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        scrolled.add(listbox)

        for item in reversed(self.history):
            row = Gtk.ListBoxRow()
            hbox = Gtk.Box(spacing=0, margin=0)
            row.add(hbox)
            iv = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            lb = Gtk.LinkButton.new_with_label(item['url'], item['url'][:50] + "...")
            lb.set_halign(Gtk.Align.START)
            iv.pack_start(lb, 0, 0, 0)
            st = "Ошибка" if item.get('error') else "Загружено"
            lbl = Gtk.Label(xalign=0, margin_left=20)
            lbl.set_markup(f"<small>{item['date']} | {item['quality']} | {st}</small>")
            iv.pack_start(lbl, 0, 0, 0)
            hbox.pack_start(iv, True, True, 0)
            cb = Gtk.Button.new_from_icon_name("edit-copy-symbolic", Gtk.IconSize.BUTTON)
            cb.set_relief(Gtk.ReliefStyle.NONE)
            cb.connect("clicked", lambda b, u=item['url']: Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD).set_text(u, -1))
            hbox.pack_end(cb, False, False, 0)
            listbox.add(row)

        cl = Gtk.Button(label="Удалить историю")
        cl.connect("clicked", lambda b: (self.on_delete_history(b), win.destroy()))
        vbox.pack_end(cl, False, False, 0)
        win.show_all()

    def on_delete_history(self, widget):
        self.history = []
        self.save_history()

    def show_info_dialog(self, widget):
        about = Gtk.AboutDialog(transient_for=self.window, modal=True, program_name="Загрузчик", logo=None)
        about.set_program_name("Загрузчик с You Tube")
        about.set_version(VERSION)
        about.set_website("https://github.com/ashtokalo/yt-dlp-gtk")
        about.set_website_label("GitHub")
        about.set_license_type(Gtk.License.MIT_X11)
        about.set_logo_icon_name("video-x-generic")
        about.set_comments("Простая программа для скачивания видео и аудио с You Tube основанная на yt-dlp.")
        about.connect("key-press-event", lambda w, e: about.destroy() if e.keyval == Gdk.KEY_Escape else False)
        about.run()
        about.destroy()

    def download(self, url, path, quality):
        proxy = self.settings.get('proxy')
        err = None
        cmd = ["yt-dlp", "--newline", "--no-mtime"]
        if quality == "mp3":
            cmd.extend(["-x", "--audio-format", "mp3"])
        elif quality == "best":
            cmd.extend(["-f", "bestvideo+bestaudio/best"])
        else:
            cmd.extend(["-f", f"bestvideo[height<={quality}]+bestaudio/best"])
        cmd.extend(["-o", f"{path}/%(title)s.%(ext)s"])
        if proxy: cmd.extend(["--proxy", proxy])
        cmd.append(url)

        try:
            progress = 3.0
            self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            for line in self.process.stdout:
                match = re.search(r'(\d+\.\d+)%', line)
                if match:
                    percent_done = float(match.group(1))
                    if percent_done < 99:
                        progress = max(progress, percent_done - 20.0)
                        GLib.idle_add(self.progress_bar.set_fraction, progress / 100)
            self.process.wait()
            if self.process and self.process.returncode != 0: 
                err = "Ошибка"
            else:
                GLib.idle_add(self.progress_bar.set_fraction, 1.0)
        except Exception as e:
            err = str(e)
        finally:
            success = (err is None and self.process is not None and self.process.returncode == 0)
            self.history.append(
                {"url": url, "quality": quality, "date": datetime.datetime.now().strftime("%d.%m.%Y %H:%M"),
                 "error": err})
            self.save_history()
            self.process = None
            GLib.idle_add(self.finalize, success, path)

    def finalize(self, success, path):
        self.btn_cancel.hide()
        self.btn_download.show()
        self.entry_url.set_editable(True)
        if success:
            d = Gtk.MessageDialog(transient_for=self.window, modal=True, message_type=Gtk.MessageType.INFO,
                                  buttons=Gtk.ButtonsType.OK, text="Готово!")
            d.add_button("Открыть папку", Gtk.ResponseType.YES)
            if d.run() == Gtk.ResponseType.YES: Gio.AppInfo.launch_default_for_uri("file://" + path, None)
            d.destroy()
        else:
            self.progress_bar.set_fraction(0.0)

if __name__ == "__main__":
    app = App()
    Gtk.main()
