import sys

from PyQt5.QtCore import QFile, QFile, QTextStream, QSize, Qt
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QMainWindow, QPushButton, QLabel, QLineEdit, QVBoxLayout, QWidget
from PyQt5.QtGui import QPalette, QColor

from character import Character
# from classes import CLASSES
from SRD import SRD, SRD_classes, SRD_class_levels, SRD_rules, SRD_species
from spellcasting import SPELLS, SRD_spells, show_spell, show_spell_list, show_spells_by_class_level
from equipment import SRD_equipment, Item
from magicitems import SRD_magicitems, MagicItem
from feats import SRD_feats
from invocations import SRD_invocations
from skills import SRD_skills, show_skill
from monsters import SRD_monsters, Monster, show_monster_list, show_monsters_by_rating, show_monster
from dice import *
from rules import show_rules

from vesperis import Vesperis
from dagl import Dagl
from dekland import Dekland
from hrothgeirr import Hrothgeirr
from leeroy import Leeroy


LIGHT_BLUE = "#87CEEB"
STEEL_BLUE = "#4682B4"
ROYAL_BLUE = "#4169E1"
ORANGE     = "#FF5733"    
GOLD       = "#FFD700"

class LabelandLineEdit(QWidget):
    def __init__(self, label_text, line_edit_text):
        super().__init__()

        self.label = QLabel(label_text)
        self.line_edit = QLineEdit(line_edit_text)

        layout = QHBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.line_edit)

        self.setLayout(layout)
    
    def editLine(self, new_text):
        self.line_edit.setText(new_text)


# Subclass QMainWindow to customize your application's main window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle(f"<span style='color:{GOLD};'>DND game manager</span>")
        # Force the style to be the same on all OSs:
        app.setStyle("Fusion")

        # Now use a palette to switch to dark colors:
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ToolTipBase, Qt.black)
        palette.setColor(QPalette.ToolTipText, Qt.white)
        palette.setColor(QPalette.Text, Qt.white)
        palette.setColor(QPalette.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ButtonText, Qt.white)
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.HighlightedText, Qt.black)
        app.setPalette(palette)

        # button = QPushButton("Press Me!")

        # fixed window size. can also call setMinimumSize() and setMaximumSize()
        # self.setFixedSize(QSize(400, 300))
                
# ...existing code...

        self.labelsNameList = [] # New list for name labels
        self.labelsClassLevelList = [] # New list for class and level labels
        self.labelsSpeedList = [] # New list for speed labels
        self.labelsMaxHPList = [] # New list for max HP labels
        self.labelAndLineEditHP = [] # New list for LabelandLineEdit widgets
        self.VBoxLayoutsList = []   # New list for QVBoxLayouts
        self.labelsArmorClassList = []  # New list for armor_class
        self.labelsInitiativeList = []  # New list for initiative
        self.labelsProfBonusList = []  # New list for prof_bonus
        self.labelsAndLineEditStrAttackBonusList = []  # New list for Strength Attack Bonus
        self.buttonsSpellListList = []  # New list for spell list buttons

        # Set fixed width for all labels and line edits
        FIXED_WIDTH = 100  # Define a fixed width for all labels and line edits

        for character in [Vesperis, Dagl, Dekland, Hrothgeirr, Leeroy]:
            # Name label in red
            name_label = QLabel()
            name_label.setText(f"<span style='color:red;'>{character.name}</span>")
            # name_label.setFixedWidth(FIXED_WIDTH)  # Set fixed width
            name_label.setAlignment(Qt.AlignCenter)  # Set alignment to center
            self.labelsNameList.append(name_label)

            # Class and level label
            class_level_label = QLabel()
            class_level_label.setText(f"<span style='color:{LIGHT_BLUE};'>{character.class_name}, lvl {character.level}</span>")
            # class_level_label.setFixedWidth(FIXED_WIDTH)  # Set fixed width
            class_level_label.setAlignment(Qt.AlignCenter)  # Set alignment to center
            self.labelsClassLevelList.append(class_level_label)

            # Speed label
            speed_widget = LabelandLineEdit(
                f"<span style='color:green;'>Speed: </span>",
                f"{getattr(character, 'speed', 'N/A')} feet"
            )
            speed_widget.label.setFixedWidth(FIXED_WIDTH)
            speed_widget.line_edit.setFixedWidth(FIXED_WIDTH)
            speed_widget.line_edit.setAlignment(Qt.AlignCenter)  # Set alignment to center
            self.labelsSpeedList.append(speed_widget)

            # Max HP label
            max_hp_widget = LabelandLineEdit(
                f"<span style='color:green;'>Max HP: </span>",
                f"{getattr(character, 'max_hp', 'N/A')}"
            )
            max_hp_widget.label.setFixedWidth(FIXED_WIDTH)
            max_hp_widget.line_edit.setFixedWidth(FIXED_WIDTH)
            max_hp_widget.line_edit.setAlignment(Qt.AlignCenter)  # Set alignment to center
            self.labelsMaxHPList.append(max_hp_widget)

            # Current HP label
            current_hp_widget = LabelandLineEdit(
                f"<span style='color:{ORANGE};'>Current HP: </span>",
                str(getattr(character, 'current_hp', 'N/A'))
            )
            current_hp_widget.label.setFixedWidth(FIXED_WIDTH)
            current_hp_widget.line_edit.setFixedWidth(FIXED_WIDTH)
            current_hp_widget.line_edit.setAlignment(Qt.AlignCenter)  # Set alignment to center
            self.labelAndLineEditHP.append(current_hp_widget)

            # Armor Class label
            armor_class_widget = LabelandLineEdit(
                f"<span style='color:green;'>Armor Class: </span>",
                f"{getattr(character, 'armor_class', 'N/A')}"
            )
            armor_class_widget.label.setFixedWidth(FIXED_WIDTH)
            armor_class_widget.line_edit.setFixedWidth(FIXED_WIDTH)
            armor_class_widget.line_edit.setAlignment(Qt.AlignCenter)  # Set alignment to center
            self.labelsArmorClassList.append(armor_class_widget)

            # Initiative label
            initiative_widget = LabelandLineEdit(
                f"<span style='color:green;'>Initiative: </span>",
                f"{getattr(character, 'initiative', 'N/A')}"
            )
            initiative_widget.label.setFixedWidth(FIXED_WIDTH)
            initiative_widget.line_edit.setFixedWidth(FIXED_WIDTH)
            initiative_widget.line_edit.setAlignment(Qt.AlignCenter)  # Set alignment to center
            self.labelsInitiativeList.append(initiative_widget)

            # Proficiency Bonus label
            prof_bonus_widget = LabelandLineEdit(
                f"<span style='color:green;'>Proficiency Bonus: </span>",
                f"{getattr(character, 'prof_bonus', 'N/A')}"
            )
            prof_bonus_widget.label.setFixedWidth(FIXED_WIDTH)
            prof_bonus_widget.line_edit.setFixedWidth(FIXED_WIDTH)
            prof_bonus_widget.line_edit.setAlignment(Qt.AlignCenter)  # Set alignment to center
            self.labelsProfBonusList.append(prof_bonus_widget)

            # Strength Attack Bonus label
            str_attack_bonus_widget = LabelandLineEdit(
                f"<span style='color:green;'>STR Atk. Bonus: </span>",
                str(character.get_ability_modifier(character.strength) + character.prof_bonus)
            )
            str_attack_bonus_widget.label.setFixedWidth(FIXED_WIDTH)
            str_attack_bonus_widget.line_edit.setFixedWidth(FIXED_WIDTH)
            str_attack_bonus_widget.line_edit.setAlignment(Qt.AlignCenter)  # Set alignment to center
            self.labelsAndLineEditStrAttackBonusList.append(str_attack_bonus_widget)

            # Spell List Button
            spell_list_button = QPushButton(f"Show {character.name}'s Spells")
            spell_list_button.setStyleSheet(f"color: {ROYAL_BLUE};")  # Set the text color to ROYAL_BLUE
            self.buttonsSpellListList.append(spell_list_button)

            # Add widgets and button to layout
            layout = QVBoxLayout()
            layout.addWidget(self.labelsNameList[-1])  # Add name widget
            layout.addWidget(self.labelsClassLevelList[-1])  # Add class and level widget
            layout.addWidget(self.labelsSpeedList[-1])  # Add speed widget
            layout.addWidget(self.labelsMaxHPList[-1])  # Add max HP widget
            layout.addWidget(self.labelAndLineEditHP[-1])  # Add current HP widget
            layout.addWidget(self.labelsArmorClassList[-1])  # Add armor class widget
            layout.addWidget(self.labelsInitiativeList[-1])  # Add initiative widget
            layout.addWidget(self.labelsProfBonusList[-1])  # Add proficiency bonus widget
            layout.addWidget(self.labelsAndLineEditStrAttackBonusList[-1])  # Add strength attack bonus widget
            layout.addWidget(self.buttonsSpellListList[-1])  # Add spell list button

            # Wrap the layout in a QWidget to apply a border
            layout_widget = QWidget()
            layout_widget.setLayout(layout)
            layout_widget.setStyleSheet("border: 1px solid black; padding: 5px;")  # Add border and padding
            self.VBoxLayoutsList.append(layout_widget)

        # Add all layouts to the main container
        container = QWidget()
        layoutHoriz = QHBoxLayout()
        for layout_widget in self.VBoxLayoutsList:
            layoutHoriz.addWidget(layout_widget)
        container.setLayout(layoutHoriz)

        # Set the central widget of the Window.
        self.setCentralWidget(container)

app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()