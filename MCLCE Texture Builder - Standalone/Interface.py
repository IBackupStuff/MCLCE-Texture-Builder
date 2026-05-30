
import sys
import os
from typing import Self, Callable, Any

from PySide6.QtCore import (
    Qt,
    QMimeData,
    QUrl
)
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QGridLayout,
    QTextEdit,
    QLabel,
    QFrame,
    QPushButton,
    QSizePolicy,
    QFileDialog,
    QDialog,
    QStackedWidget,
    QListView,
    QLineEdit,
    QComboBox,
    QMessageBox,
    QBoxLayout
)
from PySide6.QtGui import (
    QDragEnterEvent,
    QDragLeaveEvent,
    QDropEvent,
    QMouseEvent,
    QDesktopServices,
    QIcon
)

from CollapsibleSection import CollapsibleSection
import InterfaceUtil as iUt
from CodeLibs.Path import Path
from CodeLibs import JsonHandler

from EntryPoint import EntryPoint
from CodeLibs import Logger as log

# global libs holder
class GlobalLibs:
    program_version = JsonHandler.readAll(Path("global", "program_version"))
    
    input_games = JsonHandler.readAll(Path("global", "input_games"))

    input_versions_bedrock = JsonHandler.readAll(Path("global", "input_versions_bedrock"))
    input_versions_bedrock_plus = [f"{text}+" for text in input_versions_bedrock]
    input_versions_java = JsonHandler.readAll(Path("global", "input_versions_java"))
    input_versions_java_plus = [f"{text}+" for text in input_versions_java]

    output_structures_nintendo_switch = JsonHandler.readAll(Path("global", "output_structures_nintendo_switch"))
    output_structures_ps3 = JsonHandler.readAll(Path("global", "output_structures_ps3"))
    output_structures_ps4 = JsonHandler.readAll(Path("global", "output_structures_ps4"))
    output_structures_psV = JsonHandler.readAll(Path("global", "output_structures_psV"))
    output_structures_wiiu = JsonHandler.readAll(Path("global", "output_structures_wiiu"))
    output_structures_xbox_one = JsonHandler.readAll(Path("global", "output_structures_xbox_one"))
    output_structures_xbox360 = JsonHandler.readAll(Path("global", "output_structures_xbox360"))
    output_structures_all = [
        *output_structures_nintendo_switch,
        *output_structures_ps3,
        *output_structures_ps4,
        *output_structures_psV,
        *output_structures_wiiu,
        *output_structures_xbox_one,
        *output_structures_xbox360
    ]

    output_drives = JsonHandler.readAll(Path("global", "output_drives"))

    modes_size = JsonHandler.readAll(Path("global", "modes_size"))
    modes_build = JsonHandler.readAll(Path("global", "modes_build"))

# entry point data holder
class EntryPointData:
    def __init__(self: Self) -> Self:
        self.input_path = None
        self.input_path_type = None
        self.input_game = None
        self.input_version = None

        self.output_path = None
        self.output_structure = None
        self.output_drive = None
        
        self.build_mode = None # error mode
        self.size_mode = None
        self.complex_processing = None

    def __str__(self: Self) -> str:
        return (
            "{"
            f"input_path: {self.input_path}, "
            f"input_path_type: {self.input_path_type}, "
            f"input_game: {self.input_game}, "
            f"input_version: {self.input_version}, "
            f"output_path: {self.output_path}, "
            f"output_structure: {self.output_structure}, "
            f"output_drive: {self.output_drive}, "
            f"build_mode: {self.build_mode}, "
            f"size_mode: {self.size_mode}, "
            f"complex_processing: {self.complex_processing}"
            "}"
        )

# main window
class MainWindow(QWidget):

    ARIAL_ROUNDED: str = "Arial Rounded MT"
    ZIP: str = "zip"
    END_ZIP: str = f".{ZIP}"
    MCPACK: str = "mcpack"
    END_MCPACK: str = f".{MCPACK}"

    INPUT_DRAG_IDLE_STR: str = "Drag & Drop a texture pack here..."
    INPUT_DRAG_INVALID_HOVER: str = "Invalid pack! Check available input games."
    INPUT_DRAG_VALID_HOVER: str = "..."
    INPUT_DRAG_HOLDING_STR: str = "Got your pack!"

    JAVA: str = "java"
    BEDROCK: str = "bedrock"
    NINTENDO_SWITCH: str = "nintendo_switch"
    PS3: str = "ps3"
    PS4: str = "ps4"
    PSV: str = "psV"
    WIIU: str = "wiiu"
    XBOX_ONE: str = "xbox_one"
    XBOX360: str = "xbox360"

    GAME_TO_OUTPUT_STRUCTURE_LIB: dict[str, list] = {
        JAVA: GlobalLibs.output_structures_all,
        BEDROCK: GlobalLibs.output_structures_all,
        NINTENDO_SWITCH: GlobalLibs.output_structures_nintendo_switch,
        PS3: GlobalLibs.output_structures_ps3,
        PS4: GlobalLibs.output_structures_ps4,
        PSV: GlobalLibs.output_structures_psV,
        WIIU: GlobalLibs.output_structures_wiiu,
        XBOX_ONE: GlobalLibs.output_structures_xbox_one,
        XBOX360: GlobalLibs.output_structures_xbox360
    }

    HUGE_LABEL_SIZE: int = 15
    LARGE_LABEL_SIZE: int = 11
    MEDIUM_LABEL_SIZE: int = 9
    SMALL_LABEL_SIZE: int = 7

    def __init__(self: Self, icon: QIcon) -> Self:
        super().__init__()
        
        # variables
        self.curr_version_set: str|None = None
        self.curr_structure_set: str|None = None
        self.entry_data = EntryPointData()
        
        # set main window settings
        self.setWindowTitle(f"MC LCE Texture Builder {GlobalLibs.program_version["ver"]}")
        self.setWindowIcon(icon)
        self.grid = QGridLayout()
        iUt.change_margins(self.grid, all=0)
        self.grid.setRowStretch(0, 1) # settings row
        self.grid.setRowStretch(1, 0) # bar row
        self.setLayout(self.grid)

        # settings grid
        self.settings_grid = QGridLayout()
        self.settings_grid.setContentsMargins(10, 10, 10, 10)
        SET_R0HEIGHT = 20
        self.settings_grid.setRowMinimumHeight(0, SET_R0HEIGHT) 
        self.settings_grid.setRowStretch(0, 0) # input label
        self.settings_grid.setRowStretch(1, 1) # input container
        SET_R2HEIGHT = 10
        self.settings_grid.setRowMinimumHeight(2, SET_R2HEIGHT)
        self.settings_grid.setRowStretch(2, 0) # spacer
        SET_R3HEIGHT = 20
        self.settings_grid.setRowMinimumHeight(3, SET_R3HEIGHT) 
        self.settings_grid.setRowStretch(3, 0) # output label
        self.settings_grid.setRowStretch(4, 0) # output container
        SET_R5HEIGHT = 10
        self.settings_grid.setRowMinimumHeight(5, SET_R5HEIGHT) 
        self.settings_grid.setRowStretch(5, 1) # spacer
        self.settings_grid.setRowStretch(6, 0) # advanced container
        self.settings_container = QWidget()
        self.settings_container.setLayout(self.settings_grid)
        self.grid.addWidget(self.settings_container, 0, 0, 1, 1)

        # input label
        self.input_label = QLabel("Input Settings")
        self.input_label.setFont(self.ARIAL_ROUNDED)
        iUt.set_font_size(self.input_label, self.LARGE_LABEL_SIZE)
        self.input_label.setFixedHeight(SET_R0HEIGHT)
        self.settings_grid.addWidget(self.input_label, 0, 0, 1, 1)

        # input grid rows
        self.input_grid = QGridLayout()
        IN_R0HEIGHT = 100
        self.input_grid.setRowMinimumHeight(0, IN_R0HEIGHT)
        self.input_grid.setRowStretch(0, 1) # default 1
        IN_R1HEIGHT = 30
        self.input_grid.setRowMinimumHeight(1, IN_R1HEIGHT)
        self.input_grid.setRowStretch(1, 0)
        IN_R2HEIGHT = 30
        self.input_grid.setRowMinimumHeight(2, IN_R2HEIGHT)
        self.input_grid.setRowStretch(2, 0)

        # input grid columns
        IN_C0WIDTH = 50
        self.input_grid.setColumnMinimumWidth(0, IN_C0WIDTH)
        self.input_grid.setColumnStretch(0, 0)
        IN_C1WIDTH = 100
        self.input_grid.setColumnMinimumWidth(1, IN_C1WIDTH)
        self.input_grid.setColumnStretch(1, 1)
        IN_C2WIDTH = 150
        self.input_grid.setColumnMinimumWidth(2, IN_C2WIDTH)
        self.input_grid.setColumnStretch(2, 0)

        # input drag/drop space
        self.input_drag = QWidget()
        self.input_drag.setAcceptDrops(True) # must be the event holder because it's above the colored box
        self.input_drag.dragEnterEvent = self.__handle_drag_enter
        self.input_drag.dragLeaveEvent = self.__handle_drag_leave
        self.input_drag.dropEvent = self.__handle_drop
        self.input_drag.mousePressEvent = self.__handle_click
        self.input_drag.setStyleSheet(
            """
            QWidget[state="idle"] {
                background-color: #222222;
                border-radius: 20px;
            }
            QWidget[state="valid_hover"] {
                background-color: #00FF00;
                border-radius: 20px;
            }
            QWidget[state="invalid_hover"] {
                background-color: #FF0000;
                border-radius: 20px;
            }
            QWidget[state="hold"] {
                background-color: #0000FF;
                border-radius: 20px;
            }
            """
        )
        self.input_drag.setProperty("state", "idle")
        self.input_grid.addWidget(self.input_drag, 0, 0, 1, 3)

        # input drag/drop space text
        self.input_drag_text = QLabel()
        self.input_drag_text.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.input_drag_text.setText(self.INPUT_DRAG_IDLE_STR) # default
        self.input_drag_text.setFont(self.ARIAL_ROUNDED)
        iUt.set_font_size(self.input_drag_text, self.HUGE_LABEL_SIZE)
        self.input_drag_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.input_grid.addWidget(self.input_drag_text, 0, 0, 1, 3)

        # input path text
        self.input_path_text = QTextEdit()
        self.input_path_text.setReadOnly(True)
        self.input_path_text.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        self.input_path_text.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.input_path_text.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.input_path_text.setFont(self.ARIAL_ROUNDED)
        self.input_path_text.textChanged.connect(self.__handle_input_path_text_changed)
        self.input_path_text.setFixedHeight(IN_R1HEIGHT)
        self.input_grid.addWidget(self.input_path_text, 1, 0, 1, 2)

        # input path browse
        self.input_path_button = QPushButton("Browse Input")
        self.input_path_button.setFont(self.ARIAL_ROUNDED)
        self.input_path_button.clicked.connect(self.__handle_input_path_button_click)
        self.input_path_button.setFixedHeight(IN_R1HEIGHT)
        self.input_grid.addWidget(self.input_path_button, 1, 2, 1, 1)

        # input type label
        self.intput_type_label = QLabel("Convert From")
        self.intput_type_label.setFont(self.ARIAL_ROUNDED)
        iUt.set_font_size(self.intput_type_label, self.MEDIUM_LABEL_SIZE)
        self.intput_type_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.intput_type_label.setFixedHeight(IN_R2HEIGHT)
        self.input_grid.addWidget(self.intput_type_label, 2, 0, 1, 1)

        # input type
        self.input_type = QComboBox()
        self.input_type.setToolTip("what edition of Minecraft is this texture pack from?")
        self.input_type.addItems(GlobalLibs.input_games)
        self.input_type.currentTextChanged.connect(self.__handle_input_type_changed)
        self.input_type.setFont(self.ARIAL_ROUNDED)
        self.input_type.setFixedHeight(IN_R2HEIGHT)
        self.input_grid.addWidget(self.input_type, 2, 1, 1, 1)

        # input version
        self.input_version = QComboBox()
        self.input_version.setToolTip("what version of Minecraft is this texure pack from?")
        self.input_version.currentIndexChanged.connect(self.__handle_input_version_changed)
        self.input_version.setFont(self.ARIAL_ROUNDED)
        self.input_version.setFixedHeight(IN_R2HEIGHT)
        self.input_grid.addWidget(self.input_version, 2, 2, 1, 1)

        # input frame
        self.input_frame = QFrame()
        self.input_frame.setObjectName("input_frame")
        self.input_frame.setStyleSheet(
            """
                QFrame#input_frame {
                    border: 2px solid #000000;
                    border-radius: 20px;
                }
            """
        )
        self.input_frame.setLayout(self.input_grid)
        self.settings_grid.addWidget(self.input_frame, 1, 0, 1, 1)

        # spacing row
        r2_spacer = QWidget()
        r2_spacer.setFixedHeight(SET_R2HEIGHT)
        self.settings_grid.addWidget(r2_spacer, 2, 0, 1, 1) 

        # output label
        self.output_label = QLabel("Output Settings")
        self.output_label.setFont(self.ARIAL_ROUNDED)
        iUt.set_font_size(self.output_label, self.LARGE_LABEL_SIZE)
        self.output_label.setFixedHeight(SET_R3HEIGHT)
        self.settings_grid.addWidget(self.output_label, 3, 0, 1, 1)

        # output grid rows
        self.output_grid = QGridLayout()
        OUT_R0HEIGHT = 30
        self.output_grid.setRowMinimumHeight(0, OUT_R0HEIGHT)
        self.output_grid.setRowStretch(0, 0)
        OUT_R1HEIGHT = 30
        self.output_grid.setRowMinimumHeight(1, OUT_R1HEIGHT)
        self.output_grid.setRowStretch(1, 0)

        # output grid columns
        OUT_C0WIDTH = 50
        self.output_grid.setColumnMinimumWidth(0, OUT_C0WIDTH)
        self.output_grid.setColumnStretch(0, 0)
        OUT_C1WIDTH = 100
        self.output_grid.setColumnMinimumWidth(1, OUT_C1WIDTH)
        self.output_grid.setColumnStretch(1, 1)
        OUT_C2WIDTH = 150
        self.output_grid.setColumnMinimumWidth(2, OUT_C2WIDTH)
        self.output_grid.setColumnStretch(2, 0)

        # output path text
        self.output_path_text = QTextEdit()
        self.output_path_text.setReadOnly(True)
        self.output_path_text.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        self.output_path_text.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.output_path_text.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.output_path_text.setFont(self.ARIAL_ROUNDED)
        self.output_path_text.textChanged.connect(self.__handle_output_path_text_changed)
        self.output_path_text.setFixedHeight(OUT_R0HEIGHT)
        self.output_grid.addWidget(self.output_path_text, 0, 0, 1, 2)

        # output path browse
        self.output_path_button = QPushButton("Browse Output")
        self.output_path_button.setFont(self.ARIAL_ROUNDED)
        self.output_path_button.clicked.connect(self.__handle_output_path_button_click)
        self.output_path_button.setFixedHeight(OUT_R0HEIGHT)
        self.output_grid.addWidget(self.output_path_button, 0, 2, 1, 1)

        # output structure label
        self.output_structure_label = QLabel("Convert To")
        self.output_structure_label.setFont(self.ARIAL_ROUNDED)
        iUt.set_font_size(self.output_structure_label, self.MEDIUM_LABEL_SIZE)
        self.output_structure_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.output_structure_label.setFixedHeight(OUT_R1HEIGHT)
        self.output_grid.addWidget(self.output_structure_label, 1, 0, 1, 1)

        # output structure
        self.output_structure = QComboBox()
        self.output_structure.setToolTip("what version of Minecraft are you converting to?")
        self.output_structure.currentIndexChanged.connect(self.__handle_output_structure_changed)
        self.output_structure.setFont(self.ARIAL_ROUNDED)
        self.output_structure.setFixedHeight(OUT_R1HEIGHT)
        self.output_grid.addWidget(self.output_structure, 1, 1, 1, 1)

        # output open button
        self.output_open_button = QPushButton("Open Output")
        self.output_open_button.setToolTip("open the output folder that you have choosen")
        self.output_open_button.setFont(self.ARIAL_ROUNDED)
        self.output_open_button.clicked.connect(self.__handle_output_open_button_click)
        self.output_open_button.setFixedHeight(OUT_R1HEIGHT)
        self.output_grid.addWidget(self.output_open_button, 1, 2, 1, 1)

        # output frame
        self.output_frame = QFrame()
        self.output_frame.setObjectName("output_frame")
        self.output_frame.setStyleSheet(
            """
                QFrame#output_frame {
                    border: 2px solid #000000;
                    border-radius: 20px;
                }
            """
        )
        self.output_frame.setLayout(self.output_grid)
        self.settings_grid.addWidget(self.output_frame, 4, 0, 1, 1)

        # spacing row
        r5_spacer = QWidget()
        r5_spacer.setFixedHeight(SET_R5HEIGHT)
        self.settings_grid.addWidget(r5_spacer, 5, 0, 1, 1) 

        # advanced grid rows
        self.advanced_grid = QGridLayout()
        ADV_R0HEIGHT_LABEL = 15
        ADV_R0HEIGHT_ELEMENT = 30
        ADV_R0HEIGHT = ADV_R0HEIGHT_LABEL + ADV_R0HEIGHT_ELEMENT + 15
        self.advanced_grid.setRowMinimumHeight(0, ADV_R0HEIGHT)
        self.advanced_grid.setRowStretch(0, 0)
        ADV_R1HEIGHT = 30
        self.advanced_grid.setRowMinimumHeight(1, ADV_R1HEIGHT)
        self.advanced_grid.setRowStretch(1, 0)

        # advanced grid columns
        ADV_C0WIDTH = 100
        self.advanced_grid.setColumnMinimumWidth(0, ADV_C0WIDTH)
        self.advanced_grid.setColumnStretch(0, 0)
        ADV_C1WIDTH = 100
        self.advanced_grid.setColumnMinimumWidth(0, ADV_C1WIDTH)
        self.advanced_grid.setColumnStretch(1, 0)
        ADV_C2WIDTH = 100
        self.advanced_grid.setColumnMinimumWidth(0, ADV_C2WIDTH)
        self.advanced_grid.setColumnStretch(2, 0)

        # advanced main
        self.advanced_collapsible = CollapsibleSection("Advanced/More Settings")
        self.advanced_collapsible.button_font_str = self.ARIAL_ROUNDED
        self.advanced_collapsible.button_font_size = self.LARGE_LABEL_SIZE
        self.advanced_collapsible.button_height = 30
            # content | frame
        advanced_collapsible_content = QFrame()
        advanced_collapsible_content.setObjectName("advanced_frame")
        advanced_collapsible_content.setStyleSheet(
            """
                QFrame#advanced_frame {
                    border: 2px solid #000000;
                    border-radius: 20px;
                }
            """
        )
        advanced_collapsible_content.setLayout(self.advanced_grid)
        self.advanced_collapsible.content = advanced_collapsible_content
        self.settings_grid.addWidget(self.advanced_collapsible, 6, 0, 1, 1)

        # advanced ⧼output⧽ drive
        advanced_drive_layout = QBoxLayout(QBoxLayout.Direction.TopToBottom)
        iUt.change_margins(advanced_drive_layout, all=0)
        advanced_drive_layout.setSpacing(0)
            # label
        advanced_drive_label = QLabel("Output Drive")
        advanced_drive_label.setFont(self.ARIAL_ROUNDED)
        iUt.set_font_size(advanced_drive_label, self.MEDIUM_LABEL_SIZE)
        advanced_drive_label.setFixedHeight(ADV_R0HEIGHT_LABEL)
        advanced_drive_layout.addWidget(advanced_drive_label)
            # element
        self.advanced_drive = QComboBox()
        self.advanced_drive.setToolTip("what drive will this texture pack live on on your console?")
        self.advanced_drive.currentIndexChanged.connect(self.__handle_advanced_drive_changed)
        self.advanced_drive.setFixedHeight(ADV_R0HEIGHT_ELEMENT)
        advanced_drive_layout.addWidget(self.advanced_drive)
            # container
        advanced_drive_container = QWidget()
        advanced_drive_container.setLayout(advanced_drive_layout)
        advanced_drive_container.setFixedHeight(ADV_R0HEIGHT)
        self.advanced_grid.addWidget(advanced_drive_container, 0, 0, 1, 1)

        # advanced build ⧼mode⧽
        self.entry_data.build_mode = GlobalLibs.modes_build[0] # default selection
        advanced_build_layout = QBoxLayout(QBoxLayout.Direction.TopToBottom)
        iUt.change_margins(advanced_build_layout, all=0)
        advanced_build_layout.setSpacing(0)
            # label
        advanced_build_label = QLabel("Build Mode")
        advanced_build_label.setFont(self.ARIAL_ROUNDED)
        iUt.set_font_size(advanced_build_label, self.MEDIUM_LABEL_SIZE)
        advanced_build_label.setFixedHeight(ADV_R0HEIGHT_LABEL)
        advanced_build_layout.addWidget(advanced_build_label)
            # element
        self.advanced_build = QComboBox()
        self.advanced_build.setToolTip("what texture should be placed when a texture must be resized or cropped?")
        self.advanced_build.addItems(GlobalLibs.modes_build)
        self.advanced_build.currentIndexChanged.connect(self.__handle_advanced_error_changed)
        self.advanced_build.setFixedHeight(ADV_R0HEIGHT_ELEMENT)
        advanced_build_layout.addWidget(self.advanced_build)
            # container
        advanced_error_container = QWidget()
        advanced_error_container.setLayout(advanced_build_layout)
        advanced_error_container.setFixedHeight(ADV_R0HEIGHT)
        self.advanced_grid.addWidget(advanced_error_container, 0, 1, 1, 1)

        # advanced size ⧼mode⧽
        self.entry_data.size_mode = 16 # default selection
        self.entry_data.complex_processing = True # default selection
        advanced_size_layout = QBoxLayout(QBoxLayout.Direction.TopToBottom)
        iUt.change_margins(advanced_size_layout, all=0)
        advanced_size_layout.setSpacing(0)
            # label
        advanced_size_label = QLabel("Size Mode ")
        advanced_size_label.setFont(self.ARIAL_ROUNDED)
        iUt.set_font_size(advanced_size_label, self.MEDIUM_LABEL_SIZE)
        advanced_size_label.setFixedHeight(ADV_R0HEIGHT_LABEL)
        advanced_size_layout.addWidget(advanced_size_label)
            # element
        self.advanced_size = QComboBox()
        self.advanced_size.setToolTip("what size should the texture pack come out as?")
        self.advanced_size.addItems(GlobalLibs.modes_size)
        self.advanced_size.currentIndexChanged.connect(self.__handle_advanced_size_changed)
        self.advanced_size.setFixedHeight(ADV_R0HEIGHT_ELEMENT)
        advanced_size_layout.addWidget(self.advanced_size)
            # container
        advanced_size_container = QWidget()
        advanced_size_container.setLayout(advanced_size_layout)
        advanced_size_container.setFixedHeight(ADV_R0HEIGHT)
        self.advanced_grid.addWidget(advanced_size_container, 0, 2, 1, 1)

        # advanced ⧼show⧽ log
        self.advanced_log_button = QPushButton("Show Log")
        self.advanced_log_button.setToolTip("show the log details of the next/current active build")
        self.advanced_log_button.setFont(self.ARIAL_ROUNDED)
        self.advanced_log_button.clicked.connect(self.__handle_advanced_log_button_click)
        self.advanced_log_button.setFixedHeight(ADV_R1HEIGHT)
        self.advanced_grid.addWidget(self.advanced_log_button, 1, 0, 1, 1)

        # finalized bar
        self.finalized = QFrame()
        self.finalized.setStyleSheet(
            """
                QFrame {
                    background-color: #dfdfdf;
                }
            """
        )
        self.grid.addWidget(self.finalized, 1, 0, 1, 1)

        # finalized grid rows
        self.finalized_grid = QGridLayout()
        self.finalized_grid.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.finalized.setLayout(self.finalized_grid)
        FIN_R0HEIGHT = 30
        self.finalized_grid.setRowMinimumHeight(0, FIN_R0HEIGHT)
        self.finalized_grid.setRowStretch(0, 0)
        FIN_R1HEIGHT = 10
        self.finalized_grid.setRowMinimumHeight(1, FIN_R1HEIGHT)
        self.finalized_grid.setRowStretch(1, 0)
        
        # finalized grid columns
        self.finalized_grid.setRowStretch(0, 1)
        self.finalized_grid.setRowStretch(1, 1)
        self.finalized_grid.setRowStretch(2, 2)
        FIN_C3WIDTH = 100
        self.finalized_grid.setColumnMinimumWidth(3, FIN_C3WIDTH)
        self.finalized_grid.setRowStretch(3, 0)

        # build button
        self.finalized_build = QPushButton("Build")
        self.finalized_build.setEnabled(False)
        self.finalized_build.clicked.connect(self.__handle_finalized_build_click)
        self.finalized_build.setFixedSize(FIN_C3WIDTH, FIN_R0HEIGHT)
        self.finalized_grid.addWidget(self.finalized_build, 0, 3, 1, 1)

        # set main window size 
        self.setMaximumSize(1000, 1000)
        self.resize(200, 450)

    def __set_style_of(self: Self, widget: QWidget, state_name: str, state_value: str) -> None:
        widget.setProperty(state_name, state_value)
        widget.style().unpolish(widget)
        widget.style().polish(widget)
        widget.update()

    def __select_folder(self: Self, start_directory: str|None = None) -> str|None:
        # have user select folder with native
        file_path = QFileDialog.getExistingDirectory(
            self,
            "Select a Folder",
            (start_directory if start_directory else "")
        )
        return file_path

    def __select_file_or_folder(self: Self, filter: str|None = None, start_directory: str|None = None) -> str|None:
        # create dialog
        dialog = QFileDialog()
        dialog.setWindowTitle("Select a File or Folder")
        dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        dialog.setOption(QFileDialog.Option.DontUseNativeDialog, True)
        if start_directory: dialog.setDirectory(start_directory)
        if filter: dialog.setNameFilter(filter)

        # stop dialog from opening folder when selecting and instead accept it
        dialog.accept = lambda: QDialog.accept(dialog)

        # use stacked view
        stacked_widget = dialog.findChild(QStackedWidget)
        view = stacked_widget.findChild(QListView)

        # text updates
        line_edit = dialog.findChild(QLineEdit)
        def update_line_edit():
            selected = []
            for index in view.selectionModel().selectedRows():
                selected.append(f"{index.data()}")
            line_edit.setText(str.join(" ", selected))
        view.selectionModel().selectionChanged.connect(update_line_edit)
        dialog.directoryEntered.connect(lambda: line_edit.setText(""))

        # run dialog
        dialog.exec()
        if dialog.selectedFiles():
            return dialog.selectedFiles()[0]
        return None

    def __set_input_path(self: Self, path: Path) -> None:
        path.formalize()

        # make type selection based on path ending
        if (path.getLast().endswith(self.END_MCPACK)):
            self.entry_data.input_game = self.BEDROCK
            self.entry_data.input_path_type = self.MCPACK
            self.input_type.setCurrentText("bedrock .mcpack file")
        elif (path.getLast().endswith(self.END_ZIP)):
            self.entry_data.input_game = self.JAVA
            self.entry_data.input_path_type = self.ZIP
            self.input_type.setCurrentText("java .zip file")
        else:
            self.entry_data.input_path_type = "folder"
            input_type_text: str = self.input_path_text.toPlainText()
            if (
                input_type_text != "java folder"
                and input_type_text != "bedrock folder"
            ):
                self.input_type.setCurrentText("select a game...")
        
        # set path
        self.input_path_text.setText(path.getPath())

    def __clear_input_path(self: Self) -> None:
        self.input_path_text.setText("")
        self.entry_data.input_path = None
        QMessageBox.information(self, "path cleared", "cleared the input path because it does not match the selected input game")

    def __prompt_input_path(self: Self) -> None:
        input_str: str = self.__select_file_or_folder(f"Texture Packs (‹folder› *{self.END_MCPACK} *{self.END_ZIP})")
        if input_str: self.__set_input_path(Path(input_str, isRootDirectory=True))

    def __handle_drag_enter(self: Self, event: QDragEnterEvent) -> None:
        mime: QMimeData = event.mimeData()

        # check if any of dragged leads to files
        if (
            mime.hasUrls()
            and any([url.isLocalFile() for url in mime.urls()])
        ):
            first_file: str = next((url.toLocalFile() for url in mime.urls()), None)
            if (
                os.path.isdir(first_file)
                or first_file.endswith(self.END_ZIP)
                or first_file.endswith(self.END_MCPACK)
            ):
                # change color, accept
                self.__set_style_of(self.input_drag, "state", "valid_hover")
                self.input_drag_text.setText(self.INPUT_DRAG_VALID_HOVER)
                event.acceptProposedAction()
                return
        self.__set_style_of(self.input_drag, "state", "invalid_hover")
        self.input_drag_text.setText(self.INPUT_DRAG_INVALID_HOVER)
        event.ignore()

    def __handle_drag_leave(self: Self, event: QDragLeaveEvent) -> None:
        # set color back to idle
        self.__set_style_of(self.input_drag, "state", "idle")
        self.input_drag_text.setText(self.INPUT_DRAG_IDLE_STR)

    def __handle_drop(self: Self, event: QDropEvent) -> None:
        mime: QMimeData = event.mimeData()
        # must already have file data because it passed drag check

        if mime.hasUrls():
            file_names: list[str] = [url.toLocalFile() for url in mime.urls()]
            self.__set_input_path(Path(file_names[0], isRootDirectory=True))

    def __handle_click(self: Self, event: QMouseEvent) -> None: 
        self.__prompt_input_path()

    def __handle_input_path_text_changed(self: Self) -> None:
        input_path: str = self.input_path_text.toPlainText()
        if input_path:
            self.entry_data.input_path = input_path
            self.input_drag_text.setText(self.INPUT_DRAG_HOLDING_STR)
            self.__set_style_of(self.input_drag, "state", "hold")
        else:
            self.input_drag_text.setText(self.INPUT_DRAG_IDLE_STR)
            self.__set_style_of(self.input_drag, "state", "idle")

        # check build
        self.__update_for_build_requirements()

    def __handle_input_path_button_click(self: Self) -> None:
        self.__prompt_input_path()

    def __handle_input_type_changed(self: Self, text: str) -> None:
        # switch modes based on selection
        input_type_text: str = self.input_path_text.toPlainText()
        match text:
            case "select a game...":
                self.entry_data.input_game = None
                self.entry_data.input_path_type = None
                self.__set_versions(None)
                self.__set_structures(None)
            case "java folder":
                self.entry_data.input_game = self.JAVA
                self.entry_data.input_path_type = "folder"
                if (
                    input_type_text
                    and (
                        input_type_text.endswith(self.END_ZIP)
                        or input_type_text.endswith(self.END_MCPACK)
                    )
                ): self.__clear_input_path()
                self.__set_versions(self.JAVA)
                self.__set_structures(self.JAVA)
            case "java .zip file":
                self.entry_data.input_game = self.JAVA
                self.entry_data.input_path_type = "zip"
                if (
                    input_type_text
                    and not input_type_text.endswith(self.END_ZIP)
                ): self.__clear_input_path()
                self.__set_versions(self.JAVA)
                self.__set_structures(self.JAVA)
            case "bedrock folder":
                self.entry_data.input_game = self.BEDROCK
                self.entry_data.input_path_type = "folder"
                if (
                    input_type_text
                    and (
                        input_type_text.endswith(self.END_ZIP)
                        or input_type_text.endswith(self.END_MCPACK)
                    )
                ): self.__clear_input_path()
                self.__set_versions(self.BEDROCK)
                self.__set_structures(self.BEDROCK)
            case "bedrock .mcpack file":
                self.entry_data.input_game = self.BEDROCK
                self.entry_data.input_path_type = "mcpack"
                if (
                    input_type_text
                    and not self.input_path_text.toPlainText().endswith(self.END_MCPACK)
                ): self.__clear_input_path()
                self.__set_versions(self.BEDROCK)
                self.__set_structures(self.BEDROCK)
            case "xbox one/nintendo switch default textures (dump only)":
                self.entry_data.input_game = "wiiu"
                self.entry_data.input_path_type = "‹none›"
                self.__set_versions(None)
                self.__set_structures(self.XBOX_ONE)
            case "wiiu default textures":
                self.entry_data.input_game = "wiiu"
                self.entry_data.input_path_type = "‹none›"
                self.__set_versions(None)
                self.__set_structures(self.WIIU)
            case "xbox360/ps3/psV default textures (dump only)":
                self.entry_data.input_game = "wiiu"
                self.entry_data.input_path_type = "‹none›"
                self.__set_versions(None)
                self.__set_structures(self.XBOX360)
            case "ps4 default textures (dump only)":
                self.entry_data.input_game = "wiiu"
                self.entry_data.input_path_type = "‹none›"
                self.__set_versions(None)
                self.__set_structures(self.PS4)

        # check build
        self.__update_for_build_requirements()

    def __set_versions(self: Self, version: str|None) -> None:
        match version:
            case self.JAVA:
                if self.curr_version_set != self.JAVA:
                    self.input_version.clear()
                    self.input_version.addItems(GlobalLibs.input_versions_java_plus)
                    self.curr_version_set = self.JAVA
                    self.entry_data.input_version = GlobalLibs.input_versions_java[0]
            case self.BEDROCK:
                if self.curr_version_set != self.BEDROCK:
                    self.input_version.clear()
                    self.input_version.addItems(GlobalLibs.input_versions_bedrock_plus)
                    self.curr_version_set = self.BEDROCK
                    self.entry_data.input_version = GlobalLibs.input_versions_bedrock[0]
            case _:
                self.input_version.clear()
                self.curr_version_set = None
                self.entry_data.input_version = None

    def __handle_input_version_changed(self: Self, index: int) -> None:
        if (self.curr_version_set == "java"):
            self.entry_data.input_version = GlobalLibs.input_versions_java[index]
        elif (self.curr_version_set == "bedrock"):
            self.entry_data.input_version = GlobalLibs.input_versions_bedrock[index]
        else:
            self.entry_data.input_version = None

        # check build
        self.__update_for_build_requirements()

    def __handle_output_path_text_changed(self: Self) -> None:
        output_path: str = self.output_path_text.toPlainText()
        if output_path:
            self.entry_data.output_path = output_path

        # check build
        self.__update_for_build_requirements()

    def __handle_output_path_button_click(self: Self) -> None:
        output_str: str = self.__select_folder()
        if output_str: self.output_path_text.setText(output_str)

    def __set_structures(self: Self, structure: str|None) -> None:
        # check each game type
        for game in [self.JAVA, self.BEDROCK, self.NINTENDO_SWITCH, self.PS3, self.PS4, self.PSV, self.WIIU, self.XBOX_ONE, self.XBOX360]:
            if (structure == game):
                self.output_structure.clear()
                curr_lib = self.GAME_TO_OUTPUT_STRUCTURE_LIB[game]
                self.output_structure.addItems(curr_lib)
                self.curr_structure_set = game
                self.entry_data.output_structure = curr_lib[0]
                self.__set_drives(curr_lib[0])
                break
        else:
            self.output_structure.clear()
            self.curr_structure_set = None
            self.entry_data.output_structure = None
            self.__set_drives(None)

    def __handle_output_structure_changed(self: Self, index: int) -> None:
        # set entry data to the current structure set's index equal
        output_structure = None
        if self.curr_structure_set is not None:
            output_structure: str = self.GAME_TO_OUTPUT_STRUCTURE_LIB[self.curr_structure_set][index] # get str selection
            self.entry_data.output_structure = output_structure 
        else:
            self.entry_data.output_structure = None
        self.__set_drives(output_structure) # set drives ╎ set drives changes must be mirrored in __set_structures

        # check build
        self.__update_for_build_requirements()

    def __if_path_exists(self: Self, which_path: str, callback: Callable|None = None) -> None:
        # select and validate ‹which_path›
        host: QWidget|None = None
        match which_path:
            case "input": host = self.input_path_text
            case "output": host = self.output_path_text
            case _: raise ValueError(f"⸉{which_path}⸉ is not a valid selector")
        path: str = host.toPlainText()

        # check if path exists
        if os.path.exists(path):
            if callback is not None: 
                callback(path)
        else:
            host.setText("")
            QMessageBox.information(self, "file/folder doesn't exist", f"the specified output directory ({path}) could not be found. as a result it has been cleared")
    
    def __handle_output_open_button_click(self: Self) -> None:
        # check if folder exists
        def open_in_explorer(path_str: str):
            path: Path = Path(path_str, isRootDirectory=True, doFormalize=True)
            if (os.path.isfile(path_str)):
                path.removeAt(len(path) - 1)
            QDesktopServices.openUrl(QUrl.fromLocalFile(path.getPath()))
        self.__if_path_exists("output", open_in_explorer)

    def __set_drives(self: Self, output_structure: str|None) -> None:
        # helper for finalizing
        def set_entry_data() -> None: self.entry_data.output_drive = GlobalLibs.output_drives[0]

        # wiiu
        if (
            (output_structure == "wiiu port pack (root directory)")
            or (output_structure == "wiiu modpack (sdcafiine)")
        ): 
            self.advanced_drive.clear()
            self.advanced_drive.addItems(GlobalLibs.output_drives)
            set_entry_data(); return

        # anything else or none
        self.entry_data.output_drive = None
        self.advanced_drive.clear()

    def __handle_advanced_drive_changed(self: Self, index: int|None) -> None:
        if index is not None:
            self.entry_data.output_drive = GlobalLibs.output_drives[index]
        self.entry_data.output_drive = None

        # check build
        self.__update_for_build_requirements()

    def __handle_advanced_error_changed(self: Self, index: int) -> None:
        self.entry_data.build_mode = GlobalLibs.modes_build[index]
        
        # check build
        self.__update_for_build_requirements()
    
    def __handle_advanced_size_changed(self: Self, index: int) -> None:
        mode: str = GlobalLibs.modes_size[index]
        match mode:
            case "x16": 
                self.entry_data.size_mode = 16
                self.entry_data.complex_processing = True
            case "x32":
                self.entry_data.size_mode = 32
                self.entry_data.complex_processing = True
            case "x32 simple processing":
                self.entry_data.size_mode = 32
                self.entry_data.complex_processing = False
            case "x64 simple processing":
                self.entry_data.size_mode = 64
                self.entry_data.complex_processing = False

        # check build
        self.__update_for_build_requirements()

    def __handle_advanced_log_button_click(self: Self) -> None:
        pass
        
    def __update_for_build_requirements(self: Self) -> None:
        # helper to enable/disable build button
        def set_build(v: bool) -> None: self.finalized_build.setEnabled(v)

        # check input game
        if self.entry_data.input_game is None:
            set_build(False); return
        if (
            (self.entry_data.input_game == self.JAVA)
            or (self.entry_data.input_game == self.BEDROCK)
        ): 
            # check input path
            if self.entry_data.input_path is None:
                set_build(False); return
            
            # check version
            if self.entry_data.input_version is None:
                set_build(False); return
            
        # check output path
        if self.entry_data.output_path is None:
            set_build(False); return
        
        # check output structure
        if self.entry_data.output_structure is None:
            set_build(False); return
        if (
            (self.entry_data.output_structure == "wiiu port pack (root directory)")
            or (self.entry_data.output_structure == "wiiu modpack (sdcafiine)")
        ):
            # check output drive
            if self.entry_data.output_drive is None:
                set_build(False); return
            
        # check build mode
        if self.entry_data.build_mode is None:
            set_build(False); return

        # check size mode
        if self.entry_data.size_mode is None:
            set_build(False); return
        
        # if everything was fine, set build to true
        set_build(True)

    def __handle_finalized_build_click(self: Self) -> None:
        # helper for errors when building
        def show_error(text: str) -> None: QMessageBox.information(self, "error when buidling", text)

        # helper to set None as an empty string
        def none_empty(val: None|Any) -> str|Any: return "" if val == None else val

        # finish helper to re-enable settings
        def set_settings_enabled(v: bool) -> None: self.settings_container.setEnabled(v)
        set_settings_enabled(False)

        # validate input and output paths still exist
        if (
            (self.entry_data.input_game == self.JAVA)
            or (self.entry_data.input_game == self.BEDROCK)
        ): self.__if_path_exists("input")
        self.__if_path_exists("output")

        # initialize entry point
        entry = EntryPoint(
            errorMode=self.entry_data.build_mode,
            processingSize=self.entry_data.size_mode,
            useComplexProcessing=self.entry_data.complex_processing,
            
            inputPath=none_empty(self.entry_data.input_path),
            inputPathType=none_empty(self.entry_data.input_path_type),
            inputGame=none_empty(self.entry_data.input_game),
            inputVersion=none_empty(self.entry_data.input_version),
            
            outputPath=self.entry_data.output_path,
            outputStructure=self.entry_data.output_structure,
            outputDrive=none_empty(self.entry_data.output_drive),

            logging=[log.PLAIN, log.WARNING, log.LOG]
        )

        # run entry point
        entry.start()

        # finish
        set_settings_enabled(True)

def launch() -> None:
    # app construction 
    app = QApplication(sys.argv)
    ICON = QIcon("resources/Re.ico")
    app.setWindowIcon(ICON)

    # set main window
    window = MainWindow(ICON)
    window.show()
    sys.exit(app.exec())
