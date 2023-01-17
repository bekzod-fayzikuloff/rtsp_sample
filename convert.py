import os
import sys

from PyQt5 import QtWidgets
from PyQt5.QtCore import QObject, QSize, Qt, QThread, pyqtSignal
from PyQt5.QtGui import QIcon


class Worker(QObject):
    finished = pyqtSignal()

    def __init__(self, input_file, compress_depth, output_file):
        super().__init__()
        self.input_file = input_file
        self.compress_depth = compress_depth
        self.output_file = output_file

    def run(self):
        """Long-running task."""
        print(self.input_file)
        print(self.compress_depth)
        os.system(f"ffmpeg -i {self.input_file} -vcodec libx264 -crf {self.compress_depth} {self.output_file}")
        self.finished.emit()


class UtilitUi(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self._init_ui()

    def _init_ui(self):
        self.setWindowTitle("Video Convert")
        self.setMinimumSize(480, 280)

        self.compress_button = QtWidgets.QPushButton()
        self.compress_button.setText("Compress")
        self.compress_button.clicked.connect(self._compress_video)

        self.hbox_layout = QtWidgets.QHBoxLayout()

        self.hbox_layout.addWidget(self.compress_button)

        self.setLayout(self.hbox_layout)

    def _compress_video(self):
        self.compress_ui = CompressUi()
        self.compress_ui.show()


class CompressUi(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self._init_ui()

    def _init_ui(self):
        self.setWindowTitle("Compress")
        self.setFixedSize(320, 110)

        self.fileBtn = QtWidgets.QPushButton()
        self.compress_slider = QtWidgets.QSlider(Qt.Horizontal)
        self.compress_depth = QtWidgets.QLabel()
        self.output_text = QtWidgets.QLineEdit()

        self.output_text.setPlaceholderText("Output file name...")
        self.output_text.setText("output.mp4")

        self.fileBtn.clicked.connect(self.select_file)
        self.fileBtn.setIcon(QIcon("images/folders.png"))
        self.fileBtn.setIconSize(QSize(20, 20))

        self.compress_slider.setRange(1, 100)
        self.compress_slider.sliderMoved.connect(self.change_compress_depth)
        self.compress_slider.setSliderPosition(24)
        self.compress_depth.setText(f"{self.compress_slider.sliderPosition()}")

        self.hbox = QtWidgets.QHBoxLayout()
        self.vbox = QtWidgets.QVBoxLayout()

        self.hbox.addWidget(self.fileBtn)
        self.hbox.addWidget(self.compress_slider)
        self.hbox.addWidget(self.compress_depth)

        self.vbox.addLayout(self.hbox)
        self.vbox.addWidget(self.output_text)
        self.setLayout(self.vbox)

    def select_file(self):
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(self)

        self.thread = QThread()
        self.worker = Worker(filename, self.compress_slider.sliderPosition(), self.output_text.text())
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

        self.fileBtn.setEnabled(False)
        self.thread.finished.connect(lambda: self.fileBtn.setEnabled(True))

    def change_compress_depth(self):
        self.compress_depth.setText(f"{self.compress_slider.sliderPosition()}")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = UtilitUi()
    window.show()
    sys.exit(app.exec_())
