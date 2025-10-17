from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSignal as Signal
from utils import new_line_edit, new_text_edit, HLine
import tooltips as tt


class Derivative(QWidget):
    """
    this widget has fields relevant to a dataset description of type derivative,
    it is a logical extension to the form.
    """

    modified = Signal()

    def __init__(self):
        super().__init__()
        self.state_change_cb = None

        # main layout and sub layouts (for dynamic field insertion)
        self.main_layout = QGridLayout()
        self.gen_by_layout = QVBoxLayout()
        self.src_data_layout = QVBoxLayout()

        # lists of widgets for dynamically added (and subtracted) fields
        self.gen_by_ls = []
        self.src_data_ls = []

        # UI setup
        self.setLayout(self.main_layout)
        self.init_ui()
        self.add_gen_by()

    def init_ui(self):
        """
        Initialize UI components.
        Naming conventions for the labels are taken from official BIDS
        specification (v1.4.0).
        :return:
        """
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        row = 0  # for main layout row count

        # section separation line
        h_line = HLine()
        self.main_layout.addWidget(h_line, row, 0, 1, -1)
        row += 1

        # GeneratedBy control
        gen_by_label = QLabel("GeneratedBy")
        gen_by_label.setToolTip(tt.generated_by)
        gen_by_add_button = QPushButton("+")
        gen_by_add_button.clicked.connect(self.add_gen_by)
        gen_by_remove_button = QPushButton("-")
        gen_by_remove_button.clicked.connect(self.remove_gen_by)
        self.main_layout.addWidget(gen_by_label, row, 0)
        self.main_layout.addWidget(gen_by_remove_button, row, 1)
        self.main_layout.addWidget(gen_by_add_button, row, 2)
        row += 1

        # GeneratedBy fields
        self.main_layout.addLayout(self.gen_by_layout, row, 0, 1, -1)
        row += 1

        # SourceDatasets control
        src_data_label = QLabel("SourceDatasets")
        src_data_label.setToolTip(tt.sources_datasets)
        src_data_add_button = QPushButton("+")
        src_data_add_button.clicked.connect(self.add_src_data)
        src_data_remove_button = QPushButton("-")
        src_data_remove_button.clicked.connect(self.remove_src_data)
        self.main_layout.addWidget(src_data_label, row, 0)
        self.main_layout.addWidget(src_data_remove_button, row, 1)
        self.main_layout.addWidget(src_data_add_button, row, 2)
        row += 1

        # DataSources fields
        self.main_layout.addLayout(self.src_data_layout, row, 0, 1, -1)
        row += 1

        # spacer and stretch to push content to top left
        self.main_layout.addItem(QSpacerItem(0, 0), 0, 3, -1, 1)
        self.main_layout.setRowStretch(row, 1)
        self.main_layout.setColumnStretch(3, 1)

    def add_gen_by(self):
        """
        add a GeneratedBy section to layout
        :return:
        """
        gen_by = GeneratedBy()
        gen_by.modified.connect(self.modified.emit)
        self.gen_by_layout.addWidget(gen_by)
        self.gen_by_ls.append(gen_by)
        self.modified.emit()

    def remove_gen_by(self):
        """
        remove the last GeneratedBy section from layout.
        there is a requirement to have at least one GeneratedBy section if class
        is initiated, therefore remove won't work if there is a single instance
        of GeneratedBy section
        :return:
        """
        if len(self.gen_by_ls) == 1:
            return
        self.gen_by_layout.removeWidget(self.gen_by_ls[-1])
        self.gen_by_ls[-1].deleteLater()
        self.gen_by_ls = self.gen_by_ls[:-1]
        self.modified.emit()

    def add_src_data(self):
        """
        add a SourceDatasets section to layout
        :return:
        """
        src_data = SourceDatasets()
        src_data.modified.connect(self.modified.emit)
        self.src_data_layout.addWidget(src_data)
        self.src_data_ls.append(src_data)
        self.modified.emit()

    def remove_src_data(self):
        """
        remove the last SourceDatasets section from layout
        :return:
        """
        if len(self.src_data_ls) == 0:
            return
        self.src_data_layout.removeWidget(self.src_data_ls[-1])
        self.src_data_ls[-1].deleteLater()
        self.src_data_ls = self.src_data_ls[:-1]
        self.modified.emit()

    def get_data(self):
        """
        get relevant data from the user filled fields
        :return:
        """
        gen_by_data_ls = []
        src_data_data_ls = []
        for i in self.gen_by_ls:
            gen_by_data_ls.append(i.get_data())
        for i in self.src_data_ls:
            src_data_data_ls.append(i.get_data())
        data = {"GeneratedBy": gen_by_data_ls, "SourceDatasets": src_data_data_ls}
        return data

    def set_data(self, data):
        """
        populate derivative fields from provided data dictionary
        :param data: dict with GeneratedBy and SourceDatasets information
        :return:
        """
        # Clear existing items
        while len(self.gen_by_ls) > 0:
            self.gen_by_layout.removeWidget(self.gen_by_ls[-1])
            self.gen_by_ls[-1].deleteLater()
            self.gen_by_ls = self.gen_by_ls[:-1]

        while len(self.src_data_ls) > 0:
            self.src_data_layout.removeWidget(self.src_data_ls[-1])
            self.src_data_ls[-1].deleteLater()
            self.src_data_ls = self.src_data_ls[:-1]

        # Load GeneratedBy data
        if "GeneratedBy" in data:
            for gen_by_item in data["GeneratedBy"]:
                gen_by = GeneratedBy()
                gen_by.modified.connect(self.modified.emit)
                gen_by.set_data(gen_by_item)
                self.gen_by_ls.append(gen_by)
                self.gen_by_layout.addWidget(gen_by)
        else:
            # Add at least one GeneratedBy item
            self.add_gen_by()

        # Load SourceDatasets data
        if "SourceDatasets" in data:
            for src_data_item in data["SourceDatasets"]:
                src_data = SourceDatasets()
                src_data.modified.connect(self.modified.emit)
                src_data.set_data(src_data_item)
                self.src_data_ls.append(src_data)
                self.src_data_layout.addWidget(src_data)

        self.modified.emit()


class GeneratedBy(QWidget):
    modified = Signal()

    def __init__(self):
        super().__init__()

        # static widgets with stored user input data
        self.name_value = None
        self.version_value = None
        self.desc_value = None
        self.url_value = None
        self.cont_type_value = None
        self.cont_tag_value = None
        self.cont_uri_value = None

        # UI setup
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.init_ui()

    def init_ui(self):
        self.layout.setContentsMargins(0, 0, 0, 0)
        row = 0

        # Name
        name_label = QLabel("Name")
        name_label.setToolTip(tt.gen_name)
        self.name_value = new_line_edit(self.modified.emit)
        self.name_value.setPlaceholderText("Required")
        self.layout.addWidget(name_label, row, 0)
        self.layout.addWidget(self.name_value, row, 1, 1, -1)
        row += 1

        # Version
        version_label = QLabel("Version")
        version_label.setToolTip(tt.gen_version)
        self.version_value = new_line_edit(self.modified.emit)
        self.layout.addWidget(version_label, row, 0)
        self.layout.addWidget(self.version_value, row, 1, 1, -1)
        row += 1

        # Description
        desc_label = QLabel("Description")
        desc_label.setToolTip(tt.gen_description)
        self.desc_value = new_text_edit(self.modified.emit)
        self.desc_value.setFixedHeight(80)
        self.layout.addWidget(desc_label, row, 0)
        row += 1
        self.layout.addWidget(self.desc_value, row, 0, 1, -1)
        row += 1

        # CodeURL
        url_label = QLabel("CodeURL")
        url_label.setToolTip(tt.gen_code_url)
        self.url_value = new_line_edit(self.modified.emit)
        self.layout.addWidget(url_label, row, 0)
        self.layout.addWidget(self.url_value, row, 1, 1, -1)
        row += 1

        # Container
        cont_label = QLabel("Container")
        cont_label.setToolTip(tt.gen_container)
        self.layout.addWidget(cont_label, row, 0)
        row += 1

        cont_type_label = QLabel("Type")
        self.cont_type_value = new_line_edit(self.modified.emit)
        self.layout.addWidget(cont_type_label, row, 1)
        self.layout.addWidget(self.cont_type_value, row, 2, 1, -1)
        row += 1

        cont_tag_label = QLabel("Tag")
        self.cont_tag_value = new_line_edit(self.modified.emit)
        self.layout.addWidget(cont_tag_label, row, 1)
        self.layout.addWidget(self.cont_tag_value, row, 2, 1, -1)
        row += 1

        cont_uri_label = QLabel("URI")
        self.cont_uri_value = new_line_edit(self.modified.emit)
        self.layout.addWidget(cont_uri_label, row, 1)
        self.layout.addWidget(self.cont_uri_value, row, 2, 1, -1)
        row += 1

        # separator line
        h_line = HLine()
        self.layout.addWidget(h_line, row, 1, 1, -1)
        row += 1

        # spacer to push content to top
        self.layout.addItem(QSpacerItem(0, 0), row, 0, 2, -1)

    def get_data(self):
        """
        get relevant data from the user filled fields
        :return:
        """
        data = {
            "Name": self.name_value.text(),
            "Version": self.version_value.text(),
            "Description": self.desc_value.toPlainText(),
            "CodeURL": self.url_value.text(),
            "Container": {
                "Type": self.cont_type_value.text(),
                "Tag": self.cont_tag_value.text(),
                "URI": self.cont_uri_value.text(),
            },
        }
        return data

    def set_data(self, data):
        """
        populate fields from provided data dictionary
        :param data: dict with GeneratedBy information
        :return:
        """
        if "Name" in data:
            self.name_value.setText(data.get("Name", ""))
        if "Version" in data:
            self.version_value.setText(data.get("Version", ""))
        if "Description" in data:
            self.desc_value.setPlainText(data.get("Description", ""))
        if "CodeURL" in data:
            self.url_value.setText(data.get("CodeURL", ""))
        if "Container" in data:
            container = data["Container"]
            self.cont_type_value.setText(container.get("Type", ""))
            self.cont_tag_value.setText(container.get("Tag", ""))
            self.cont_uri_value.setText(container.get("URI", ""))


class SourceDatasets(QWidget):
    modified = Signal()

    def __init__(self):
        super().__init__()

        # static widgets with stored user input data
        self.doi_value = None
        self.url_value = None
        self.version_value = None

        # UI setup
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.init_ui()

    def init_ui(self):
        self.layout.setContentsMargins(0, 0, 0, 0)
        row = 0

        # DOI
        doi_label = QLabel("DOI")
        self.doi_value = new_line_edit(self.modified.emit)
        self.layout.addWidget(doi_label, row, 0)
        self.layout.addWidget(self.doi_value, row, 1, 1, -1)
        row += 1

        # URL
        url_label = QLabel("URL")
        self.url_value = new_line_edit(self.modified.emit)
        self.layout.addWidget(url_label, row, 0)
        self.layout.addWidget(self.url_value, row, 1, 1, -1)
        row += 1

        # Version
        version_label = QLabel("Version")
        self.version_value = new_line_edit(self.modified.emit)
        self.layout.addWidget(version_label, row, 0)
        self.layout.addWidget(self.version_value, row, 1, 1, -1)
        row += 1

        # separator line
        h_line = HLine()
        self.layout.addWidget(h_line, row, 1, 1, -1)
        row += 1

        # spacer to push content to top
        self.layout.addItem(QSpacerItem(0, 0), row, 0, 2, -1)

    def get_data(self):
        """
        get relevant data from the user filled fields
        :return:
        """
        data = {
            "DOI": self.doi_value.text(),
            "URL": self.url_value.text(),
            "Version": self.version_value.text(),
        }
        return data

    def set_data(self, data):
        """
        populate fields from provided data dictionary
        :param data: dict with SourceDatasets information
        :return:
        """
        self.doi_value.setText(data.get("DOI", ""))
        self.url_value.setText(data.get("URL", ""))
        self.version_value.setText(data.get("Version", ""))
