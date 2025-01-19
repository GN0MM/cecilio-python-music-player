import requests
import json
from PyQt5 import QtWidgets

class YouTubeIntegration:
    def __init__(self):
        try:
            with open("youtube_config.json", "r") as config_file:
                config = json.load(config_file)
                self.api_key = config.get("api_key")
                if not self.api_key:
                    raise ValueError("API key not found in configuration.")
        except FileNotFoundError:
            print("Warning: YouTube configuration file not found. YouTube features are disabled.")
            self.api_key = None
        except ValueError as e:
            print(f"Error in YouTube configuration file: {e}")
            self.api_key = None

    def search_videos(self, query, max_results=10):
        if not self.api_key:
            raise ValueError("YouTube integration is not configured.")

        url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            "part": "snippet",
            "q": query,
            "type": "video",
            "maxResults": max_results,
            "key": self.api_key
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json().get("items", [])
        except requests.RequestException as e:
            raise ValueError(f"Error fetching YouTube videos: {e}")

class YouTubeStreamDialog(QtWidgets.QDialog):
    def __init__(self, youtube_integration):
        super().__init__()
        self.integration = youtube_integration
        self.videos = []
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Stream from YouTube")
        self.setGeometry(300, 200, 400, 300)

        self.layout = QtWidgets.QVBoxLayout()

        self.search_label = QtWidgets.QLabel("Search for videos:")
        self.search_input = QtWidgets.QLineEdit()
        self.search_button = QtWidgets.QPushButton("Search")

        self.video_list = QtWidgets.QListWidget()
        self.stream_button = QtWidgets.QPushButton("Play Selected Video")

        self.layout.addWidget(self.search_label)
        self.layout.addWidget(self.search_input)
        self.layout.addWidget(self.search_button)
        self.layout.addWidget(self.video_list)
        self.layout.addWidget(self.stream_button)
        self.setLayout(self.layout)

        self.search_button.clicked.connect(self.search_videos)
        self.stream_button.clicked.connect(self.stream_selected_video)

    def search_videos(self):
        query = self.search_input.text()
        if not query:
            QtWidgets.QMessageBox.warning(self, "Input Error", "Please enter a search query.")
            return

        try:
            videos = self.integration.search_videos(query)
            self.video_list.clear()
            for video in videos:
                title = video["snippet"]["title"]
                self.video_list.addItem(title)
            self.videos = videos
        except ValueError as e:
            QtWidgets.QMessageBox.critical(self, "Error", str(e))

    def stream_selected_video(self):
        selected_items = self.video_list.selectedItems()
        if not selected_items:
            QtWidgets.QMessageBox.warning(self, "Selection Error", "Please select a video to play.")
            return

        selected_index = self.video_list.currentRow()
        selected_video = self.videos[selected_index]
        video_url = f"https://www.youtube.com/watch?v={selected_video['id']['videoId']}"

        try:
            self.accept()
            return video_url
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Cannot play video: {e}")
