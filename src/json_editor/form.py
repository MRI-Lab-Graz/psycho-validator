from PyQt5.QtCore import pyqtSignal as Signal
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from form_derivative import Derivative
from utils import new_line_edit, new_text_edit, new_combo_box
import tooltips as tt


class FormScroll(QScrollArea):
    """
    variation of the form widget in a scroll area
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form = Form()
        self.setWidget(self.form)
        self.setWidgetResizable(True)


class Form(QWidget):
    """
    this is the root form, all the fields to be filled by the user are on this
    level, or in widgets instantiated in this class.
    """

    # all required fields of the form should emit the 'modified' signal
    modified = Signal()

    def __init__(self):
        super().__init__()

        # static widgets with stored user input data
        self.derivative = None
        self.name_value = None
        self.bids_ver_value = None
        self.data_type_value = None
        self.license_value = None
        self.ack_value = None
        self.how_to_ack_value = None
        self.doi_value = None
        self.curr_saved_label = None
        self.save_button = None
        self.is_valid_text = None
        self.is_valid_icon = None

        # main layout and sub layouts (for dynamic field insertion).
        # layouts author, funding, ethics and ref are for dynamically added
        # fields in the main layout.
        # layout derivative is for toggled BIDS derivative related fields.
        self.main_layout = QGridLayout()
        self.author_layout = QVBoxLayout()
        self.funding_layout = QVBoxLayout()
        self.ethics_layout = QVBoxLayout()
        self.ref_layout = QVBoxLayout()
        self.derivative_layout = QGridLayout()
        self.src_data_layout = QGridLayout()
        self.gen_by_layout = QVBoxLayout()

        # lists of widgets for dynamically added (and subtracted) fields
        self.ref_ls = []
        self.ethics_ls = []
        self.funding_ls = []
        self.author_ls = []
        self.gen_by_ls = []

        # UI setup
        self.init_ui()
        self.setLayout(self.main_layout)

    def init_ui(self):
        """
        Initialize UI components.
        Naming conventions for the labels are taken from official BIDS
        specification (v1.4.0).
        :return:
        """
        row = 0  # for main layout row count
        # set stretch to enforce last column take available space
        self.main_layout.setColumnStretch(4, 1)

        # Name (Dataset name)
        name_label = QLabel("Name")
        name_label.setToolTip(tt.name)
        self.name_value = new_line_edit(self.modified.emit)
        self.name_value.setPlaceholderText("Required")
        self.main_layout.addWidget(name_label, row, 0)
        self.main_layout.addWidget(self.name_value, row, 1, 1, 4)
        row += 1

        # BIDSVersion
        bids_ver_label = QLabel("BIDSVersion")
        bids_ver_label.setToolTip(tt.bids_version)
        self.bids_ver_value = QComboBox()
        self.bids_ver_value.addItems(["1.4.0"])
        self.bids_ver_value.setDisabled(True)  # to be modified in the future
        self.main_layout.addWidget(bids_ver_label, row, 0)
        self.main_layout.addWidget(self.bids_ver_value, row, 1, 1, 4)
        row += 1

        # DatasetType
        data_type_label = QLabel("DatasetType")
        data_type_label.setToolTip(tt.dataset_type)
        self.data_type_value = QComboBox()
        self.data_type_value.addItems(["unspecified", "raw", "derivative"])
        self.data_type_value.currentIndexChanged.connect(self.dataset_type_handler)
        self.main_layout.addWidget(data_type_label, row, 0)
        self.main_layout.addWidget(self.data_type_value, row, 1, 1, 4)
        row += 1

        # License
        license_label = QLabel("License")
        license_label.setToolTip(tt.dataset_license)
        self.license_value = new_combo_box(self.modified.emit)
        self.license_value.addItems(["unspecified", "PD", "PDDL", "CC0"])
        self.license_value.setItemData(1, tt.license_pd, Qt.ToolTipRole)
        self.license_value.setItemData(2, tt.license_pddl, Qt.ToolTipRole)
        self.license_value.setItemData(3, tt.license_cc0, Qt.ToolTipRole)
        self.main_layout.addWidget(license_label, row, 0)
        self.main_layout.addWidget(self.license_value, row, 1, 1, 4)
        row += 1

        # Authors
        author_label = QLabel("Author")
        author_label.setToolTip(tt.authors)
        author_button_add = QPushButton("+")
        author_button_add.clicked.connect(self.add_author)
        author_button_remove = QPushButton("-")
        author_button_remove.clicked.connect(self.remove_author)
        self.main_layout.addWidget(author_label, row, 0)
        self.main_layout.addWidget(author_button_remove, row, 1)
        self.main_layout.addWidget(author_button_add, row, 2)
        row += 1
        self.main_layout.addLayout(self.author_layout, row, 0, 1, -1)
        row += 1

        # Acknowledgements
        ack_label = QLabel("Acknowledgements")
        ack_label.setToolTip(tt.acknowledgements)
        self.ack_value = new_text_edit(self.modified.emit)
        self.ack_value.setFixedHeight(80)
        self.main_layout.addWidget(ack_label, row, 0)
        row += 1
        self.main_layout.addWidget(self.ack_value, row, 0, 1, -1)
        row += 1

        # HowToAcknowledge
        how_to_ack_label = QLabel("HowToAcknowledge")
        how_to_ack_label.setToolTip(tt.how_to_ack)
        self.how_to_ack_value = new_text_edit(self.modified.emit)
        self.how_to_ack_value.setFixedHeight(80)
        self.main_layout.addWidget(how_to_ack_label, row, 0)
        row += 1
        self.main_layout.addWidget(self.how_to_ack_value, row, 0, 1, -1)
        row += 1

        # Funding
        funding_label = QLabel("Funding")
        funding_label.setToolTip(tt.funding)
        funding_button_add = QPushButton("+")
        funding_button_add.clicked.connect(self.add_funding)
        funding_button_remove = QPushButton("-")
        funding_button_remove.clicked.connect(self.remove_funding)
        self.main_layout.addWidget(funding_label, row, 0)
        self.main_layout.addWidget(funding_button_remove, row, 1)
        self.main_layout.addWidget(funding_button_add, row, 2)
        row += 1
        self.main_layout.addLayout(self.funding_layout, row, 0, 1, -1)
        row += 1

        # EthicsApprovals
        ethics_label = QLabel("EthicsApprovals")
        ethics_label.setToolTip(tt.ethics_approval)
        ethics_button_add = QPushButton("+")
        ethics_button_add.clicked.connect(self.add_ethics)
        ethics_button_remove = QPushButton("-")
        ethics_button_remove.clicked.connect(self.remove_ethics)
        self.main_layout.addWidget(ethics_label, row, 0)
        self.main_layout.addWidget(ethics_button_remove, row, 1)
        self.main_layout.addWidget(ethics_button_add, row, 2)
        row += 1
        self.main_layout.addLayout(self.ethics_layout, row, 0, 1, -1)
        row += 1

        # ReferencesAndLinks
        ref_label = QLabel("ReferencesAndLinks")
        ref_label.setToolTip(tt.ref_and_links)
        ref_button_add = QPushButton("+")
        ref_button_add.clicked.connect(self.add_ref)
        ref_button_remove = QPushButton("-")
        ref_button_remove.clicked.connect(self.remove_ref)
        self.main_layout.addWidget(ref_label, row, 0)
        self.main_layout.addWidget(ref_button_remove, row, 1)
        self.main_layout.addWidget(ref_button_add, row, 2)
        row += 1
        self.main_layout.addLayout(self.ref_layout, row, 0, 1, -1)
        row += 1

        # DatasetDOI
        doi_label = QLabel("DatasetDOI")
        doi_label.setToolTip(tt.dataset_doi)
        self.doi_value = new_line_edit(self.modified.emit)
        self.main_layout.addWidget(doi_label, row, 0)
        self.main_layout.addWidget(self.doi_value, row, 1, 1, -1)
        row += 1

        # Derivative sections (fields dynamically added to layout)
        self.main_layout.addLayout(self.derivative_layout, row, 0, 1, -1)
        row += 1

        # spacer item to push content to top
        self.main_layout.addItem(QSpacerItem(0, 0), row, 0, 2, -1)
        col_count = self.main_layout.columnCount()
        self.main_layout.setColumnStretch(col_count - 1, 1)

    def add_author(self):
        """
        adds line edit to the layout (under Author)
        :return:
        """
        line = new_line_edit(self.modified.emit)
        self.author_ls.append(line)
        self.author_layout.addWidget(line)

    def remove_author(self):
        """
        removes the last line edit from layout (under Author)
        :return:
        """
        if len(self.author_ls) == 0:
            return
        self.author_layout.removeWidget(self.author_ls[-1])
        self.author_ls[-1].deleteLater()
        self.author_ls = self.author_ls[:-1]

    def add_funding(self):
        """
        adds line edit to the layout (under Funding)
        :return:
        """
        line = new_line_edit(self.modified.emit)
        self.funding_ls.append(line)
        self.funding_layout.addWidget(line)

    def remove_funding(self):
        """
        removes the last line edit from layout (under Funding)
        :return:
        """
        if len(self.funding_ls) == 0:
            return
        self.funding_layout.removeWidget(self.funding_ls[-1])
        self.funding_ls[-1].deleteLater()
        self.funding_ls = self.funding_ls[:-1]

    def add_ethics(self):
        """
        adds line edit to the layout (under EthicsApprovals)
        :return:
        """
        line = new_line_edit(self.modified.emit)
        self.ethics_ls.append(line)
        self.ethics_layout.addWidget(line)

    def remove_ethics(self):
        """
        removes the last line edit from layout (under EthicsApprovals)
        :return:
        """
        if len(self.ethics_ls) == 0:
            return
        self.ethics_layout.removeWidget(self.ethics_ls[-1])
        self.ethics_ls[-1].deleteLater()
        self.ethics_ls = self.ethics_ls[:-1]

    def add_ref(self):
        """
        adds line edit to the layout (under ReferencesAndLinks)
        :return:
        """
        line = new_line_edit(self.modified.emit)
        self.ref_ls.append(line)
        self.ref_layout.addWidget(line)

    def remove_ref(self):
        """
        removes the last line edit from layout (under ReferencesAndLinks)
        :return:
        """
        if len(self.ref_ls) == 0:
            return
        self.ref_layout.removeWidget(self.ref_ls[-1])
        self.ref_ls[-1].deleteLater()
        self.ref_ls = self.ref_ls[:-1]

    def init_ui_derivative(self):
        """
        adds missing derivative fields from raw dataset description type
        :return:
        """
        self.derivative = Derivative()
        self.derivative.modified.connect(self.modified.emit)
        self.derivative_layout.addWidget(self.derivative)
        self.modified.emit()

    def clear_ui_derivative(self):
        """
        removes derivative fields
        :return:
        """
        if self.derivative is None:
            return
        self.derivative.deleteLater()
        self.derivative = None
        self.modified.emit()

    def dataset_type_handler(self, index):
        """
        determine what action to take based on the value of DatasetType
        :param index:
        :return:
        """
        if index == 2:
            self.init_ui_derivative()
        else:
            self.clear_ui_derivative()

    def get_data(self):
        """
        get relevant data from the user filled fields
        :return:
        """
        data = {}
        data["Name"] = self.name_value.text()
        data["BIDSVersion"] = self.bids_ver_value.currentText()
        data["DatasetType"] = self.data_type_value.currentText()
        data["License"] = self.license_value.currentText()
        data["Authors"] = [i.text() for i in self.author_ls]
        data["Acknowledgements"] = self.ack_value.toPlainText()
        data["HowToAcknowledge"] = self.how_to_ack_value.toPlainText()
        data["Funding"] = [i.text() for i in self.funding_ls]
        data["EthicsApprovals"] = [i.text() for i in self.ethics_ls]
        data["ReferencesAndLinks"] = [i.text() for i in self.ref_ls]
        data["DatasetDOI"] = self.doi_value.text()

        # in case the the DatasetType is derivative
        if self.derivative is not None:
            data_derivative = self.derivative.get_data()
            data["GeneratedBy"] = data_derivative["GeneratedBy"]
            data["SourceDatasets"] = data_derivative["SourceDatasets"]
        return data

    def set_data(self, data):
        """
        populate form fields from provided data dictionary (typically loaded from JSON)
        :param data: dict containing dataset description data
        :return:
        """
        # Set simple text fields
        self.name_value.setText(data.get("Name", ""))
        self.ack_value.setPlainText(data.get("Acknowledgements", ""))
        self.how_to_ack_value.setPlainText(data.get("HowToAcknowledge", ""))
        self.doi_value.setText(data.get("DatasetDOI", ""))

        # Set combo box values
        if "BIDSVersion" in data:
            index = self.bids_ver_value.findText(data["BIDSVersion"])
            if index >= 0:
                self.bids_ver_value.setCurrentIndex(index)

        if "DatasetType" in data:
            index = self.data_type_value.findText(data["DatasetType"])
            if index >= 0:
                self.data_type_value.setCurrentIndex(index)

        if "License" in data:
            index = self.license_value.findText(data["License"])
            if index >= 0:
                self.license_value.setCurrentIndex(index)

        # Clear existing authors, funding, ethics, references
        while len(self.author_ls) > 0:
            self.author_layout.removeWidget(self.author_ls[-1])
            self.author_ls[-1].deleteLater()
            self.author_ls = self.author_ls[:-1]

        while len(self.funding_ls) > 0:
            self.funding_layout.removeWidget(self.funding_ls[-1])
            self.funding_ls[-1].deleteLater()
            self.funding_ls = self.funding_ls[:-1]

        while len(self.ethics_ls) > 0:
            self.ethics_layout.removeWidget(self.ethics_ls[-1])
            self.ethics_ls[-1].deleteLater()
            self.ethics_ls = self.ethics_ls[:-1]

        while len(self.ref_ls) > 0:
            self.ref_layout.removeWidget(self.ref_ls[-1])
            self.ref_ls[-1].deleteLater()
            self.ref_ls = self.ref_ls[:-1]

        # Populate Authors
        if "Authors" in data:
            for author in data["Authors"]:
                line = new_line_edit(self.modified.emit)
                line.setText(author)
                self.author_ls.append(line)
                self.author_layout.addWidget(line)

        # Populate Funding
        if "Funding" in data:
            for funding in data["Funding"]:
                line = new_line_edit(self.modified.emit)
                line.setText(funding)
                self.funding_ls.append(line)
                self.funding_layout.addWidget(line)

        # Populate EthicsApprovals
        if "EthicsApprovals" in data:
            for ethics in data["EthicsApprovals"]:
                line = new_line_edit(self.modified.emit)
                line.setText(ethics)
                self.ethics_ls.append(line)
                self.ethics_layout.addWidget(line)

        # Populate ReferencesAndLinks
        if "ReferencesAndLinks" in data:
            for ref in data["ReferencesAndLinks"]:
                line = new_line_edit(self.modified.emit)
                line.setText(ref)
                self.ref_ls.append(line)
                self.ref_layout.addWidget(line)

        # Handle derivative data
        if "GeneratedBy" in data or "SourceDatasets" in data:
            self.data_type_value.setCurrentIndex(2)  # set to 'derivative'
            if self.derivative is not None:
                derivative_data = {}
                if "GeneratedBy" in data:
                    derivative_data["GeneratedBy"] = data["GeneratedBy"]
                if "SourceDatasets" in data:
                    derivative_data["SourceDatasets"] = data["SourceDatasets"]
                self.derivative.set_data(derivative_data)

        self.modified.emit()
