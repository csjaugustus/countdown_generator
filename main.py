import sys
import os
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QSpinBox, QLineEdit, QPushButton, QProgressBar,
                             QSlider, QColorDialog, QFileDialog, QComboBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap, QIcon, QColor
import cv2
from PIL import Image, ImageDraw, ImageFont

class VideoGenerator(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal()

    def __init__(self, width, height, duration, font_size, circle_radius, circle_width,
                 text_color, circle_color, bg_color, font_path, output_path, style):
        super().__init__()
        self.width = width
        self.height = height
        self.duration = duration
        self.font_size = font_size
        self.circle_radius = circle_radius
        self.circle_width = circle_width
        self.text_color = text_color
        self.circle_color = circle_color
        self.bg_color = bg_color
        self.font_path = font_path
        self.output_path = output_path
        self.style = style
        self.fps = 30
        self.current_frame = 0

    def run(self):
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(self.output_path, fourcc, self.fps, (self.width, self.height))

        total_frames = int(self.duration * self.fps)

        for frame_num in range(total_frames):
            t = frame_num / self.fps
            frame = self.make_frame(t)
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            out.write(frame_bgr)
            self.current_frame = frame_num + 1
            progress = int((self.current_frame / total_frames) * 100)
            self.progress.emit(progress)

        out.release()
        self.finished.emit()

    def make_frame(self, t):
        if t == 0:
            remaining = self.duration
        elif t >= self.duration - 1.0 / self.fps:
            remaining = 0
        else:
            remaining = max(self.duration - 1 - int(t), 0)

        mins = remaining // 60
        secs = remaining % 60
        time_str = f"{mins:02}:{secs:02}"

        img = Image.new("RGB", (self.width, self.height), self.bg_color)
        draw = ImageDraw.Draw(img)

        if self.style == "Circle":
            percent = t / self.duration
            start_angle = -90
            end_angle = -90 + 360 * percent

            center_x, center_y = self.width // 2, self.height // 2
            x0 = center_x - self.circle_radius
            y0 = center_y - self.circle_radius
            x1 = center_x + self.circle_radius
            y1 = center_y + self.circle_radius

            draw.arc([x0, y0, x1, y1], start=start_angle, end=end_angle,
                     fill=self.circle_color, width=self.circle_width)

        try:
            font = ImageFont.truetype(self.font_path, self.font_size)
        except OSError:
            font = ImageFont.load_default()

        draw.text((self.width // 2, self.height // 2), time_str,
                  font=font, fill=self.text_color, anchor="mm")

        return np.array(img)

class CountdownApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Countdown Video Generator")
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Left panel for controls
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        # Style selection
        style_layout = QHBoxLayout()
        style_layout.addWidget(QLabel("Style:"))
        self.style_combo = QComboBox()
        self.style_combo.addItems(["Circle", "Digital"])
        style_layout.addWidget(self.style_combo)
        left_layout.addLayout(style_layout)

        # Input controls
        self.width_spin = QSpinBox()
        self.width_spin.setRange(100, 1920)
        self.width_spin.setValue(1920)
        left_layout.addWidget(QLabel("Width:"))
        left_layout.addWidget(self.width_spin)

        self.height_spin = QSpinBox()
        self.height_spin.setRange(100, 1080)
        self.height_spin.setValue(1080)
        left_layout.addWidget(QLabel("Height:"))
        left_layout.addWidget(self.height_spin)

        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(1, 600)
        self.duration_spin.setValue(15)
        left_layout.addWidget(QLabel("Duration (s):"))
        left_layout.addWidget(self.duration_spin)

        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(10, 1000)
        self.font_size_spin.setValue(200)
        left_layout.addWidget(QLabel("Font Size:"))
        left_layout.addWidget(self.font_size_spin)

        self.circle_radius_spin = QSpinBox()
        self.circle_radius_spin.setRange(10, 500)
        self.circle_radius_spin.setValue(450)
        left_layout.addWidget(QLabel("Circle Radius:"))
        left_layout.addWidget(self.circle_radius_spin)

        self.circle_width_spin = QSpinBox()
        self.circle_width_spin.setRange(1, 50)
        self.circle_width_spin.setValue(50)
        left_layout.addWidget(QLabel("Circle Width:"))
        left_layout.addWidget(self.circle_width_spin)

        # Font path with file picker
        font_path_layout = QHBoxLayout()
        font_path_layout.addWidget(QLabel("Font Path:"))
        self.font_path_edit = QLineEdit()
        font_path_layout.addWidget(self.font_path_edit)
        font_browse_button = QPushButton("Browse")
        font_browse_button.clicked.connect(self.select_font)
        font_path_layout.addWidget(font_browse_button)
        left_layout.addLayout(font_path_layout)

        # Color selection buttons
        color_layout = QHBoxLayout()
        self.text_color_button = QPushButton("Text Color")
        self.text_color_button.clicked.connect(self.select_text_color)
        color_layout.addWidget(self.text_color_button)

        self.circle_color_button = QPushButton("Circle Color")
        self.circle_color_button.clicked.connect(self.select_circle_color)
        color_layout.addWidget(self.circle_color_button)

        self.bg_color_button = QPushButton("Background Color")
        self.bg_color_button.clicked.connect(self.select_bg_color)
        color_layout.addWidget(self.bg_color_button)
        left_layout.addLayout(color_layout)

        # Set initial colors
        self.text_color = "white"
        self.circle_color = "white"
        self.bg_color = "black"
        self.update_color_button(self.text_color_button, self.text_color)
        self.update_color_button(self.circle_color_button, self.circle_color)
        self.update_color_button(self.bg_color_button, self.bg_color)

        # Output path input field
        output_path_layout = QHBoxLayout()
        output_path_layout.addWidget(QLabel("Output Path:"))
        self.output_path_edit = QLineEdit()
        default_output = os.path.join(os.path.expanduser('~'), 'Downloads', 'countdown.mp4')
        self.output_path_edit.setText(default_output)
        output_path_layout.addWidget(self.output_path_edit)
        output_browse_button = QPushButton("Browse")
        output_browse_button.clicked.connect(self.select_output_path)
        output_path_layout.addWidget(output_browse_button)
        left_layout.addLayout(output_path_layout)

        # Generate button
        self.generate_button = QPushButton("Generate Video")
        self.generate_button.clicked.connect(self.start_video_generation)
        left_layout.addWidget(self.generate_button)

        # Progress bar
        self.progress_bar = QProgressBar()
        left_layout.addWidget(self.progress_bar)

        left_layout.addStretch()
        main_layout.addWidget(left_panel)

        # Right panel for preview
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        self.preview_label = QLabel()
        self.preview_label.setFixedSize(400, 300)
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.time_label = QLabel("Time: 0.0 s")
        self.preview_slider = QSlider(Qt.Horizontal)
        self.preview_slider.setRange(0, 100)
        self.preview_slider.setValue(50)
        slider_layout = QHBoxLayout()
        slider_layout.addWidget(self.time_label)
        slider_layout.addWidget(self.preview_slider)
        right_layout.addWidget(self.preview_label)
        right_layout.addLayout(slider_layout)
        main_layout.addWidget(right_panel)

        # Connect signals for preview updates
        self.width_spin.valueChanged.connect(self.update_preview)
        self.height_spin.valueChanged.connect(self.update_preview)
        self.duration_spin.valueChanged.connect(self.update_preview)
        self.font_size_spin.valueChanged.connect(self.update_preview)
        self.circle_radius_spin.valueChanged.connect(self.update_preview)
        self.circle_width_spin.valueChanged.connect(self.update_preview)
        self.font_path_edit.textChanged.connect(self.update_preview)
        self.preview_slider.valueChanged.connect(self.update_preview)
        self.style_combo.currentIndexChanged.connect(self.on_style_changed)

        def resource_path(relative_path):
            """Get absolute path to resource (handles PyInstaller temp paths)."""
            try:
                base_path = sys._MEIPASS
            except AttributeError:
                base_path = os.path.abspath(".")
            return os.path.join(base_path, relative_path)

        self.font_dir = resource_path("fonts")
        self.style_combo.setCurrentIndex(0)
        self.on_style_changed(0)

        # Initial preview
        self.update_preview()

    def on_style_changed(self, index):
        style = self.style_combo.currentText()
        if style == "Circle":
            self.font_path_edit.setText(os.path.join(self.font_dir, "Poppins-Black.ttf"))
            self.font_size_spin.setValue(200)
            # enable circle controls
            self.circle_radius_spin.setEnabled(True)
            self.circle_width_spin.setEnabled(True)
        elif style == "Digital":
            self.font_path_edit.setText(os.path.join(self.font_dir, "digital-7.ttf"))
            self.font_size_spin.setValue(400)
            # disable irrelevant controls
            self.circle_radius_spin.setEnabled(False)
            self.circle_width_spin.setEnabled(False)

        self.update_preview()

    def select_font(self):
        font_path, _ = QFileDialog.getOpenFileName(self, "Select Font File", "", "Font Files (*.ttf *.otf)")
        if font_path:
            self.font_path_edit.setText(font_path)

    def select_output_path(self):
        output_path, _ = QFileDialog.getSaveFileName(self, "Save Video As", os.path.join(os.path.expanduser('~'), 'Downloads', 'countdown.mp4'), "MP4 Files (*.mp4)")
        if output_path:
            self.output_path_edit.setText(output_path)

    @staticmethod
    def generate_frame(width, height, t, duration, font_size, circle_radius, circle_width,
                       text_color, circle_color, bg_color, font_path, style):
        remaining = max(duration - int(t), 0)
        mins = remaining // 60
        secs = remaining % 60
        time_str = f"{mins:02}:{secs:02}"

        img = Image.new("RGB", (width, height), bg_color)
        draw = ImageDraw.Draw(img)

        if style == "Circle":
            percent = t / duration
            start_angle = -90
            end_angle = -90 + 360 * percent

            center_x, center_y = width // 2, height // 2
            x0 = center_x - circle_radius
            y0 = center_y - circle_radius
            x1 = center_x + circle_radius
            y1 = center_y + circle_radius

            draw.arc([x0, y0, x1, y1], start=start_angle, end=end_angle,
                     fill=circle_color, width=circle_width)

        try:
            font = ImageFont.truetype(font_path, font_size)
        except OSError:
            font = ImageFont.load_default()

        draw.text((width // 2, height // 2), time_str,
                  font=font, fill=text_color, anchor="mm")

        return np.array(img)

    def update_preview(self):
        width = self.width_spin.value()
        height = self.height_spin.value()
        duration = self.duration_spin.value()
        font_size = self.font_size_spin.value()
        circle_radius = self.circle_radius_spin.value()
        circle_width = self.circle_width_spin.value()
        text_color = self.text_color
        circle_color = self.circle_color
        bg_color = self.bg_color
        font_path = self.font_path_edit.text()
        style = self.style_combo.currentText()

        slider_value = self.preview_slider.value()
        t = (slider_value / 100.0) * duration
        self.time_label.setText(f"Time: {t:.1f} s")

        frame = self.generate_frame(width, height, t, duration, font_size, circle_radius,
                                   circle_width, text_color, circle_color, bg_color, font_path, style)
        qimage = QImage(frame.data, frame.shape[1], frame.shape[0], frame.strides[0],
                        QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimage)
        self.preview_label.setPixmap(pixmap.scaled(self.preview_label.size(), Qt.KeepAspectRatio))

    def select_text_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.text_color = color.name()
            self.update_color_button(self.text_color_button, self.text_color)
            self.update_preview()

    def select_circle_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.circle_color = color.name()
            self.update_color_button(self.circle_color_button, self.circle_color)
            self.update_preview()

    def select_bg_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.bg_color = color.name()
            self.update_color_button(self.bg_color_button, self.bg_color)
            self.update_preview()

    def update_color_button(self, button, color):
        pixmap = QPixmap(20, 20)
        pixmap.fill(QColor(color))
        button.setIcon(QIcon(pixmap))
        button.setIconSize(pixmap.size())

    def start_video_generation(self):
        width = self.width_spin.value()
        height = self.height_spin.value()
        duration = self.duration_spin.value()
        font_size = self.font_size_spin.value()
        circle_radius = self.circle_radius_spin.value()
        circle_width = self.circle_width_spin.value()
        text_color = self.text_color
        circle_color = self.circle_color
        bg_color = self.bg_color
        font_path = self.font_path_edit.text()
        output_path = self.output_path_edit.text()
        style = self.style_combo.currentText()

        self.generator = VideoGenerator(width, height, duration, font_size, circle_radius,
                                        circle_width, text_color, circle_color, bg_color,
                                        font_path, output_path, style)
        self.generator.progress.connect(self.progress_bar.setValue)
        self.generator.finished.connect(self.on_generation_finished)
        self.generate_button.setEnabled(False)
        self.generator.start()

    def on_generation_finished(self):
        self.generate_button.setEnabled(True)
        self.progress_bar.setValue(0)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CountdownApp()
    window.show()
    sys.exit(app.exec_())