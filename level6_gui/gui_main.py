import sys
import os

# 1) Add the project root directory to sys.path
current_dir = os.path.dirname(os.path.realpath(__file__))  # Get the current script directory
project_root = os.path.dirname(current_dir)  # Move up to the project root directory
if project_root not in sys.path:
    sys.path.append(project_root)  # Add project root to sys.path for module imports

try:
    from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLineEdit, QLabel, QFileDialog, QTextEdit, QComboBox, QWidget, QVBoxLayout, QHBoxLayout
except ImportError:
    print("PyQt5 is not installed! Install it using 'pip install pyqt5'.")
    sys.exit(1)

# 2) Attempt to import Level 1–5 modules
try:
    # level1_text_compression/LZW.py -> class LZWCoding
    from level1_text_compression.LZW import LZWCoding as LZWTextCoding
except ImportError:
    LZWTextCoding = None

try:
    # level2_gray_image/LZW_gray.py -> class LZWGrayCoding
    from level2_gray_image.LZW_gray import LZWGrayCoding
except ImportError:
    LZWGrayCoding = None

try:
    # level3_gray_differences/LZW_gray_diff.py -> class LZWGrayDiffCoding
    from level3_gray_differences.LZW_gray_diff import LZWGrayDiffCoding
except ImportError:
    LZWGrayDiffCoding = None

try:
    # level4_color_image/LZW_color.py -> class LZWColorCoding
    from level4_color_image.LZW_color import LZWColorCoding
except ImportError:
    LZWColorCoding = None

try:
    # level5_color_differences/LZW_color_diff.py -> class LZWColorDiffCoding
    from level5_color_differences.LZW_color_diff import LZWColorDiffCoding
except ImportError:
    LZWColorDiffCoding = None


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LZW Compression GUI - PyQt")

        # Create the main widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # File selection UI
        file_layout = QHBoxLayout()
        main_layout.addLayout(file_layout)

        self.file_edit = QLineEdit()
        browse_btn = QPushButton("Browse")

        file_layout.addWidget(QLabel("Select File:"))
        file_layout.addWidget(self.file_edit)
        file_layout.addWidget(browse_btn)

        browse_btn.clicked.connect(self.browse_file)

        # Compression level selection UI
        level_layout = QHBoxLayout()
        main_layout.addLayout(level_layout)

        level_layout.addWidget(QLabel("Select Method/Level:"))
        self.level_combo = QComboBox()
        self.level_combo.addItems([
            "Text (Level1)",
            "Gray (Level2)",
            "Gray Diff (Level3)",
            "Color (Level4)",
            "Color Diff (Level5)"
        ])
        level_layout.addWidget(self.level_combo)

        # Buttons for compression and decompression
        btn_layout = QHBoxLayout()
        main_layout.addLayout(btn_layout)

        compress_btn = QPushButton("Compress")
        decompress_btn = QPushButton("Decompress")
        btn_layout.addWidget(compress_btn)
        btn_layout.addWidget(decompress_btn)

        compress_btn.clicked.connect(self.do_compress)
        decompress_btn.clicked.connect(self.do_decompress)

        # Log output area
        self.log_text = QTextEdit()
        main_layout.addWidget(self.log_text)

    def browse_file(self):
        """ Open a file dialog to select a file. """
        path, _ = QFileDialog.getOpenFileName(self, "Select a file", "", "All Files (*.*)")
        if path:
            self.file_edit.setText(path)

    def do_compress(self):
        """ Perform file compression based on the selected method. """
        filepath = self.file_edit.text().strip()
        if not os.path.isfile(filepath):
            self.log("File not found!")
            return

        method = self.level_combo.currentText()
        self.log(f"[Compress] File: {filepath}, Method: {method}")

        base_name, ext = os.path.splitext(os.path.basename(filepath))

        if "Text (Level1)" in method and LZWTextCoding:
            coder = LZWTextCoding(base_name, data_type="text")
            out = coder.compress_text_file()
            self.log(f"Text compression successful => {out}")
        elif "Gray (Level2)" in method and LZWGrayCoding:
            coder = LZWGrayCoding(base_name)
            out = coder.compress_image_file()
            self.log(f"Gray image compression successful => {out}")
        elif "Gray Diff (Level3)" in method and LZWGrayDiffCoding:
            coder = LZWGrayDiffCoding(base_name)
            out = coder.compress_image_file()
            self.log(f"Gray Diff compression successful => {out}")
        elif "Color (Level4)" in method and LZWColorCoding:
            coder = LZWColorCoding(base_name)
            out = coder.compress_image_file()
            self.log(f"Color image compression successful => {out}")
        elif "Color Diff (Level5)" in method and LZWColorDiffCoding:
            coder = LZWColorDiffCoding(base_name)
            out = coder.compress_image_file()
            self.log(f"Color Diff compression successful => {out}")
        else:
            self.log("This level module was not found or could not be imported!")

    def do_decompress(self):
        """ Perform file decompression based on the selected method. """
        filepath = self.file_edit.text().strip()
        if not os.path.isfile(filepath):
            self.log("File not found!")
            return

        method = self.level_combo.currentText()
        self.log(f"[Decompress] File: {filepath}, Method: {method}")

        base_name, ext = os.path.splitext(os.path.basename(filepath))

        if "Text (Level1)" in method and LZWTextCoding:
            coder = LZWTextCoding(base_name, data_type="text")
            out = coder.decompress_text_file()
            self.log(f"Text decompression successful => {out}")
        elif "Gray (Level2)" in method and LZWGrayCoding:
            coder = LZWGrayCoding(base_name)
            out = coder.decompress_image_file()
            self.log(f"Gray image decompression successful => {out}")
        elif "Gray Diff (Level3)" in method and LZWGrayDiffCoding:
            coder = LZWGrayDiffCoding(base_name)
            out = coder.decompress_image_file()
            self.log(f"Gray Diff decompression successful => {out}")
        elif "Color (Level4)" in method and LZWColorCoding:
            coder = LZWColorCoding(base_name)
            out = coder.decompress_image_file()
            self.log(f"Color image decompression successful => {out}")
        elif "Color Diff (Level5)" in method and LZWColorDiffCoding:
            coder = LZWColorDiffCoding(base_name)
            out = coder.decompress_image_file()
            self.log(f"Color Diff decompression successful => {out}")
        else:
            self.log("This level module was not found or could not be imported!")

    def log(self, msg):
        """ Display a message in the log output area. """
        self.log_text.append(msg)


def main():
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()