import os
import sys
import tempfile
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QSpinBox, QPushButton, QLineEdit, QFileDialog, QSlider, QColorDialog, QMessageBox
)
from PyQt5.QtGui import QPixmap, QImage, QIcon, QColor
from PyQt5.QtCore import Qt
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from moviepy.editor import VideoClip, AudioFileClip
import scipy.io.wavfile

class CountdownApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Countdown Video Generator")
        self.setGeometry(100, 100, 1200, 800)

        # Central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Left panel for inputs
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        # Video size row
        video_size_layout = QHBoxLayout()
        video_size_layout.addWidget(QLabel("Video size:"))
        self.width_spin = QSpinBox()
        self.width_spin.setRange(100, 3840)
        self.width_spin.setValue(1920)
        video_size_layout.addWidget(self.width_spin)
        video_size_layout.addWidget(QLabel("x"))
        self.height_spin = QSpinBox()
        self.height_spin.setRange(100, 3840)
        self.height_spin.setValue(1920)
        video_size_layout.addWidget(self.height_spin)
        left_layout.addLayout(video_size_layout)

        # FPS row
        fps_layout = QHBoxLayout()
        fps_layout.addWidget(QLabel("FPS:"))
        self.fps_spin = QSpinBox()
        self.fps_spin.setRange(1, 60)
        self.fps_spin.setValue(30)
        fps_layout.addWidget(self.fps_spin)
        left_layout.addLayout(fps_layout)

        # Duration row
        duration_layout = QHBoxLayout()
        duration_layout.addWidget(QLabel("Duration (s):"))
        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(1, 3600)
        self.duration_spin.setValue(15)
        duration_layout.addWidget(self.duration_spin)
        left_layout.addLayout(duration_layout)

        # Font size row
        font_size_layout = QHBoxLayout()
        font_size_layout.addWidget(QLabel("Font size:"))
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(10, 1000)
        self.font_size_spin.setValue(280)
        font_size_layout.addWidget(self.font_size_spin)
        left_layout.addLayout(font_size_layout)

        # Circle radius row
        circle_radius_layout = QHBoxLayout()
        circle_radius_layout.addWidget(QLabel("Circle radius:"))
        self.circle_radius_spin = QSpinBox()
        self.circle_radius_spin.setRange(10, 1920)
        self.circle_radius_spin.setValue(700)
        circle_radius_layout.addWidget(self.circle_radius_spin)
        left_layout.addLayout(circle_radius_layout)

        # Circle width row
        circle_width_layout = QHBoxLayout()
        circle_width_layout.addWidget(QLabel("Circle width:"))
        self.circle_width_spin = QSpinBox()
        self.circle_width_spin.setRange(1, 100)
        self.circle_width_spin.setValue(60)
        circle_width_layout.addWidget(self.circle_width_spin)
        left_layout.addLayout(circle_width_layout)

        # Text color row
        text_color_layout = QHBoxLayout()
        text_color_layout.addWidget(QLabel("Text color:"))
        self.text_color_button = QPushButton()
        self.text_color_button.setFixedSize(50, 30)
        self.text_color_button.clicked.connect(self.select_text_color)
        self.text_color = "white"
        self.update_color_button(self.text_color_button, self.text_color)
        text_color_layout.addWidget(self.text_color_button)
        left_layout.addLayout(text_color_layout)

        # Circle color row
        circle_color_layout = QHBoxLayout()
        circle_color_layout.addWidget(QLabel("Circle color:"))
        self.circle_color_button = QPushButton()
        self.circle_color_button.setFixedSize(50, 30)
        self.circle_color_button.clicked.connect(self.select_circle_color)
        self.circle_color = "white"
        self.update_color_button(self.circle_color_button, self.circle_color)
        circle_color_layout.addWidget(self.circle_color_button)
        left_layout.addLayout(circle_color_layout)

        # Background color row
        bg_color_layout = QHBoxLayout()
        bg_color_layout.addWidget(QLabel("Background color:"))
        self.bg_color_button = QPushButton()
        self.bg_color_button.setFixedSize(50, 30)
        self.bg_color_button.clicked.connect(self.select_bg_color)
        self.bg_color = "black"
        self.update_color_button(self.bg_color_button, self.bg_color)
        bg_color_layout.addWidget(self.bg_color_button)
        left_layout.addLayout(bg_color_layout)

        # Font file row
        font_file_layout = QHBoxLayout()
        font_file_layout.addWidget(QLabel("Font file:"))
        self.font_path_edit = QLineEdit()
        self.font_path_edit.setText("/System/Library/Fonts/Poppins-Black.ttf")
        font_file_layout.addWidget(self.font_path_edit)
        browse_font_button = QPushButton("Browse")
        browse_font_button.clicked.connect(self.browse_font)
        font_file_layout.addWidget(browse_font_button)
        left_layout.addLayout(font_file_layout)

        # Output directory row
        output_dir_layout = QHBoxLayout()
        output_dir_layout.addWidget(QLabel("Output directory:"))
        self.output_dir_edit = QLineEdit()
        default_downloads = os.path.join(os.path.expanduser('~'), 'Downloads')
        self.output_dir_edit.setText(default_downloads)
        output_dir_layout.addWidget(self.output_dir_edit)
        browse_output_button = QPushButton("Browse")
        browse_output_button.clicked.connect(self.browse_output_dir)
        output_dir_layout.addWidget(browse_output_button)
        left_layout.addLayout(output_dir_layout)

        # Generate button
        self.generate_button = QPushButton("Generate Video")
        self.generate_button.clicked.connect(self.generate_video)
        left_layout.addWidget(self.generate_button)
        left_layout.addStretch()

        # Right panel for preview
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setFixedSize(400, 400)
        right_layout.addWidget(self.preview_label)
        self.time_slider = QSlider(Qt.Horizontal)
        self.time_slider.setRange(0, 100)
        self.time_slider.setValue(0)
        right_layout.addWidget(self.time_slider)
        right_layout.addStretch()

        # Add panels to main layout
        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel)

        # Connect signals for real-time preview updates
        self.width_spin.valueChanged.connect(self.update_preview)
        self.height_spin.valueChanged.connect(self.update_preview)
        self.fps_spin.valueChanged.connect(self.update_preview)
        self.duration_spin.valueChanged.connect(self.update_preview)
        self.font_size_spin.valueChanged.connect(self.update_preview)
        self.circle_radius_spin.valueChanged.connect(self.update_preview)
        self.circle_width_spin.valueChanged.connect(self.update_preview)
        self.font_path_edit.textChanged.connect(self.update_preview)
        self.time_slider.valueChanged.connect(self.update_preview)

        # Initial preview
        self.update_preview()

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
        pixmap = QPixmap(16, 16)
        pixmap.fill(QColor(color))
        button.setIcon(QIcon(pixmap))
        button.setIconSize(pixmap.size())

    def browse_font(self):
        font_file, _ = QFileDialog.getOpenFileName(self, "Select Font File", "", "Font Files (*.ttf *.otf)")
        if font_file:
            self.font_path_edit.setText(font_file)
            self.update_preview()

    def browse_output_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if dir_path:
            self.output_dir_edit.setText(dir_path)

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
        percentage = self.time_slider.value() / 100.0
        t = percentage * duration

        frame = self.make_frame(t, width, height, duration, font_size, circle_radius, circle_width, text_color, circle_color, bg_color, font_path)
        img = Image.fromarray(frame)
        qimg = QImage(img.tobytes(), img.width, img.height, QImage.Format_RGB888)
        self.preview_label.setPixmap(QPixmap.fromImage(qimg).scaled(self.preview_label.size(), Qt.KeepAspectRatio))

    def make_frame(self, t, width, height, duration, font_size, circle_radius, circle_width, text_color, circle_color, bg_color, font_path):
        if t == 0:
            remaining = duration
        elif t >= duration - 1.0 / self.fps_spin.value():
            remaining = 0
        else:
            remaining = max(duration - 1 - int(t), 0)
        mins = remaining // 60
        secs = remaining % 60
        time_str = f"{mins:02}:{secs:02}"

        img = Image.new("RGB", (width, height), bg_color)
        draw = ImageDraw.Draw(img)

        percent = t / duration
        start_angle = -90
        end_angle = -90 + 360 * percent
        center_x, center_y = width // 2, height // 2
        x0 = center_x - circle_radius
        y0 = center_y - circle_radius
        x1 = center_x + circle_radius
        y1 = center_y + circle_radius
        draw.arc([x0, y0, x1, y1], start=start_angle, end=end_angle, fill=circle_color, width=circle_width)

        try:
            font = ImageFont.truetype(font_path, font_size)
        except OSError:
            font = ImageFont.load_default()
        w, h = draw.textsize(time_str, font=font)
        draw.text((center_x - w // 2, center_y - h // 2), time_str, font=font, fill=text_color)

        return np.array(img)

    def generate_video(self):
        width = self.width_spin.value()
        height = self.height_spin.value()
        fps = self.fps_spin.value()
        duration = self.duration_spin.value()
        font_size = self.font_size_spin.value()
        circle_radius = self.circle_radius_spin.value()
        circle_width = self.circle_width_spin.value()
        text_color = self.text_color
        circle_color = self.circle_color
        bg_color = self.bg_color
        font_path = self.font_path_edit.text()
        output_dir = self.output_dir_edit.text()

        def make_frame(t):
            if t == 0:
                remaining = duration
            elif t >= duration - 1.0 / fps:
                remaining = 0
            else:
                remaining = max(duration - 1 - int(t), 0)
            mins = remaining // 60
            secs = remaining % 60
            time_str = f"{mins:02}:{secs:02}"

            img = Image.new("RGB", (width, height), bg_color)
            draw = ImageDraw.Draw(img)

            percent = t / duration
            start_angle = -90
            end_angle = -90 + 360 * percent
            center_x, center_y = width // 2, height // 2
            x0 = center_x - circle_radius
            y0 = center_y - circle_radius
            x1 = center_x + circle_radius
            y1 = center_y + circle_radius
            draw.arc([x0, y0, x1, y1], start=start_angle, end=end_angle, fill=circle_color, width=circle_width)

            try:
                font = ImageFont.truetype(font_path, font_size)
            except OSError:
                font = ImageFont.load_default()
            w, h = draw.textsize(time_str, font=font)
            draw.text((center_x - w // 2, center_y - h // 2), time_str, font=font, fill=text_color)

            return np.array(img)

        video = VideoClip(make_frame, duration=duration)

        fps_audio = 44100
        beep_duration = 0.1
        beep_freq = 1000
        final_beep_freq = 1500

        t_beep = np.linspace(0, beep_duration, int(fps_audio * beep_duration), endpoint=False)
        beep_audio = np.sin(2 * np.pi * beep_freq * t_beep)
        beep_audio_int16 = np.int16(beep_audio * 32767)
        final_beep_audio = np.sin(2 * np.pi * final_beep_freq * t_beep)
        final_beep_audio_int16 = np.int16(final_beep_audio * 32767)

        start_beep = max(0, duration - 10)
        beep_times = range(start_beep, duration)
        final_beep_time = duration - 1

        total_samples = int(duration * fps_audio)
        audio_array = np.zeros(total_samples, dtype=np.int16)
        beep_length = len(beep_audio_int16)
        for k in beep_times:
            start_sample = int(k * fps_audio)
            end_sample = start_sample + beep_length
            if k == final_beep_time:
                if end_sample <= total_samples:
                    audio_array[start_sample:end_sample] += final_beep_audio_int16
                else:
                    audio_array[start_sample:] += final_beep_audio_int16[:total_samples - start_sample]
            else:
                if end_sample <= total_samples:
                    audio_array[start_sample:end_sample] += beep_audio_int16
                else:
                    audio_array[start_sample:] += beep_audio_int16[:total_samples - start_sample]

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio_wav:
            temp_audio_path = temp_audio_wav.name
            scipy.io.wavfile.write(temp_audio_path, fps_audio, audio_array)
        audio_clip = AudioFileClip(temp_audio_path)
        video = video.set_audio(audio_clip)

        output_filename = os.path.join(output_dir, f"countdown_{duration}s_{width}p.mp4")
        video.write_videofile(output_filename, fps=fps, audio_codec='aac')
        os.remove(temp_audio_path)

        QMessageBox.information(self, "Video Generated", f"Video saved as {output_filename}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CountdownApp()
    window.show()
    sys.exit(app.exec_())