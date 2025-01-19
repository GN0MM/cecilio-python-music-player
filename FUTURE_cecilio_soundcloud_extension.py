import soundcloud
import json
from PyQt5 import QtWidgets


class SoundCloudIntegration:
    def __init__(self):
        self.client_id = None

        # Загрузка конфигурации
        try:
            with open("soundcloud_config.json", "r") as config_file:
                config = json.load(config_file)
                self.client_id = config.get("client_id")
                if not self.client_id:
                    raise ValueError("Client ID not found in configuration.")
        except FileNotFoundError:
            print("Warning: SoundCloud configuration file not found. SoundCloud features are disabled.")
        except ValueError as e:
            print(f"Error in configuration file: {e}")

        # Создание клиента SoundCloud, если есть client_id
        if self.client_id:
            self.client = soundcloud.Client(client_id=self.client_id)
        else:
            self.client = None

    def resolve_url(self, track_url):
        if not self.client:
            raise ValueError("SoundCloud integration is not configured.")
        try:
            track = self.client.get('/resolve', url=track_url)
            return track
        except soundcloud.exceptions.HTTPError as e:
            raise ValueError(f"Failed to resolve URL: {e}")

    def get_stream_url(self, track_url):
        track = self.resolve_url(track_url)
        if hasattr(track, 'stream_url'):
            return f"{track.stream_url}?client_id={self.client_id}"
        else:
            raise ValueError("Stream URL not available for the given track.")

    def search_tracks(self, query, limit=10):
        if not self.client:
            raise ValueError("SoundCloud integration is not configured.")
        try:
            tracks = self.client.get('/tracks', q=query, limit=limit)
            return tracks
        except soundcloud.exceptions.HTTPError as e:
            raise ValueError(f"Error searching for tracks: {e}")


class SoundCloudStreamDialog(QtWidgets.QDialog):
    def __init__(self, soundcloud_integration):
        super().__init__()
        self.integration = soundcloud_integration
        self.tracks = []
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Stream from SoundCloud")
        self.setGeometry(300, 200, 400, 300)

        self.layout = QtWidgets.QVBoxLayout()

        self.url_label = QtWidgets.QLabel("Track URL:")
        self.url_input = QtWidgets.QLineEdit()

        self.search_label = QtWidgets.QLabel("Search for tracks:")
        self.search_input = QtWidgets.QLineEdit()
        self.search_button = QtWidgets.QPushButton("Search")

        self.track_list = QtWidgets.QListWidget()
        self.stream_button = QtWidgets.QPushButton("Stream Selected Track")

        self.layout.addWidget(self.url_label)
        self.layout.addWidget(self.url_input)
        self.layout.addWidget(self.search_label)
        self.layout.addWidget(self.search_input)
        self.layout.addWidget(self.search_button)
        self.layout.addWidget(self.track_list)
        self.layout.addWidget(self.stream_button)
        self.setLayout(self.layout)

        self.search_button.clicked.connect(self.search_tracks)
        self.stream_button.clicked.connect(self.stream_selected_track)

    def search_tracks(self):
        if not self.integration.client_id:
            QtWidgets.QMessageBox.warning(self, "Configuration Error", "SoundCloud is not configured.")
            return

        query = self.search_input.text()
        if not query:
            QtWidgets.QMessageBox.warning(self, "Input Error", "Please enter a search query.")
            return

        try:
            tracks = self.integration.search_tracks(query)
            self.track_list.clear()
            for track in tracks:
                self.track_list.addItem(f"{track.title} by {track.user['username']}")
            self.tracks = tracks
        except ValueError as e:
            QtWidgets.QMessageBox.critical(self, "Error", str(e))

    def stream_selected_track(self):
        selected_items = self.track_list.selectedItems()
        if not selected_items:
            QtWidgets.QMessageBox.warning(self, "Selection Error", "Please select a track to stream.")
            return

        selected_index = self.track_list.currentRow()
        selected_track = self.tracks[selected_index]

        try:
            stream_url = self.integration.get_stream_url(selected_track.permalink_url)
            self.accept()
            return stream_url
        except ValueError as e:
            QtWidgets.QMessageBox.critical(self, "Error", str(e))
