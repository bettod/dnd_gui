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

        self.setWindowTitle("DND game manager")
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
                
        self.labelsNameList = []
        self.labelsClassLevelList = []
        self.labelsSpeedList = []
        self.labelsMaxHPList = []
        self.labelAndLineEditHP = []
        self.VBoxLayoutsList = []
        # self.labelsCurrentHPList = []
        # self.lineEditsCurrentHPList = []
    
        for character in [Vesperis, Dagl, Dekland, Hrothgeirr, Leeroy]:
            eval('self.labelsNameList.append(QLabel(' + character.name.split(' ')[0] + '.name))')
            eval('self.labelsClassLevelList.append(QLabel(' + character.name.split(' ')[0] + '.class_name + \', \' + str(' + character.name.split(' ')[0] + '.level) + \' lvl\'))')
            eval('self.labelsSpeedList.append(QLabel("Speed: " + str(' + character.name.split(' ')[0] + '.speed) + \' feet\'))')
            eval('self.labelsMaxHPList.append(QLabel("Max HP: " + str(' + character.name.split(' ')[0] + '.max_hp)))')
            eval('self.labelAndLineEditHP.append(LabelandLineEdit("Current HP: ", str(' + character.name.split(' ')[0] + '.current_hp)))')
            # eval('self.labelsCurrentHPList.append(QLabel("Current HP: "))')
            # eval('self.lineEditsCurrentHPList.append(QLineEdit(str(' + character.name.split(' ')[0] + '.current_hp)))')

            layout = QVBoxLayout()
            layout.addWidget(self.labelsNameList[-1])
            layout.addWidget(self.labelsClassLevelList[-1])
            layout.addWidget(self.labelsSpeedList[-1])
            layout.addWidget(self.labelsMaxHPList[-1])
            layout.addWidget(self.labelAndLineEditHP[-1])
            self.VBoxLayoutsList.append(layout)

        container = QWidget()
        layoutHoriz = QHBoxLayout()
        for layout in self.VBoxLayoutsList:
            layoutHoriz.addLayout(layout)
        container.setLayout(layoutHoriz)

        # Set the central widget of the Window.
        self.setCentralWidget(container)


app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()