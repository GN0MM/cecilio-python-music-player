import numpy as np
import torch
import torchvision.transforms as transforms
from torchvision.models import ResNet18_Weights
from PIL import Image, ImageDraw
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtMultimedia import QMediaPlayer


class AdvancedMusicVisualiser(QtWidgets.QGraphicsView):
    def __init__(self):
        super().__init__()
        self.scene = QtWidgets.QGraphicsScene()
        self.setScene(self.scene)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_visualisation)
        self.media_player = None

        self.model = self.load_neural_network()
        self.transform = transforms.Compose([
            transforms.Resize((256, 256)),
            transforms.ToTensor(),
        ])

        # Переменные для режимов
        self.visualisation_mode = "polygons"  # Режим по умолчанию
        self.shuffle_effect = False
        self.repeat_effect = False
        self.rotation_angle = 0
        self.pulse_step = 0

    def load_neural_network(self):
        try:
            print("Loading ResNet18 model...")
            torch.hub.set_dir("C:/Users/Илья/.cache/torch")  # Custom cache path
            model = torch.hub.load('pytorch/vision', 'resnet18', weights=ResNet18_Weights.DEFAULT)
            model.eval()
            print("Model loaded successfully.")
            return model
        except Exception as e:
            print(f"Error loading neural network: {e}")
            return None

    def start_visualisation(self, media_player, shuffle=False, repeat=False):
        print("Starting visualisation...")
        self.media_player = media_player
        self.shuffle_effect = shuffle
        self.repeat_effect = repeat
        self.timer.start(75)

    def stop_visualisation(self):
        print("Stopping visualisation...")
        self.timer.stop()

    def set_visualisation_mode(self, mode):
        print(f"Switching visualisation mode to: {mode}")
        self.visualisation_mode = mode

    def generate_visual(self, audio_features, volume):
        base_image = Image.new('RGB', (512, 512), (0, 0, 0))
        draw = ImageDraw.Draw(base_image)
        center_x, center_y = 256, 256

        # Применение эффектов "Shuffle" и "Repeat"
        if self.repeat_effect:
            self.pulse_step = (self.pulse_step + 5) % 50
            volume += self.pulse_step / 100
        if self.shuffle_effect:
            self.rotation_angle = (self.rotation_angle + 5) % 360

        if self.visualisation_mode == "polygons":
            self.draw_polygons(draw, center_x, center_y, audio_features, volume)
        elif self.visualisation_mode == "waves":
            self.draw_waves(draw, center_x, center_y, audio_features, volume)
        elif self.visualisation_mode == "stars":
            self.draw_stars(draw, center_x, center_y, audio_features, volume)
        elif self.visualisation_mode == "lines":
            self.draw_lines(draw, center_x, center_y, audio_features, volume)

        return base_image.rotate(self.rotation_angle, expand=False)

    def draw_polygons(self, draw, center_x, center_y, audio_features, volume):
        max_radius = 250
        for i, feature in enumerate(audio_features[:10]):
            radius = int(max_radius * feature * volume)
            angle_step = 360 / 6
            points = [
                (
                    center_x + radius * np.cos(np.radians(angle_step * k)),
                    center_y + radius * np.sin(np.radians(angle_step * k))
                )
                for k in range(6)
            ]
            color = (int(volume * 255), int(feature * 255), int((1 - feature) * 255))
            draw.polygon(points, outline=color, width=3)

    def draw_waves(self, draw, center_x, center_y, audio_features, volume):
        for i, feature in enumerate(audio_features[:15]):
            radius = 50 + i * 15
            color = (
                int(volume * 255),
                int(feature * 255),
                int((1 - feature) * 255),
            )
            draw.ellipse(
                (center_x - radius, center_y - radius, center_x + radius, center_y + radius),
                outline=color,
                width=2,
            )

    def draw_stars(self, draw, center_x, center_y, audio_features, volume):
        for i, feature in enumerate(audio_features[:12]):
            radius = int(200 * feature * volume)
            angle = np.radians(i * (360 / 12))
            x = center_x + radius * np.cos(angle)
            y = center_y + radius * np.sin(angle)
            color = (
                int(volume * 255),
                int(feature * 200 + 50),
                255 - int(feature * 200),
            )
            draw.line((center_x, center_y, x, y), fill=color, width=3)

    def draw_lines(self, draw, center_x, center_y, audio_features, volume):
        for i, feature in enumerate(audio_features[:15]):
            x0 = int(center_x - 200 * feature * volume)
            y0 = int(center_y + (i - 7) * 20)
            x1 = int(center_x + 200 * feature * volume)
            y1 = y0
            color = (int(feature * 255), int(volume * 255), 255 - int(volume * 255))
            draw.line((x0, y0, x1, y1), fill=color, width=2)

    def update_visualisation(self):
        if not self.media_player or self.media_player.state() != QMediaPlayer.PlayingState:
            return

        audio_features = np.abs(np.sin(np.linspace(0, np.pi, 30)) + np.random.randn(30) * 0.1)
        volume = self.media_player.volume() / 100

        visual_image = self.generate_visual(audio_features, volume)
        visual_image = visual_image.convert("RGB")
        qt_image = QtGui.QImage(
            visual_image.tobytes("raw", "RGB"),
            visual_image.width,
            visual_image.height,
            QtGui.QImage.Format_RGB888,
        )
        pixmap = QtGui.QPixmap.fromImage(qt_image)
        pixmap_item = QtWidgets.QGraphicsPixmapItem(pixmap)

        self.scene.clear()
        self.scene.addItem(pixmap_item)
