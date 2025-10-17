from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPixmap
import json
from utils import remove_empty_fields
import os


class SaveController(QWidget):
    def __init__(self, get_data_callback, set_data_callback=None, bids_folder=None):
        super().__init__()
        self.save_button = QPushButton("Save")
        self.is_valid_text = QLabel("Missing required fields")
        self.is_valid_icon = QLabel()
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.curr_file_name = None
        self.get_data = get_data_callback
        self.set_data = set_data_callback
        self.last_dir = bids_folder
        self.init_ui()

    def init_ui(self):
        row = 0
        self.is_valid_icon.setPixmap(QPixmap("Icons/invalid.png"))
        self.is_valid_icon.setFixedWidth(20)

        # Set button name for styling
        self.save_button.setObjectName("saveButton")

        # Create a container with better layout
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(8)

        # Add save button with larger minimum size
        self.save_button.setMinimumHeight(40)
        self.layout.addWidget(self.save_button, row, 0, 1, 1)
        self.layout.addWidget(self.is_valid_icon, row, 1)
        self.layout.addWidget(self.is_valid_text, row, 2)
        self.layout.addItem(QSpacerItem(0, 0), row, 3)

        self.save_button.clicked.connect(self.save)
        self.save_button.setDisabled(True)

    def set_valid(self, valid):
        if valid:
            self.is_valid_icon.setPixmap(QPixmap("Icons/valid.png"))
            self.is_valid_text.setText("Valid")
        else:
            self.is_valid_icon.setPixmap(QPixmap("Icons/invalid.png"))
            self.is_valid_text.setText("Missing required fields")
        self.save_button.setDisabled(not valid)

    def save_data_as_json(self):
        cleaned_data = remove_empty_fields(self.get_data())
        f_path = os.path.join(self.last_dir, "dataset_description.json")
        with open(f_path, "w", encoding="utf-8") as f:
            json.dump(cleaned_data, f, indent=4, ensure_ascii=False)

    def load_data(self, folder_path):
        """
        Load dataset_description.json from the specified BIDS folder
        :param folder_path: path to the BIDS folder
        :return:
        """
        try:
            f_path = os.path.join(folder_path, "dataset_description.json")
            if not os.path.exists(f_path):
                QMessageBox.warning(
                    self, "File Not Found", f"dataset_description.json not found in {folder_path}"
                )
                return False

            with open(f_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if self.set_data:
                self.set_data(data)

            self.last_dir = folder_path
            return True
        except Exception as e:
            QMessageBox.critical(
                self, "Error Loading File", f"Failed to load dataset_description.json: {str(e)}"
            )
            return False

    def save(self):
        if self.last_dir:
            kwargs = {"caption": "Select Directory", "directory": self.last_dir}
        else:
            kwargs = {"caption": "Select Directory"}
        file = str(QFileDialog.getExistingDirectory(**kwargs))
        if file == "":
            return
        self.last_dir = file
        self.save_data_as_json()
