# Переменные
PKG_NAME=yt-dlp-gtk
VERSION=0.7.1
BUILD_DIR=build

all:
	@echo "Используйте 'make deb' для создания пакета"

deb: clean
	# 1. Создание структуры каталогов внутри будущего пакета
	mkdir -p $(BUILD_DIR)/DEBIAN
	mkdir -p $(BUILD_DIR)/usr/bin
	mkdir -p $(BUILD_DIR)/usr/share/applications

	# 2. Копирование метаданных
	cp dest/DEBIAN/control $(BUILD_DIR)/DEBIAN/

	# 3. Копирование исполняемого файла
	cp main.py $(BUILD_DIR)/usr/bin/$(PKG_NAME)
	chmod +x $(BUILD_DIR)/usr/bin/$(PKG_NAME)

	# 4. Копирование desktop-файла
	cp dest/yt-dlp-gtk.desktop $(BUILD_DIR)/usr/share/applications/

	# 5. Сборка пакета
	dpkg-deb --build $(BUILD_DIR) $(PKG_NAME)_$(VERSION)_all.deb
	@echo "Готово! Пакет создан: $(PKG_NAME)_$(VERSION)_all.deb"

clean:
	rm -rf $(BUILD_DIR)
	rm -f *.deb

install-deps:
	sudo apt update && sudo apt install -y python3-gi gir1.2-gtk-3.0 yt-dlp ffmpeg