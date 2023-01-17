import os
import sys

from PyQt5 import QtWidgets
from PyQt5.QtCore import QObject, QSize, Qt, QThread, pyqtSignal
from PyQt5.QtGui import QIcon


class CompressWorker(QObject):
    finished = pyqtSignal()

    def __init__(self, input_file, compress_depth, output_file) -> None:
        super().__init__()
        self.input_file = input_file
        self.compress_depth = compress_depth
        self.output_file = output_file

    def run(self) -> None:
        """Long-running task(compress file)."""
        os.system(f"ffmpeg -i {self.input_file} -vcodec libx264 -crf {self.compress_depth} {self.output_file}")
        self.finished.emit()


class ConvertWorker(QObject):
    finished = pyqtSignal()

    def __init__(self, input_file, extension, output_file) -> None:
        super().__init__()
        self.input_file = input_file
        self.extension = extension
        self.output_file = output_file

    def run(self) -> None:
        """Long-running task(convert file)."""
        os.system(f"ffmpeg -i {self.input_file} {self.output_file}.{self.extension}")
        self.finished.emit()


class UtilitUi(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self._init_ui()

    def _init_ui(self) -> None:
        """Main window ui initialize"""
        self.setWindowTitle("Video Convert")
        self.setMinimumSize(280, 80)

        self.compress_button = QtWidgets.QPushButton()
        self.compress_button.setText("Compress")
        self.compress_button.clicked.connect(self._compress_video)
        self.compress_button.setStyleSheet("border: none; background-color: silver; height: 20px")

        self.convert_button = QtWidgets.QPushButton()
        self.convert_button.setText("Convert")
        self.convert_button.clicked.connect(self._convert_video)
        self.convert_button.setStyleSheet("border: none; background-color: silver; height: 20px")

        self.vbox_layout = QtWidgets.QVBoxLayout()

        self.vbox_layout.addWidget(self.compress_button)
        self.vbox_layout.addWidget(self.convert_button)

        self.setLayout(self.vbox_layout)

    def _compress_video(self) -> None:
        self.compress_ui = CompressUi()
        self.compress_ui.show()

    def _convert_video(self) -> None:
        self.convert_ui = ConvertUi()
        self.convert_ui.show()


class CompressUi(QtWidgets.QWidget):
    def __init__(self) -> None:
        super().__init__()
        self._init_ui()

    def _init_ui(self) -> None:
        """Compress window ui initialize"""
        self.setWindowTitle("Compress")
        self.setFixedSize(320, 110)
        self.setStyleSheet("background-color: #3C3F41;")

        self.fileBtn = QtWidgets.QPushButton()
        self.compress_slider = QtWidgets.QSlider(Qt.Horizontal)
        self.compress_depth = QtWidgets.QLabel()
        self.output_text = QtWidgets.QLineEdit()

        self.output_text.setPlaceholderText("Output file name...")
        self.output_text.setText("output.mp4")
        self.output_text.setStyleSheet("color: white;")

        self.fileBtn.clicked.connect(self.select_file)
        self.fileBtn.setIcon(QIcon("images/folders.png"))
        self.fileBtn.setIconSize(QSize(20, 20))
        self.fileBtn.setStyleSheet("border: none;")

        self.compress_slider.setRange(1, 100)
        self.compress_slider.setStyleSheet(
            """
               QSlider::groove:horizontal {
                   border-radius: 1px;       
                   height: 6px;              
                   margin: -1px 0;           
               }
               QSlider::handle:horizontal {
                   background-color: #98A798;
                   border: 2px solid silver;
                   height: 16px;     
                   width: 10px;
                   margin: -4px 0;     
                   border-radius: 7px  ;
                   padding: -4px 0px;  
               }
               QSlider::add-page:horizontal {
                   background: #A6A6A6;
               }
               QSlider::sub-page:horizontal {
                   background: #272A32;
               }
               """
        )

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

    def select_file(self) -> None:
        """Compress file method in thread (not freeze ui)"""
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(self)

        self.thread = QThread()
        self.worker = CompressWorker(filename, self.compress_slider.sliderPosition(), self.output_text.text())
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

        self.fileBtn.setEnabled(False)
        self.thread.finished.connect(lambda: self.fileBtn.setEnabled(True))

    def change_compress_depth(self) -> None:
        self.compress_depth.setText(f"{self.compress_slider.sliderPosition()}")


class ConvertUi(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self._init_ui()

    def _init_ui(self):
        """Convert window ui initialize"""
        self.setWindowTitle("Convert")
        self.setFixedSize(320, 110)
        self.setStyleSheet("background-color: #3C3F41;")

        self.fileBtn = QtWidgets.QPushButton()
        self.output_text = QtWidgets.QLineEdit()
        self.ext_select = QtWidgets.QComboBox()

        self.fileBtn.clicked.connect(self.select_file)
        self.fileBtn.setIcon(QIcon("images/folders.png"))
        self.fileBtn.setIconSize(QSize(20, 20))
        self.fileBtn.setStyleSheet("border: none;")

        self.output_text.setPlaceholderText("Output file name...")
        self.output_text.setText("output")
        self.output_text.setStyleSheet("background-color: white;")

        self.ext_select.addItems(["mp4", "avi", "mkv", "mov"])
        self.ext_select.setStyleSheet("background-color: white;")

        self.hbox = QtWidgets.QHBoxLayout()
        self.hbox.addWidget(self.fileBtn)
        self.hbox.addWidget(self.output_text)
        self.hbox.addWidget(self.ext_select)

        self.setLayout(self.hbox)

    def select_file(self):
        """Convert file method in thread (not freeze ui)"""
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(self)

        self.thread = QThread()
        self.convert_worker = ConvertWorker(filename, self.ext_select.currentText(), self.output_text.text())
        self.convert_worker.moveToThread(self.thread)

        self.thread.started.connect(self.convert_worker.run)
        self.convert_worker.finished.connect(self.thread.quit)
        self.convert_worker.finished.connect(self.convert_worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

        self.fileBtn.setEnabled(False)
        self.thread.finished.connect(lambda: self.fileBtn.setEnabled(True))


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = UtilitUi()
    window.show()
    sys.exit(app.exec_())
