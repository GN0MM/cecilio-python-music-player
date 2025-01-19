import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import json
from PyQt5 import QtWidgets

class SpotifyIntegration:
    def __init__(self):
        self.client_id = None
        self.client_secret = None

        # Загрузка конфигурации
        try:
            with open("spotify_config.json", "r") as config_file:
                config = json.load(config_file)
                self.client_id = config.get("client_id")
                self.client_secret = config.get("client_secret")
                if not self.client_id or not self.client_secret:
                    raise ValueError("Client ID or Client Secret not found in configuration.")
        except FileNotFoundError:
            print("Warning: Spotify configuration file not found. Spotify features are disabled.")
        except ValueError as e:
            print(f"Error in configuration file: {e}")

        # Создание клиента Spotify, если есть данные конфигурации
        if self.client_id and self.client_secret:
            self.client = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
                client_id=self.client_id,
                client_secret=self.client_secret
            ))
        else:
            self.client = None

    def search_tracks(self, query, limit=10):
        if not self.client:
            raise ValueError("Spotify integration is not configured.")
        try:
            results = self.client.search(q=query, limit=limit, type='track')
            return results['tracks']['items']
        except Exception as e:
            raise ValueError(f"Error searching for tracks: {e}")

class SpotifyStreamDialog(QtWidgets.QDialog):
    def __init__(self, spotify_integration):
        super().__init__()
        self.integration = spotify_integration
        self.tracks = []
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Stream from Spotify")
        self.setGeometry(300, 200, 400, 300)

        self.layout = QtWidgets.QVBoxLayout()

        self.search_label = QtWidgets.QLabel("Search for tracks:")
        self.search_input = QtWidgets.QLineEdit()
        self.search_button = QtWidgets.QPushButton("Search")

        self.track_list = QtWidgets.QListWidget()
        self.stream_button = QtWidgets.QPushButton("Stream Selected Track")

        self.layout.addWidget(self.search_label)
        self.layout.addWidget(self.search_input)
        self.layout.addWidget(self.search_button)
        self.layout.addWidget(self.track_list)
        self.layout.addWidget(self.stream_button)
        self.setLayout(self.layout)

        self.search_button.clicked.connect(self.search_tracks)
        self.stream_button.clicked.connect(self.stream_selected_track)

    def search_tracks(self):
        query = self.search_input.text()
        if not query:
            QtWidgets.QMessageBox.warning(self, "Input Error", "Please enter a search query.")
            return

        try:
            tracks = self.integration.search_tracks(query)
            self.track_list.clear()
            for track in tracks:
                self.track_list.addItem(f"{track['name']} by {', '.join(artist['name'] for artist in track['artists'])}")
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
            return selected_track['preview_url']
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Cannot stream track: {e}")
