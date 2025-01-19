import os
import sys
import random
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QTableWidget, QTableWidgetItem, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSlider
from cecilio_audio_visualiser import AdvancedMusicVisualiser

# Импорт библиотек для стриминга
try:
    import soundcloud
    from pytube import YouTube
    from spotipy import Spotify
    from spotipy.oauth2 import SpotifyClientCredentials
except ImportError:
    print("Missing required libraries. Please install soundcloud, pytube, and spotipy.")

os.environ["QT_OPENGL"] = "angle"
os.environ["QT_PLUGIN_PATH"] = os.path.join(
    os.path.dirname(sys.executable), "Lib", "site-packages", "PyQt5", "Qt5", "plugins"
)

class CecilioMusicPlayer(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.media_player = QMediaPlayer(None, QMediaPlayer.StreamPlayback)
        self.visualiser = AdvancedMusicVisualiser()
        self.playlist = []
        self.previous_tracks = []
        self.shuffle_playlist = []
        self.current_index = -1
        self.repeat = False
        self.shuffle = False
        self.language = "en"
        self.translations = {
            "en": {
                "window_title": "Cecilio Music Player",
                "play": "Play",
                "pause": "Pause",
                "next": "Next",
                "previous": "Previous",
                "open_files": "Open Files",
                "shuffle": "Shuffle",
                "repeat": "Repeat",
                "volume": "Volume",
                "shuffle_playlist": "Shuffle Playlist",
                "playlist_title": "Playlist",
                "error_no_files": "No files in playlist.",
                "playlist_shuffled": "Playlist has been shuffled!",
                "playlist_loaded": "{count} files added to playlist.",
                "Options": "Options",
                "Visualisation": "Visualisation",
                "soundcloud_prompt": "Enter Soundcloud URL:",
                "spotify_prompt": "Enter Spotify URL:",
                "youtube_prompt": "Enter YouTube URL:",
                "streaming_error": "Failed to load stream. Please check the URL.",
            },
            "ru": {
                "window_title": "Плеер Cecilio",
                "play": "Играть",
                "pause": "Пауза",
                "next": "Следующий",
                "previous": "Предыдущий",
                "open_files": "Открыть Файлы",
                "shuffle": "Перемешать",
                "repeat": "Повтор",
                "volume": "Громкость",
                "shuffle_playlist": "Перемешать Плейлист",
                "playlist_title": "Плейлист",
                "error_no_files": "Нет файлов в плейлисте.",
                "playlist_shuffled": "Плейлист перемешан!",
                "playlist_loaded": "{count} файлов добавлено в плейлист.",
                "Options": "Опции",
                "Visualisation": "Визуализация",
                "soundcloud_prompt": "Введите URL Soundcloud:",
                "spotify_prompt": "Введите URL Spotify:",
                "youtube_prompt": "Введите URL YouTube:",
                "streaming_error": "Не удалось загрузить стрим. Проверьте URL.",
            },
        }
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(self.translate("window_title"))
        screen_geometry = QtWidgets.QApplication.primaryScreen().availableGeometry()
        self.resize(int(screen_geometry.width() * 0.4), int(screen_geometry.height() * 0.75))

        # Меню настроек
        menu_bar = self.menuBar()
        options_menu = menu_bar.addMenu("Options")
        language_menu = options_menu.addMenu("Languages")
        language_menu.addAction("English", lambda: self.change_language("en"))
        language_menu.addAction("Русский", lambda: self.change_language("ru"))
        visualisation_menu = options_menu.addMenu("Visualisation")
        visualisation_menu.addAction("Polygons", lambda: self.visualiser.set_visualisation_mode("polygons"))
        visualisation_menu.addAction("Waves", lambda: self.visualiser.set_visualisation_mode("waves"))
        visualisation_menu.addAction("Stars", lambda: self.visualiser.set_visualisation_mode("stars"))
        visualisation_menu.addAction("Lines", lambda: self.visualiser.set_visualisation_mode("lines"))
        streaming_menu = menu_bar.addMenu("Streaming")
        streaming_menu.addAction("Soundcloud", self.stream_from_soundcloud)
        streaming_menu.addAction("Spotify", self.stream_from_spotify)
        streaming_menu.addAction("YouTube", self.stream_from_youtube)

        # Основной виджет
        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        # Визуализатор
        self.visualiser_widget = QtWidgets.QWidget()
        self.visualiser_layout = QVBoxLayout(self.visualiser_widget)
        self.visualiser_layout.setContentsMargins(0, 0, 0, 0)
        self.visualiser_layout.addWidget(self.visualiser)
        self.main_layout.addWidget(self.visualiser_widget)

        # Полоска прогресса
        self.progress_bar = QSlider(QtCore.Qt.Horizontal)
        self.progress_bar.setMaximumWidth(5000)
        self.progress_bar.setSingleStep(10)
        self.progress_bar.sliderMoved.connect(self.set_position)
        self.main_layout.addWidget(self.progress_bar, alignment=QtCore.Qt.AlignCenter)

        # Плейлист
        self.playlist_widget = QTableWidget(0, 1)
        self.playlist_widget.setHorizontalHeaderLabels([self.translate("playlist_title")])
        self.playlist_widget.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.playlist_widget.verticalHeader().setVisible(False)
        self.playlist_widget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.playlist_widget.setFixedHeight(180)
        self.main_layout.addWidget(self.playlist_widget)

        # Панель управления
        self.controls_layout = QHBoxLayout()
        self.play_pause_button = QPushButton(self.translate("play"))
        self.next_button = QPushButton(self.translate("next"))
        self.prev_button = QPushButton(self.translate("previous"))
        self.open_button = QPushButton(self.translate("open_files"))
        self.shuffle_button = QPushButton(self.translate("shuffle"))
        self.repeat_button = QPushButton(self.translate("repeat"))
        self.shuffle_playlist_button = QPushButton(self.translate("shuffle_playlist"))
        self.volume_slider = QSlider(QtCore.Qt.Horizontal)
        self.volume_label = QLabel("100%")

        self.shuffle_button.setCheckable(True)
        self.repeat_button.setCheckable(True)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(100)
        self.volume_slider.setMaximumWidth(200)

        self.controls_layout.addWidget(self.prev_button)
        self.controls_layout.addWidget(self.play_pause_button)
        self.controls_layout.addWidget(self.next_button)
        self.controls_layout.addWidget(self.open_button)
        self.controls_layout.addWidget(self.shuffle_button)
        self.controls_layout.addWidget(self.repeat_button)
        self.controls_layout.addWidget(self.shuffle_playlist_button)
        self.volume_text = QLabel(self.translate("volume"))
        self.controls_layout.addWidget(self.volume_text)
        self.controls_layout.addWidget(self.volume_slider)
        self.controls_layout.addWidget(self.volume_label)

        self.main_layout.addLayout(self.controls_layout)

        # Сигналы
        self.play_pause_button.clicked.connect(self.play_pause_music)
        self.next_button.clicked.connect(self.next_track)
        self.prev_button.clicked.connect(self.prev_track)
        self.open_button.clicked.connect(self.open_files)
        self.shuffle_button.clicked.connect(self.toggle_shuffle)
        self.repeat_button.clicked.connect(self.toggle_repeat)
        self.shuffle_playlist_button.clicked.connect(self.shuffle_playlist_action)
        self.volume_slider.valueChanged.connect(self.change_volume)
        self.media_player.positionChanged.connect(self.update_progress)
        self.media_player.durationChanged.connect(self.set_progress_max)
        self.media_player.mediaStatusChanged.connect(self.handle_media_end)

        # Горячие клавиши
        QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Space), self).activated.connect(self.play_pause_music)

    def translate(self, key):
        return self.translations[self.language].get(key, key)

    def change_language(self, lang):
        self.language = lang
        self.setWindowTitle(self.translate("window_title"))
        self.update_ui_texts()

    def update_ui_texts(self):
        self.play_pause_button.setText(self.translate("play" if self.media_player.state() != QMediaPlayer.PlayingState else "pause"))
        self.next_button.setText(self.translate("next"))
        self.prev_button.setText(self.translate("previous"))
        self.open_button.setText(self.translate("open_files"))
        self.shuffle_button.setText(self.translate("shuffle"))
        self.shuffle_playlist_button.setText(self.translate("shuffle_playlist"))
        self.repeat_button.setText(self.translate("repeat"))
        self.playlist_widget.setHorizontalHeaderLabels([self.translate("playlist_title")])
        self.volume_text.setText(self.translate("volume"))


    def shuffle_playlist_action(self):
        if not self.playlist:
            QMessageBox.warning(self, self.translate("playlist_title"), self.translate("error_no_files"))
            return
        random.shuffle(self.playlist)  # Перемешивание списка треков
        self.current_index = 0  # Установка текущего индекса на первый трек после перемешивания
        self.update_playlist()  # Обновление отображения плейлиста
        self.play_music()  # Автоматическое воспроизведение первого трека
        QMessageBox.information(self, self.translate("playlist_title"), self.translate("playlist_shuffled"))

# DOESN'T WORK?
    def update_playlist(self):
        self.playlist_widget.setRowCount(len(self.playlist))
        for i, track in enumerate(self.playlist):
            item = QTableWidgetItem(os.path.basename(track))
            item.setToolTip(track)
            self.playlist_widget.setItem(i, 0, item)
        self.highlight_current_track()


    def generate_shuffle_playlist(self):
        self.shuffle_playlist = random.sample(range(len(self.playlist)), len(self.playlist))


    def play_pause_music(self):
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.pause_music()
        else:
            self.play_music()

    def play_music(self):
        if self.current_index == -1 and self.playlist:
            self.current_index = 0
        if not self.playlist or self.current_index == -1:
            QMessageBox.warning(self, self.translate("playlist_title"), self.translate("error_no_files"))
            return
        file_path = self.playlist[self.current_index]
        if self.media_player.media().canonicalUrl().toString() != QtCore.QUrl.fromLocalFile(file_path).toString():
            self.media_player.setMedia(QMediaContent(QtCore.QUrl.fromLocalFile(file_path)))
        self.media_player.play()
        self.play_pause_button.setText(self.translate("pause"))
        self.visualiser.start_visualisation(self.media_player)
        self.highlight_current_track()

    def pause_music(self):
        self.media_player.pause()
        self.play_pause_button.setText(self.translate("play"))
        self.visualiser.stop_visualisation()

    def prev_track(self):
        if not self.playlist:
            return
        if self.previous_tracks:
            self.current_index = self.previous_tracks.pop()
        else:
            if self.media_player.position() > 5000:
                self.media_player.setPosition(0)
                return
            self.current_index = (self.current_index - 1) % len(self.playlist)
        self.play_music()

    def next_track(self):
        if not self.playlist:
            return
        if self.shuffle:
            self.previous_tracks.append(self.current_index)
            self.current_index = self.shuffle_playlist.pop(0) if self.shuffle_playlist else 0
        else:
            self.previous_tracks.append(self.current_index)
            self.current_index = (self.current_index + 1) % len(self.playlist)
        self.play_music()

    def open_files(self):
        try:
            files, _ = QFileDialog.getOpenFileNames(self, self.translate("open_files"), "", "Audio Files (*.mp3 *.wav *.flac)")
            if files:
                self.playlist = files
                self.current_index = 0
                self.previous_tracks = []
                self.update_playlist()
                QMessageBox.information(self, self.translate("playlist_title"), self.translate("playlist_loaded").format(count=len(files)))
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def update_playlist(self):
        self.playlist_widget.setRowCount(len(self.playlist))
        for i, track in enumerate(self.playlist):
            item = QTableWidgetItem(os.path.basename(track))
            item.setToolTip(track)
            self.playlist_widget.setItem(i, 0, item)
        self.highlight_current_track()

    def highlight_current_track(self):
        self.playlist_widget.clearSelection()
        if self.current_index >= 0:
            self.playlist_widget.selectRow(self.current_index)

    def toggle_shuffle(self):
        self.shuffle = self.shuffle_button.isChecked()
        if self.shuffle:
            self.generate_shuffle_playlist()

    def toggle_repeat(self):
        self.repeat = self.repeat_button.isChecked()

    def handle_media_end(self, status):
        if status == QMediaPlayer.EndOfMedia:
            if self.repeat:
                self.media_player.setPosition(0)
                self.media_player.play()
            else:
                self.next_track()

    def set_progress_max(self, duration):
        self.progress_bar.setMaximum(duration)

    def update_progress(self, position):
        self.progress_bar.setValue(position)

    def set_position(self, position):
        self.media_player.setPosition(position)

    def change_volume(self, value):
        self.volume_label.setText(f"{value}%")
        self.media_player.setVolume(value)


    def stream_from_soundcloud(self):
        url, ok = QtWidgets.QInputDialog.getText(self, "Soundcloud", self.translate("soundcloud_prompt"))
        if ok and url:
            try:
                client = soundcloud.Client(client_id="YOUR_SOUNDCLOUD_CLIENT_ID")
                track = client.get("/resolve", url=url)
                stream_url = client.get(track.stream_url, allow_redirects=False).location
                self.playlist.append(stream_url)
                self.update_playlist()
            except Exception as e:
                QMessageBox.critical(self, "Error", self.translate("streaming_error"))

    def stream_from_spotify(self):
        url, ok = QtWidgets.QInputDialog.getText(self, "Spotify", self.translate("spotify_prompt"))
        if ok and url:
            try:
                sp = Spotify(auth_manager=SpotifyClientCredentials(client_id="YOUR_SPOTIFY_CLIENT_ID", client_secret="YOUR_SPOTIFY_CLIENT_SECRET"))
                results = sp.track(url)
                stream_url = results["preview_url"]
                if stream_url:
                    self.playlist.append(stream_url)
                    self.update_playlist()
                else:
                    raise Exception("No preview available.")
            except Exception as e:
                QMessageBox.critical(self, "Error", self.translate("streaming_error"))

    def stream_from_youtube(self):
        url, ok = QtWidgets.QInputDialog.getText(self, "YouTube", self.translate("youtube_prompt"))
        if ok and url:
            try:
                yt = YouTube(url)
                stream_url = yt.streams.filter(only_audio=True).first().url
                self.playlist.append(stream_url)
                self.update_playlist()
            except Exception as e:
                QMessageBox.critical(self, "Error", self.translate("streaming_error"))

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = CecilioMusicPlayer()
    window.show()
    sys.exit(app.exec_())
