import sys
from pprint import pprint

from PyQt5.QtCore import QFile, QFile, QTextStream, QSize, Qt
# from PyQt5.QtWidgets import QApplication, QHBoxLayout, QMainWindow, QPushButton, QLabel, QLineEdit, QVBoxLayout, QWidget
from PyQt5.QtGui import QPalette, QColor, QIntValidator, QDoubleValidator
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QRadioButton,
    QButtonGroup,
    QSpinBox,
    QComboBox,
    QAction,
    QLineEdit,
    QScrollArea,
    QCheckBox,    
    QTreeWidget,
    QTreeWidgetItem,
    QTextEdit,
)

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
# from rules import show_rules

from vesperis import Vesperis
from dagl import Dagl
from dekland import Dekland
from hrothgeirr import Hrothgeirr
from leeroy import Leeroy
from dice import roll_dice, sum_rolls


LIGHT_BLUE = "#87CEEB"
STEEL_BLUE = "#4682B4"
ROYAL_BLUE = "#4169E1"
ORANGE     = "#FF5733"    
GOLD       = "#FFD700"
LIGHT_MAGENTA = "#FF55FF"
GOLDEN_ROD = "#DAA520"
DARK_SLATE_BLUE = "#483D8B"
SALMON = '#FA8072'
SANDY_BROWN = '#F4A460'
TEAL = '#008080'

def format_str_html(str_html: str) -> str:
    """
    Take the HTML-like str description from Character.format_single_spell for example
    and normalize whitespace for QLabel rich text.
    """
    if not str_html:
        return ""
    return (
        str_html
        # .replace("\t", "<pre>&emsp;</pre>")
        # .replace("\t", "<pre></pre>")  # QLabel doesn't support &emsp;, so use spaces instead
        .replace("\n", "<br>")
    )

class LabelandLineEdit(QWidget):
    def __init__(self, label_text, line_edit_text):
        super().__init__()

        self.label = QLabel(label_text)
        self.line_edit = QLineEdit(line_edit_text)

         # Only allow integers between, e.g., 0 and 9999
        int_validator = QIntValidator(0, 9999, self)
        self.line_edit.setValidator(int_validator)

        # expose the inner layout so callers can tune spacing/margins
        self.layout_hbox = QHBoxLayout()
        self.layout_hbox.addWidget(self.label)
        self.layout_hbox.addWidget(self.line_edit)
        # tight default for this composite widget
        self.layout_hbox.setSpacing(2)
        self.layout_hbox.setContentsMargins(0, 0, 0, 0)

        self.setLayout(self.layout_hbox)
    
    def editLine(self, new_text):
        self.line_edit.setText(new_text)

class DiceWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Dice Roller")

        central = QWidget()
        main_layout = QVBoxLayout()

        # --- Choose function: roll_dice vs sum_rolls ---
        func_label = QLabel("Choose function:")
        self.radio_roll_dice = QRadioButton("roll_dice (single roll)")
        self.radio_sum_rolls = QRadioButton("sum_rolls (multiple dice)")
        self.radio_roll_dice.setChecked(True)

        func_group_layout = QVBoxLayout()
        func_group_layout.addWidget(func_label)
        func_group_layout.addWidget(self.radio_roll_dice)
        func_group_layout.addWidget(self.radio_sum_rolls)

        main_layout.addLayout(func_group_layout)

        # --- Dice type selection ---
        dice_type_layout = QHBoxLayout()
        dice_type_layout.addWidget(QLabel("Die type:"))

        self.die_combo = QComboBox()
        # common dice
        self.die_combo.addItems(["4", "6", "8", "10", "12", "20", "100"])
        self.die_combo.setCurrentText("20")

        dice_type_layout.addWidget(self.die_combo)
        main_layout.addLayout(dice_type_layout)

        # --- Number of dice (for sum_rolls) ---
        count_layout = QHBoxLayout()
        count_layout.addWidget(QLabel("Number of dice (sum_rolls):"))
        self.count_spin = QSpinBox()
        self.count_spin.setMinimum(1)
        self.count_spin.setMaximum(100)  # arbitrary cap
        self.count_spin.setValue(1)
        count_layout.addWidget(self.count_spin)
        main_layout.addLayout(count_layout)

        # connect radios to toggle method
        self.radio_roll_dice.toggled.connect(self.update_count_spin_state)
        self.radio_sum_rolls.toggled.connect(self.update_count_spin_state)
        # set initial state
        self.update_count_spin_state()

        # # --- Drop lowest (for sum_rolls) ---
        # drop_layout = QHBoxLayout()
        # drop_layout.addWidget(QLabel("Drop lowest die (sum_rolls):"))
        # self.drop_combo = QComboBox()
        # self.drop_combo.addItems(["False", "True"])
        # self.drop_combo.setCurrentText("False")
        # drop_layout.addWidget(self.drop_combo)
        # main_layout.addLayout(drop_layout)

        # --- Roll button and result label ---
        self.roll_button = QPushButton("Roll")
        self.roll_button.clicked.connect(self.handle_roll)

        self.result_label = QLabel("Result will appear here.")
        main_layout.addWidget(self.roll_button)
        main_layout.addWidget(self.result_label)

        central.setLayout(main_layout)
        self.setCentralWidget(central)
    
    def update_count_spin_state(self):
        """Enable count_spin only when sum_rolls is selected."""
        self.count_spin.setEnabled(self.radio_sum_rolls.isChecked())

    def handle_roll(self):
        try:
            die_size = int(self.die_combo.currentText())
        except ValueError:
            self.result_label.setText("Invalid die size.")
            return

        use_roll_dice = self.radio_roll_dice.isChecked()
        use_sum_rolls = self.radio_sum_rolls.isChecked()

        if use_roll_dice:
            # roll_dice(dice: int = 20)
            result = roll_dice(dice=die_size)
            self.result_label.setText(f"roll_dice(d{die_size}) -> {result}")
        elif use_sum_rolls:
            # sum_rolls(dX=..., drop_lowest=...)
            count = self.count_spin.value()
            # drop_lowest = self.drop_combo.currentText() == "True"
            drop_lowest = "False"

            # Map selected die size to the correct parameter
            kwargs = {
                "d100": 0,
                "d20": 0,
                "d12": 0,
                "d10": 0,
                "d8": 0,
                "d6": 0,
                "d4": 0,
                "drop_lowest": drop_lowest,
            }

            if die_size == 100:
                kwargs["d100"] = count
            elif die_size == 20:
                kwargs["d20"] = count
            elif die_size == 12:
                kwargs["d12"] = count
            elif die_size == 10:
                kwargs["d10"] = count
            elif die_size == 8:
                kwargs["d8"] = count
            elif die_size == 6:
                kwargs["d6"] = count
            elif die_size == 4:
                kwargs["d4"] = count
            else:
                self.result_label.setText("Unsupported die size for sum_rolls.")
                return

            result = sum_rolls(**kwargs)
            self.result_label.setText(
                f"sum_rolls(d{die_size}={count}) -> {result}"
            )
        else:
            self.result_label.setText("Please select a function.")

class FeetToMetersWindow(QMainWindow):
    """Simple converter from feet to meters."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Feet to Meters")

        central = QWidget()
        layout = QVBoxLayout()

        row = QHBoxLayout()
        self.feet_edit = QLineEdit()
        self.feet_edit.setPlaceholderText("Feet")
        # allow only floating-point numbers (e.g. -9999.99 to 9999.99)
        validator = QDoubleValidator(-9999.99, 9999.99, 2, self)
        validator.setNotation(QDoubleValidator.StandardNotation)
        self.feet_edit.setValidator(validator)
        row.addWidget(QLabel("Feet:"))
        row.addWidget(self.feet_edit)
        layout.addLayout(row)

        self.result_label = QLabel("Meters: -")
        convert_btn = QPushButton("Convert")
        convert_btn.clicked.connect(self.convert)

        layout.addWidget(convert_btn)
        layout.addWidget(self.result_label)

        central.setLayout(layout)
        self.setCentralWidget(central)

    def convert(self):
        try:
            feet = float(self.feet_edit.text())
        except ValueError:
            self.result_label.setText("Meters: invalid input")
            return
        meters = feet * 0.3048
        self.result_label.setText(f"Meters: {meters:.2f}")

class FeaturesWindow(QMainWindow):
    def __init__(self, character, parent=None):
        super().__init__(parent)
        self.character = character

        char_name = getattr(character, "name", "Unknown")
        self.setWindowTitle(f"Features - {char_name}")
        self.resize(800, 600)

        central = QWidget()
        main_layout = QVBoxLayout()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()

        # Use character.show() to get the text (assuming it returns a string;
        # if it prints, we need to refactor it to return instead)
        try:
            features_text = character.show_features()
        except TypeError:
            # if show() prints and returns None, fallback or adjust show()
            features_text = ""

        html = format_str_html(features_text)
        label = QLabel(html)
        label.setWordWrap(True)
        label.setTextFormat(Qt.RichText)

        scroll_layout.addWidget(label)
        scroll_layout.addStretch(1)
        scroll_widget.setLayout(scroll_layout)
        scroll.setWidget(scroll_widget)

        main_layout.addWidget(scroll)
        central.setLayout(main_layout)
        self.setCentralWidget(central)

class InvocationsWindow(QMainWindow):
    def __init__(self, character, parent=None):
        super().__init__(parent)
        self.character = character

        char_name = getattr(character, "name", "Unknown")
        self.setWindowTitle(f"Invocations - {char_name}")
        self.resize(800, 600)

        central = QWidget()
        main_layout = QVBoxLayout()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()

        # Use character.show_invocations_known() to get the text (assuming it returns a string;
        # if it prints, we need to refactor it to return instead)
        try:
            invocations_text = character.show_invocations_known()
        except TypeError:
            # if show() prints and returns None, fallback or adjust show()
            invocations_text = ""

        html = format_str_html(invocations_text)
        label = QLabel(html)
        label.setWordWrap(True)
        label.setTextFormat(Qt.RichText)

        scroll_layout.addWidget(label)
        scroll_layout.addStretch(1)
        scroll_widget.setLayout(scroll_layout)
        scroll.setWidget(scroll_widget)

        main_layout.addWidget(scroll)
        central.setLayout(main_layout)
        self.setCentralWidget(central)

class MetamagicWindow(QMainWindow):
    def __init__(self, character, parent=None):
        super().__init__(parent)
        self.character = character

        char_name = getattr(character, "name", "Unknown")
        self.setWindowTitle(f"Metamagic Feats - {char_name}")
        self.resize(800, 600)

        central = QWidget()
        main_layout = QVBoxLayout()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()

        # Use character.show_invocations_known() to get the text (assuming it returns a string;
        # if it prints, we need to refactor it to return instead)
        try:
            metamagic_text = character.show_metamagic_feats()
        except TypeError:
            # if show() prints and returns None, fallback or adjust show()
            metamagic_text = ""

        html = format_str_html(metamagic_text)
        label = QLabel(html)
        label.setWordWrap(True)
        label.setTextFormat(Qt.RichText)

        scroll_layout.addWidget(label)
        scroll_layout.addStretch(1)
        scroll_widget.setLayout(scroll_layout)
        scroll.setWidget(scroll_widget)

        main_layout.addWidget(scroll)
        central.setLayout(main_layout)
        self.setCentralWidget(central)


class SavingThrowsWindow(QMainWindow):
    def __init__(self, character, parent=None):
        super().__init__(parent)
        self.character = character

        char_name = getattr(character, "name", "Unknown")
        self.setWindowTitle(f"Saving Throws - {char_name}")
        self.resize(300, 200)

        central = QWidget()
        main_layout = QVBoxLayout()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()

        # Use character.show_saving_throws() to get the text
        try:
            saving_text = character.show_saving_throws()
        except TypeError:
            # if show_saving_throws() prints and returns None, fallback
            saving_text = ""

        html = format_str_html(saving_text)
        label = QLabel(html)
        label.setWordWrap(True)
        label.setTextFormat(Qt.RichText)

        scroll_layout.addWidget(label)
        scroll_layout.addStretch(1)
        scroll_widget.setLayout(scroll_layout)
        scroll.setWidget(scroll_widget)

        main_layout.addWidget(scroll)
        central.setLayout(main_layout)
        self.setCentralWidget(central)

class SkillsWindow(QMainWindow):
    def __init__(self, character, parent=None):
        super().__init__(parent)
        self.character = character

        char_name = getattr(character, "name", "Unknown")
        self.setWindowTitle(f"Skills - {char_name}")
        self.resize(300, 400)

        central = QWidget()
        main_layout = QVBoxLayout()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()

        # Use character.show_skill_bonuses() to get the text
        try:
            skills_text = character.show_skill_bonuses()
        except TypeError:
            # if show_saving_throws() prints and returns None, fallback
            skills_text = ""

        html = format_str_html(skills_text)
        label = QLabel(html)
        label.setWordWrap(True)
        label.setTextFormat(Qt.RichText)

        scroll_layout.addWidget(label)
        scroll_layout.addStretch(1)
        scroll_widget.setLayout(scroll_layout)
        scroll.setWidget(scroll_widget)

        main_layout.addWidget(scroll)
        central.setLayout(main_layout)
        self.setCentralWidget(central)

class ItemListWindow(QMainWindow):
    def __init__(self, character, parent=None):
        super().__init__(parent)
        self.character = character
        self.main_window = parent  # reference to MainWindow for updating character state if needed

        char_name = getattr(character, "name", "Unknown")
        self.setWindowTitle(f"Inventory - {getattr(character, 'name', 'Unknown')}")
        self.resize(400, 600)

        central = QWidget()
        main_layout = QVBoxLayout()

        # Scroll area in case there are many items
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()

        items = getattr(character, "inventory", [])
        magic_items = getattr(character, "magicinventory", [])

        self.itemsEquippedCheckboxes = [] # New list for equipped checkboxes

        for item in items:
            # ITEMS object
            item_name = getattr(item, "name", "Unknown item")

            # Use character helper to get same formatting as show_inventory()
            if hasattr(character, "format_single_item"):
                item_desc = character.format_single_item(item)
            else:
                item_desc = getattr(item, "description", "No description available.")

            item_container = QWidget()
            item_layout = QVBoxLayout()
            item_layout.setContentsMargins(0,0,0,0)
            item_layout.setSpacing(20)
            item_container.setLayout(item_layout)

            btn = QPushButton(item_name)
            btn.setCheckable(True)
            btn.setStyleSheet(f"color: {ORANGE};")

            html_desc = format_str_html(item_desc)
            desc_label = QLabel(html_desc)
            desc_label.setWordWrap(True)
            desc_label.setVisible(False)
            desc_label.setTextFormat(Qt.RichText)

            btn.toggled.connect(lambda checked, lbl=desc_label: lbl.setVisible(checked))

            item_layout.addWidget(btn)
            item_layout.addWidget(desc_label)
            # --- Equipped checkbox for weapons ---
            is_weapon = getattr(item, "damage", None) is not None
            if is_weapon:
                # find index of this character in the main window's character list
                characters = [Vesperis, Dagl, Dekland, Hrothgeirr, Leeroy]
                try:
                    char_idx = characters.index(self.character)
                except ValueError:
                    char_idx = None
                # default atkbonus_string from STR if index not found
                atkbonus_str_string = str(
                    character.get_ability_modifier(character.strength) + character.prof_bonus
                )
                # default atkbonus_string from DEX if index not found
                atkbonus_dex_string = str(
                    character.get_ability_modifier(character.dexterity) + character.prof_bonus
                )
                
                # if we found the character index, use the Dex attack bonus line edit value
                str_widget = None
                dex_widget = None
                if (
                    char_idx is not None
                    and self.main_window is not None
                    and 0 <= char_idx < len(self.main_window.labelsAndLineEditStrAttackBonusList)
                    and 0 <= char_idx < len(self.main_window.labelsAndLineEditDexAttackBonusList)
                ):
                    str_widget = self.main_window.labelsAndLineEditStrAttackBonusList[char_idx]
                    dex_widget = self.main_window.labelsAndLineEditDexAttackBonusList[char_idx]

                # create labels but don't hard‑code the final text yet
                atk_bonus_label = LabelandLineEdit(
                    "<span style='color:red;'>Atk Bonus: </span>",
                    "",
                )
                damage_label = LabelandLineEdit(
                    "<span style='color:red;'>Damage: </span>",
                    "",
                )
                atk_bonus_label.setVisible(False)
                item_layout.addWidget(atk_bonus_label)
                damage_label.setVisible(False)
                item_layout.addWidget(damage_label)
                equipped_checkbox = QCheckBox("Equipped")
                equipped_checkbox.setVisible(False)  # hidden until expanded
                self.itemsEquippedCheckboxes.append(equipped_checkbox)  # Add to the list of checkboxes
                item_layout.addWidget(equipped_checkbox)
                equipped_checkbox.toggled.connect(self.on_equipped_changed)

                
                def toggle_item_widgets(
                    checked,
                    it=item,
                    lbl=desc_label,
                    atk_label=atk_bonus_label,
                    dmg_label=damage_label,
                    cb=equipped_checkbox,
                    ch=character,
                    str_w=str_widget,
                    dex_w=dex_widget,
                ):
                    lbl.setVisible(checked)
                    atk_label.setVisible(checked)
                    dmg_label.setVisible(checked)
                    if cb is not None:
                        cb.setVisible(checked)

                    if not checked:
                        return

                    # --- recompute using CURRENT MainWindow line edits ---

                    # STR atk bonus
                    if str_w is not None:
                        str_txt = str_w.line_edit.text()
                        if str_txt.strip():
                            atk_str = str_txt
                        else:
                            atk_str = str(ch.get_ability_modifier(ch.strength) + ch.prof_bonus)
                    else:
                        atk_str = str(ch.get_ability_modifier(ch.strength) + ch.prof_bonus)

                    # DEX atk bonus
                    if dex_w is not None:
                        dex_txt = dex_w.line_edit.text()
                        if dex_txt.strip():
                            atk_dex = dex_txt
                        else:
                            atk_dex = str(ch.get_ability_modifier(ch.dexterity) + ch.prof_bonus)
                    else:
                        atk_dex = str(ch.get_ability_modifier(ch.dexterity) + ch.prof_bonus)

                    # build strings (keep your special / finesse logic)
                    special = getattr(it, "special", "")
                    if special:
                        atkbonus_string = atk_str + special
                        damage_str = (
                            it.damage["damage_dice"]
                            + "+ "
                            + str(int(special) + ch.get_ability_modifier(ch.strength))
                        )
                        for prop in it.properties:
                            if "Finesse" in prop.values():
                                atkbonus_string += " or " + atk_dex + special
                                damage_str += (
                                    " or "
                                    + it.damage["damage_dice"]
                                    + "+ "
                                    + str(int(special) + ch.get_ability_modifier(ch.dexterity))
                                )
                                break
                    else:
                        atkbonus_string = atk_str
                        damage_str = (
                            it.damage["damage_dice"]
                            + "+ "
                            + str(ch.get_ability_modifier(ch.strength))
                        )
                        for prop in it.properties:
                            if "Finesse" in prop.values():
                                atkbonus_string += " or " + atk_dex
                                damage_str += (
                                    " or "
                                    + it.damage["damage_dice"]
                                    + "+ "
                                    + str(ch.get_ability_modifier(ch.dexterity))
                                )
                                break
                            
                    atk_label.editLine(atkbonus_string)
                    dmg_label.editLine(damage_str)

                btn.toggled.connect(toggle_item_widgets)
                
            scroll_layout.addWidget(item_container)
        
        # magic items header
        magic_items_label = QLabel(
            f"<span style='color:{GOLD};'>Magic Items</span>"
        )
        magic_items_label.setTextFormat(Qt.RichText)
        magic_items_label.setAlignment(Qt.AlignCenter)  # Set alignment to center
        scroll_layout.addWidget(magic_items_label)

        for item in magic_items:
            # ITEMS object
            item_name = getattr(item, "name", "Unknown item")

            # Use character helper to get same formatting as show_inventory()
            if hasattr(character, "format_single_item"):
                item_desc = character.format_single_item(item)
            else:
                item_desc = getattr(item, "description", "No description available.")

            item_container = QWidget()
            item_layout = QVBoxLayout()
            item_layout.setContentsMargins(0,0,0,0)
            item_layout.setSpacing(20)
            item_container.setLayout(item_layout)

            btn = QPushButton(item_name)
            btn.setCheckable(True)
            btn.setStyleSheet(f"color: {ORANGE};")

            html_desc = format_str_html(item_desc)
            desc_label = QLabel(html_desc)
            desc_label.setWordWrap(True)
            desc_label.setVisible(False)
            desc_label.setTextFormat(Qt.RichText)

            btn.toggled.connect(lambda checked, lbl=desc_label: lbl.setVisible(checked))

            item_layout.addWidget(btn)
            item_layout.addWidget(desc_label)
            scroll_layout.addWidget(item_container)

        scroll_layout.addStretch(1)
        scroll_widget.setLayout(scroll_layout)
        scroll.setWidget(scroll_widget)

        main_layout.addWidget(scroll)
        central.setLayout(main_layout)
        self.setCentralWidget(central)

    def on_equipped_changed(self, checked):
        # If this weapon is now equipped in main hand, unpdate character stats and uncheck any other equipped weapon checkboxes
        if checked:
            for other_checkbox in self.itemsEquippedCheckboxes:
                if other_checkbox.isChecked() and other_checkbox != self.sender():
                    other_checkbox.setChecked(False)
    
class SpellsByLevelWindow(QMainWindow):
    """Display all spells from SRD_spells, grouped by level."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Spells By Level")
        self.resize(800, 800)

        central = QWidget()
        main_layout = QVBoxLayout()

        # Search bar
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search spells by name or description...")
        self.search_edit.textChanged.connect(self.filter_spells)
        main_layout.addWidget(self.search_edit)

        # Scroll area for spells list
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()

        # Initialize list to hold all spell data for filtering
        self.all_spell_data = []  # list of (container, name, desc)

        # Group spells by level
        spells_by_level = {}
        for spell_id in SRD_spells:
            spell_data = SRD_spells[spell_id]
            level = spell_data.get('level', 0)
            spells_by_level.setdefault(level, []).append(spell_data)

        # Sort each level's spells by name
        for level in spells_by_level:
            spells_by_level[level].sort(key=lambda s: s.get('name', 'Unknown'))

        # Display spells by level
        for level in sorted(spells_by_level.keys()):
            # Level header button
            lvl_btn = QPushButton(f"Level {level} Spells")
            lvl_btn.setStyleSheet(f"color: {GOLD};")
            lvl_btn.setCheckable(True)
            lvl_btn.setChecked(False)
            scroll_layout.addWidget(lvl_btn)

            # List to hold spell containers for this level
            level_spell_containers = []

            # Display each spell in this level
            for spell_data in spells_by_level[level]:
                spell_name = spell_data.get('name', 'Unknown Spell')
                spell_desc = spell_data.get('desc', ['No description available.'])
                if isinstance(spell_desc, list):
                    spell_desc = '\n'.join(spell_desc)

                spell_container = QWidget()
                spell_layout = QVBoxLayout()
                spell_layout.setContentsMargins(0,0,0,0)
                spell_layout.setSpacing(20)
                spell_container.setLayout(spell_layout)

                btn = QPushButton(spell_name)
                btn.setStyleSheet(f"color: {ORANGE};")
                btn.setCheckable(True)

                html_desc = format_str_html(show_spell(spell_name))
                desc_label = QLabel(html_desc)
                desc_label.setWordWrap(True)
                desc_label.setVisible(False)

                btn.toggled.connect(lambda checked, lbl=desc_label: lbl.setVisible(checked))

                spell_layout.addWidget(btn)
                spell_layout.addWidget(desc_label)
                scroll_layout.addWidget(spell_container)
                level_spell_containers.append(spell_container)
                self.all_spell_data.append((spell_container, spell_name, spell_desc))
                spell_container.setVisible(False)  # start hidden until level button toggled

            # Connect level button to toggle all spells in this level
            lvl_btn.toggled.connect(lambda checked, containers=level_spell_containers: 
                [c.setVisible(checked) for c in containers])

        scroll_layout.addStretch(1)
        scroll_widget.setLayout(scroll_layout)
        scroll.setWidget(scroll_widget)

        main_layout.addWidget(scroll)
        central.setLayout(main_layout)
        self.setCentralWidget(central)

    def filter_spells(self, text):
        text = text.lower()
        for container, name, desc in self.all_spell_data:
            visible = text in name.lower() or text in desc.lower()
            container.setVisible(visible)

class MonstersByCRWindow(QMainWindow):
    """Display all monsters from SRD_monsters, grouped by challenge rating."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Monsters By CR")
        self.resize(800, 800)

        central = QWidget()
        main_layout = QVBoxLayout()

        # Search bar
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search monsters by name or description...")
        self.search_edit.textChanged.connect(self.filter_monsters)
        main_layout.addWidget(self.search_edit)

        # Scroll area for monsters list
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()

        # Initialize list to hold all monster data for filtering
        self.all_monster_data = []  # list of (container, name, desc)

        # Group monsters by CR
        monsters_by_cr = {}
        for monster_id in SRD_monsters:
            monster_data = SRD_monsters[monster_id]
            cr = monster_data.get('challenge_rating', 0)
            monsters_by_cr.setdefault(cr, []).append(monster_data)

        # Sort each CR's monsters by name
        for cr in monsters_by_cr:
            monsters_by_cr[cr].sort(key=lambda m: m.get('name', 'Unknown'))

        # Display monsters by CR
        for cr in sorted(monsters_by_cr.keys()):
            # CR header button
            cr_btn = QPushButton(f"CR {cr} Monsters")
            cr_btn.setStyleSheet(f"color: {GOLD};")
            cr_btn.setCheckable(True)
            cr_btn.setChecked(True)  # Start expanded
            scroll_layout.addWidget(cr_btn)

            # List to hold monster containers for this CR
            cr_monster_containers = []

            # Display each monster in this CR
            for monster_data in monsters_by_cr[cr]:
                monster_name = monster_data.get('name', 'Unknown Monster')
                monster_index = monster_data.get('index', 'Unknown Monster')
                monster_desc = monster_data.get('desc', 'No description available.')

                monster_container = QWidget()
                monster_layout = QVBoxLayout()
                monster_layout.setContentsMargins(0,0,0,0)
                monster_layout.setSpacing(20)
                monster_container.setLayout(monster_layout)

                btn = QPushButton(monster_name)
                btn.setStyleSheet(f"color: {ORANGE};")
                btn.setCheckable(True)

                html_desc = format_str_html(show_monster(monster_index))
                desc_label = QLabel(html_desc)
                desc_label.setWordWrap(True)
                desc_label.setVisible(False)

                btn.toggled.connect(lambda checked, lbl=desc_label: lbl.setVisible(checked))

                monster_layout.addWidget(btn)
                monster_layout.addWidget(desc_label)
                scroll_layout.addWidget(monster_container)
                cr_monster_containers.append(monster_container)
                self.all_monster_data.append((monster_container, monster_name, monster_desc))
                monster_container.setVisible(False)  # start hidden until CR button toggled

            # Connect CR button to toggle all monsters in this CR
            cr_btn.toggled.connect(lambda checked, containers=cr_monster_containers: 
                [c.setVisible(checked) for c in containers])

        scroll_layout.addStretch(1)
        scroll_widget.setLayout(scroll_layout)
        scroll.setWidget(scroll_widget)

        main_layout.addWidget(scroll)
        central.setLayout(main_layout)
        self.setCentralWidget(central)

    def filter_monsters(self, text):
        text = text.lower()
        for container, name, desc in self.all_monster_data:
            visible = text in name.lower() or text in desc.lower()
            container.setVisible(visible)

class RulesWindow(QMainWindow):
    """Expandable view of all SRD_rules by depth."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Rules (SRD)")
        self.resize(900, 700)

        central = QWidget()
        # Outer vertical layout: search bar + content
        outer_layout = QVBoxLayout()
        central.setLayout(outer_layout)

        # Search bar
        search_layout = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search rules...")
        search_layout.addWidget(self.search_edit)
        outer_layout.addLayout(search_layout)

        # Main horizontal layout: tree + text
        main_layout = QHBoxLayout()
        outer_layout.addLayout(main_layout)

        # Left: tree of rules
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("Rules")
        main_layout.addWidget(self.tree, stretch=1)

        # Right: rule text
        self.text_view = QTextEdit()
        self.text_view.setReadOnly(True)
        main_layout.addWidget(self.text_view, stretch=2)

        self.setCentralWidget(central)

        # Populate tree from SRD_rules
        self._populate_tree()
        self.tree.itemClicked.connect(self._on_item_clicked)
        self.search_edit.textChanged.connect(self._on_search_changed)

    def _populate_tree(self):
        # SRD_rules is a nested dict of strings; split leaf strings by '#'
        def add_nodes(parent_item, value):
            if isinstance(value, dict):
                for k, v in value.items():
                    child = QTreeWidgetItem([k])
                    parent_item.addChild(child)
                    add_nodes(child, v)
            elif isinstance(value, str):
                # Split by '#' into sections, each first line becomes a child node
                sections = [s for s in value.split("#") if s.strip()]
                for idx, section in enumerate(sections):
                    title_line = section.strip().split("\n", 1)[0]
                    child = QTreeWidgetItem([title_line])
                    # Store full text for this section
                    child.setData(0, Qt.UserRole, section.strip())
                    parent_item.addChild(child)

        self.tree.clear()
        for top_key, second_level in SRD_rules.items():
            top_item = QTreeWidgetItem([top_key])
            self.tree.addTopLevelItem(top_item)
            add_nodes(top_item, second_level)
        self.tree.expandToDepth(1)

    def _on_item_clicked(self, item, _column):
        text = item.data(0, Qt.UserRole)
        if not text:
            # Non-leaf node; clear or ignore
            self.text_view.clear()
            return
        formatted = text.replace("#", "")
        self.text_view.setPlainText(formatted)

    def _on_search_changed(self, text: str):
        """Filter tree items and highlight matches in the current rule text."""
        text = text.strip().lower()

        # Filter tree: show nodes whose label or stored text matches, and their ancestors.
        def matches(item) -> bool:
            label = item.text(0).lower()
            stored = item.data(0, Qt.UserRole)
            stored_text = stored.lower() if isinstance(stored, str) else ""
            if not text:
                return True
            return (text in label) or (text in stored_text)

        def filter_item(item) -> bool:
            child_match = False
            for i in range(item.childCount()):
                if filter_item(item.child(i)):
                    child_match = True
            own_match = matches(item)
            visible = own_match or child_match
            item.setHidden(not visible)
            if visible and text:
                # Expand branches that contain matches
                parent = item.parent()
                while parent is not None:
                    parent.setExpanded(True)
                    parent = parent.parent()
            return visible

        for i in range(self.tree.topLevelItemCount()):
            filter_item(self.tree.topLevelItem(i))

        # Highlight in text_view (simple lowercase search, no rich formatting)
        current = self.text_view.toPlainText()
        if not text or not current:
            # Reset any selection
            cursor = self.text_view.textCursor()
            cursor.clearSelection()
            self.text_view.setTextCursor(cursor)
            return

        idx = current.lower().find(text)
        if idx != -1:
            cursor = self.text_view.textCursor()
            cursor.setPosition(idx)
            cursor.setPosition(idx + len(text), cursor.KeepAnchor)
            self.text_view.setTextCursor(cursor)
        else:
            cursor = self.text_view.textCursor()
            cursor.clearSelection()
            self.text_view.setTextCursor(cursor)

class StatusWindow(QMainWindow):
    """Per-character window to toggle conditions on/off."""
    def __init__(self, character, parent=None):
        super().__init__(parent)
        self.character = character

        char_name = getattr(character, "name", "Unknown")
        # self.setWindowTitle(f"Statuses - {char_name}")
        self.resize(500, 500)

        central = QWidget()
        main_layout = QVBoxLayout()

        # Title
        title = QLabel(f"Statuses and Conditions for {char_name}")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"color: {GOLDEN_ROD}; font-weight: bold;")
        main_layout.addWidget(title)

        # Scroll area for many conditions
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()

        self.condition_checkboxes = {}

        # Short descriptions for each condition
        condition_descriptions = {
            "blinded":      "Can't see; fails sight checks; attacks vs you have adv; your attacks have disadv.",
            "charmed":      "Can't attack charmer; charmer has adv on social checks vs you.",
            "deafened":     "Can't hear; fails checks that require hearing.",
            "exhaustion":   "Six levels; each adds cumulative penalties.",
            "frightened":   "Disadv on checks/attacks; can't move closer to source of fear.",
            "grappled":     "Speed 0; ends if grappler is incapacitated or you are moved.",
            "incapacitated":"Can't take actions or reactions.",
            "invisible":    "Can't be seen; attacks vs you have disadv; your attacks have adv.",
            "paralyzed":    "Incapacitated; auto‑fail STR/DEX saves; attacks vs you have adv; melee crits.",
            "petrified":    "Turned to solid; incapacitated; STR/DEX saves fail; resist all damage.",
            "poisoned":     "Disadvantage on attack rolls and ability checks.",
            "prone":        "Only crawl or stand; melee vs you adv, ranged vs you disadv; your attacks disadv.",
            "restrained":   "Speed 0; attacks vs you adv; your attacks and DEX saves disadv.",
            "stunned":      "Incapacitated; can't move; STR/DEX saves auto‑fail; attacks vs you adv.",
            "unconscious":  "Incapacitated; prone; STR/DEX saves auto‑fail; melee hits are crits.",
        }

        # Get conditions list from SRD_rules["Conditions and Statuses"]["subsections"]
        cond_section = SRD_rules.get("Conditions and Statuses") or SRD_rules.get("conditions")
        subsections = cond_section.keys() if cond_section else []

        for sub in subsections:
            idx = sub.lower()

            row = QWidget()
            row_layout = QHBoxLayout()
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(4)
            row.setLayout(row_layout)

            cb = QCheckBox(sub)
            cb.setStyleSheet(f"color: {SALMON};")
            # initialize from character.conditions if present
            if hasattr(character, "conditions") and idx in character.conditions:
                cb.setChecked(bool(character.conditions[idx]))

            cb.toggled.connect(
                lambda checked, cond_idx=idx, ch=character: self._on_condition_toggled(ch, cond_idx, checked)
            )
            self.condition_checkboxes[idx] = cb
            row_layout.addWidget(cb, stretch=0)

            # description label
            desc_text = condition_descriptions.get(idx, "")
            desc_label = QLabel(desc_text)
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet("color: #CCCCCC; font-size: 10px;")
            row_layout.addWidget(desc_label, stretch=1)

            scroll_layout.addWidget(row)

        scroll_layout.addStretch(1)
        scroll_widget.setLayout(scroll_layout)
        scroll.setWidget(scroll_widget)

        main_layout.addWidget(scroll)
        central.setLayout(main_layout)
        self.setCentralWidget(central)

    def _on_condition_toggled(self, character, cond_idx: str, checked: bool):
        # keep Character.conditions dict in sync
        if not hasattr(character, "conditions") or character.conditions is None:
            character.conditions = {}
        character.conditions[cond_idx] = checked

class SpellSlotsWindow(QMainWindow):
    """Display and manage spell slots for a character with checkbuttons."""
    def __init__(self, character, parent=None):
        super().__init__(parent)
        self.character = character
        # self.setWindowTitle(f"Spell Slots - {getattr(character, 'name', 'Unknown')}")
        self.resize(400, 400)

        central = QWidget()
        main_layout = QVBoxLayout()

        # Title label
        title = QLabel(f"Spell Slots for {character.name}")
        title.setStyleSheet(f"color: {GOLD}; font-weight: bold;")
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)

        # Scroll area for spell slots
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()

        # Store checkboxes for later reference if needed
        self.slot_checkboxes = {}

        # Create a checkbox for each spell slot level
        spell_slots = getattr(character, "spell_slots", {})
        spells_prepared = getattr(character, "spells_known", [])

        # Special handling for Warlocks: all known spells are cast at the highest
        # available spell slot level. Compute the highest slot level with >0 slots.
        is_warlock = getattr(character, "class_name", "").lower() == "warlock"
        highest_slot_level = None
        if is_warlock:
            nonzero_levels = [
                lvl for lvl in range(1, 10)
                if spell_slots.get(f"spell_slots_level_{lvl}", 0) > 0
            ]
            highest_slot_level = max(nonzero_levels) if nonzero_levels else None

        for level in range(1, 10):  # Spell levels 1-9
            # If warlock, only show the highest slot level
            if is_warlock and highest_slot_level is not None and level != highest_slot_level:
                continue

            slot_key = f"spell_slots_level_{level}"
            total_slots = spell_slots.get(slot_key, 0)

            if total_slots > 0:
                # Level header (for warlock, indicate that all known spells are shown)
                if is_warlock:
                    level_label = QLabel(f"<span style='color:{GOLD};'>Level {level} Spells (Warlock - all known spells) ({total_slots} total)</span>")
                else:
                    level_label = QLabel(f"<span style='color:{GOLD};'>Level {level} Spells ({total_slots} total)</span>")
                level_label.setTextFormat(Qt.RichText)
                scroll_layout.addWidget(level_label)

                # For warlocks, show all known spells regardless of their individual level.
                if is_warlock:
                    spells_of_level = spells_prepared[:]  # all known spells
                else:
                    spells_of_level = [s for s in spells_prepared if s.level == level]
                spell_names = [s.name for s in spells_of_level]

                # Create checkbox + combobox for each slot
                level_checkboxes = []
                for slot_num in range(1, total_slots + 1):
                    checkbox_key = f"level_{level}_slot_{slot_num}"

                    # Horizontal container for checkbox + combobox
                    slot_container = QWidget()
                    slot_layout = QHBoxLayout()
                    slot_layout.setContentsMargins(0, 0, 0, 0)
                    slot_container.setLayout(slot_layout)

                    # Checkbox (no text)
                    checkbox = QCheckBox()
                    checkbox.setStyleSheet(f"color: {ORANGE};")
                    slot_layout.addWidget(checkbox, stretch=0)

                    # Combobox with prepared spells
                    combobox = QComboBox()
                    combobox.addItems(["-- Select Spell --"] + spell_names)
                    combobox.setStyleSheet(f"color: {ORANGE};")
                    slot_layout.addWidget(combobox, stretch=1)

                    scroll_layout.addWidget(slot_container)
                    level_checkboxes.append(checkbox)
                    self.slot_checkboxes[checkbox_key] = checkbox

        # Clear button to reset all checkboxes
        clear_button = QPushButton("Clear All Slots")
        clear_button.setStyleSheet(f"color: {ROYAL_BLUE};")
        clear_button.clicked.connect(self.clear_all_slots)
        scroll_layout.addWidget(clear_button)

        scroll_layout.addStretch(1)
        scroll_widget.setLayout(scroll_layout)
        scroll.setWidget(scroll_widget)

        main_layout.addWidget(scroll)
        central.setLayout(main_layout)
        self.setCentralWidget(central)

    def clear_all_slots(self):
        """Uncheck all spell slot checkboxes."""
        for checkbox in self.slot_checkboxes.values():
            checkbox.setChecked(False)

class SpellListWindow(QMainWindow):
    def __init__(self, character, parent=None):
        super().__init__(parent)
        self.character = character
        self.setWindowTitle(f"Spells - {getattr(character, 'name', 'Unknown')}")
        # initial size (resizable)
        self.resize(800, 800)  # width, height in pixels

        central = QWidget()
        main_layout = QVBoxLayout()

        # header = QLabel(f"<span style='color:green;'>Spells known by {getattr(character, 'name', 'Unknown')}:</span>")
        # main_layout.addWidget(header)

        # Scroll area in case there are many spells
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()

        # Build one "button + dropdown text" per spell
        spells = getattr(character, "spells_known", [])
        cantrips = getattr(character, "cantrips_known", [])

         # --- First: cantrips (level 0) ---
        if cantrips:
            # cantrips header
            lvl_label = QLabel(
                f"<span style='color:{GOLD};'>Cantrips</span>"
            )
            lvl_label.setTextFormat(Qt.RichText)
            lvl_label.setAlignment(Qt.AlignCenter)  # Set alignment to center
            scroll_layout.addWidget(lvl_label)

        for spell in cantrips:
            # SPELLS object
            spell_name = getattr(spell, "name", "Unknown cantrip")

            # Use character helper to get same formatting as show_spells_known()
            if hasattr(character, "format_single_spell"):
                spell_desc = character.format_single_spell(spell)
            else:
                spell_desc = getattr(spell, "description", "No description available.")

            # Container for each cantrip
            spell_container = QWidget()
            spell_layout = QVBoxLayout()
            spell_layout.setContentsMargins(0,0,0,0)
            spell_layout.setSpacing(20)
            spell_container.setLayout(spell_layout)

            btn = QPushButton(spell_name)
            btn.setStyleSheet(f"color: {ORANGE};")
            btn.setCheckable(True)

            html_desc = format_str_html(spell_desc)
            desc_label = QLabel(html_desc)
            desc_label.setWordWrap(True)
            desc_label.setVisible(False)

            btn.toggled.connect(lambda checked, lbl=desc_label: lbl.setVisible(checked))

            spell_layout.addWidget(btn)
            spell_layout.addWidget(desc_label)
            scroll_layout.addWidget(spell_container)

        # --- Then: level 1+ spells, grouped by level ---
        # group spells by their level attribute
        spells_by_level = {}
        for spell in spells:
            level = getattr(spell, "level", 0)
            spells_by_level.setdefault(level, []).append(spell)

        # iterate levels in order
        for level in sorted(spells_by_level.keys()):
            # level label
            lvl_label = QLabel(
                f"<span style='color:{GOLD};'>Level {level} spells</span>"
            )
            lvl_label.setTextFormat(Qt.RichText)
            lvl_label.setAlignment(Qt.AlignCenter)  # Set alignment to center
            scroll_layout.addWidget(lvl_label)

            for spell in spells_by_level[level]:
                spell_name = getattr(spell, "name", "Unknown spell")

                if hasattr(character, "format_single_spell"):
                    spell_desc = character.format_single_spell(spell)
                else:
                    spell_desc = getattr(spell, "description", "No description available.")

                spell_container = QWidget()
                spell_layout = QVBoxLayout()
                spell_layout.setContentsMargins(0,0,0,0)
                spell_layout.setSpacing(20)
                spell_container.setLayout(spell_layout)

                btn = QPushButton(spell_name)
                btn.setStyleSheet(f"color: {ORANGE};")
                btn.setCheckable(True)

                html_desc = format_str_html(spell_desc)
                desc_label = QLabel(html_desc)
                desc_label.setWordWrap(True)
                desc_label.setVisible(False)

                btn.toggled.connect(lambda checked, lbl=desc_label: lbl.setVisible(checked))

                spell_layout.addWidget(btn)
                spell_layout.addWidget(desc_label)
                scroll_layout.addWidget(spell_container)

        scroll_layout.addStretch(1)
        scroll_widget.setLayout(scroll_layout)
        scroll.setWidget(scroll_widget)

        main_layout.addWidget(scroll)
        central.setLayout(main_layout)
        self.setCentralWidget(central)


# Subclass QMainWindow to customize your application's main window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle(f"DND game manager")
        # Initial main window size (width, height). Adjust as you prefer.
        self.resize(1200, 800)
        # Keep a reasonable minimum so the layout doesn't collapse.
        self.setMinimumSize(800, 600)
        
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
        # self.set  Size(QSize(400, 300))
                
        self._spell_windows = {}  # key: character.name, value: SpellListWindow instance
        self._spell_slots_windows = {}  # key: character.name, value: SpellSlotsWindow instance
        self._item_windows = {}   # key: character.name, value: ItemListWindow instance
        self._features_windows = {}  # key: character.name -> FeaturesWindow
        self._saving_throws_windows = {}  # name -> SavingThrowsWindow
        self._skills_windows = {}  # name -> SkillsWindow
        self._invocations_windows = {}  # key: character.name, value: InvocationsWindow instance
        self._metamagic_windows = {}  # key: character.name, value: MetamagicWindow instance
        self._status_windows = {}  # key: character.name, value: StatusWindow instance

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
        self.labelsAndLineEditDexAttackBonusList = []  # New list for Dexterity Attack Bonus
        self.labelsAndLineEditSpellAttackBonusList = []  # New list for Spell Attack Bonus
        self.labelsAndLineEditSpellDCList = []  # New list for Spell DC

        self.buttonsStatusListList = []  # New list for status buttons
        self.buttonsSkillsListList = []  # New list for skills buttons
        self.buttonsSavingThrowsListList = []  # New list for saving throws buttons
        self.buttonsFeatureListList = []  # New list for feature list buttons
        self.buttonsSpellListList = []  # New list for spell list buttons
        self.buttonsSpellSlotsListList = []  # New list for spell slots buttons
        self.buttonsInvocationsListList = [] # New list for invocations list buttons (Warlock only)
        self.buttonsMetamagicListList = [] # New list for metamagic list buttons (Sorcerer only)
        self.buttonsItemListList = []  # New list for item list buttons

        # Set fixed width for all labels and line edits
        FIXED_WIDTH = 125  # Define a fixed width for all labels and line edits

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
                f"<span style='color:green;'>Speed: feet </span>",
                f"{getattr(character, 'speed', 'N/A')}"
            )
            speed_widget.layout_hbox.setSpacing(2)
            speed_widget.layout_hbox.setContentsMargins(0, 0, 0, 0)
            speed_widget.label.setFixedWidth(FIXED_WIDTH)
            # speed_widget.line_edit.setFixedWidth(FIXED_WIDTH)
            speed_widget.line_edit.setAlignment(Qt.AlignCenter)  # Set alignment to center
            self.labelsSpeedList.append(speed_widget)

            # Max HP label
            max_hp_widget = LabelandLineEdit(
                f"<span style='color:green;'>Max HP: </span>",
                f"{getattr(character, 'max_hp', 'N/A')}"
            )
            max_hp_widget.layout_hbox.setSpacing(2)
            max_hp_widget.layout_hbox.setContentsMargins(0, 0, 0, 0)
            max_hp_widget.label.setFixedWidth(FIXED_WIDTH)
            # max_hp_widget.line_edit.setFixedWidth(FIXED_WIDTH)
            max_hp_widget.line_edit.setAlignment(Qt.AlignCenter)  # Set alignment to center
            self.labelsMaxHPList.append(max_hp_widget)

            # Current HP label
            current_hp_widget = LabelandLineEdit(
                f"<span style='color:{ORANGE};'>Current HP: </span>",
                str(getattr(character, 'current_hp', 'N/A'))
            )
            current_hp_widget.layout_hbox.setSpacing(2)
            current_hp_widget.layout_hbox.setContentsMargins(0, 0, 0, 0)
            current_hp_widget.label.setFixedWidth(FIXED_WIDTH)
            # current_hp_widget.line_edit.setFixedWidth(FIXED_WIDTH)
            current_hp_widget.line_edit.setAlignment(Qt.AlignCenter)  # Set alignment to center
            self.labelAndLineEditHP.append(current_hp_widget)

            # Armor Class label
            armor_class_widget = LabelandLineEdit(
                f"<span style='color:green;'>Armor Class: </span>",
                f"{getattr(character, 'armor_class', 'N/A')}"
            )
            armor_class_widget.layout_hbox.setSpacing(2)
            armor_class_widget.layout_hbox.setContentsMargins(0, 0, 0, 0)
            armor_class_widget.label.setFixedWidth(FIXED_WIDTH)
            # armor_class_widget.line_edit.setFixedWidth(FIXED_WIDTH)
            armor_class_widget.line_edit.setAlignment(Qt.AlignCenter)  # Set alignment to center
            self.labelsArmorClassList.append(armor_class_widget)

            # Initiative label
            initiative_widget = LabelandLineEdit(
                f"<span style='color:green;'>Initiative: </span>",
                f"{getattr(character, 'initiative', 'N/A')}"
            )
            initiative_widget.label.setFixedWidth(FIXED_WIDTH)
            # initiative_widget.line_edit.setFixedWidth(FIXED_WIDTH)
            initiative_widget.line_edit.setAlignment(Qt.AlignCenter)  # Set alignment to center
            self.labelsInitiativeList.append(initiative_widget)

            # Proficiency Bonus label
            prof_bonus_widget = LabelandLineEdit(
                f"<span style='color:green;'>Proficiency Bonus: </span>",
                f"{getattr(character, 'prof_bonus', 'N/A')}"
            )
            prof_bonus_widget.label.setFixedWidth(FIXED_WIDTH)
            # prof_bonus_widget.line_edit.setFixedWidth(FIXED_WIDTH)
            prof_bonus_widget.line_edit.setAlignment(Qt.AlignCenter)  # Set alignment to center
            self.labelsProfBonusList.append(prof_bonus_widget)

            # Strength Attack Bonus label
            str_attack_bonus_widget = LabelandLineEdit(
                f"<span style='color:green;'>STR Atk. Bonus: </span>",
                str(character.get_ability_modifier(character.strength) + character.prof_bonus)
            )
            str_attack_bonus_widget.label.setFixedWidth(FIXED_WIDTH)
            # str_attack_bonus_widget.line_edit.setFixedWidth(FIXED_WIDTH)
            str_attack_bonus_widget.line_edit.setAlignment(Qt.AlignCenter)  # Set alignment to center
            self.labelsAndLineEditStrAttackBonusList.append(str_attack_bonus_widget)

            # Dexterity Attack Bonus label
            dex_attack_bonus_widget = LabelandLineEdit(
                f"<span style='color:green;'>DEX Atk. Bonus: </span>",
                str(character.get_ability_modifier(character.dexterity) + character.prof_bonus)
            )
            dex_attack_bonus_widget.label.setFixedWidth(FIXED_WIDTH)
            # dex_attack_bonus_widget.line_edit.setFixedWidth(FIXED_WIDTH)
            dex_attack_bonus_widget.line_edit.setAlignment(Qt.AlignCenter)  # Set alignment to center
            self.labelsAndLineEditDexAttackBonusList.append(dex_attack_bonus_widget)

            # Spell Attack Bonus label
            if character.spellcasting_stat == 'wisdom':
                mod = character.get_ability_modifier(character.wisdom) + character.prof_bonus
            elif character.spellcasting_stat == 'intelligence':
                mod = character.get_ability_modifier(character.intelligence) + character.prof_bonus
            elif character.spellcasting_stat == 'charisma':
                mod = character.get_ability_modifier(character.charisma) + character.prof_bonus
            else:
                mod = "N/A"
            spell_attack_bonus_widget = LabelandLineEdit(
                f"<span style='color:green;'>Spell Atk. Bonus: </span>", str(mod))
            spell_attack_bonus_widget.label.setFixedWidth(FIXED_WIDTH)
            # spell_attack_bonus_widget.line_edit.setFixedWidth(FIXED_WIDTH)
            spell_attack_bonus_widget.line_edit.setAlignment(Qt.AlignCenter)  # Set alignment to center
            self.labelsAndLineEditSpellAttackBonusList.append(spell_attack_bonus_widget)
            if not character.spellcasting_stat:
                spell_attack_bonus_widget.line_edit.setEnabled(False)

            # Spell Attack Bonus label
            if character.spellcasting_stat == 'wisdom':
                mod = character.get_ability_modifier(character.wisdom) + character.prof_bonus + 10
            elif character.spellcasting_stat == 'intelligence':
                mod = character.get_ability_modifier(character.intelligence) + character.prof_bonus + 10
            elif character.spellcasting_stat == 'charisma':
                mod = character.get_ability_modifier(character.charisma) + character.prof_bonus + 10
            else:
                mod = "N/A"
            spell_dc_widget = LabelandLineEdit(
                f"<span style='color:green;'>Spell DC: </span>", str(mod))
            spell_dc_widget.label.setFixedWidth(FIXED_WIDTH)
            # spell_dc_widget.line_edit.setFixedWidth(FIXED_WIDTH)
            spell_dc_widget.line_edit.setAlignment(Qt.AlignCenter)  # Set alignment to center
            self.labelsAndLineEditSpellDCList.append(spell_dc_widget)
            if not character.spellcasting_stat:
                spell_dc_widget.line_edit.setEnabled(False)

            # Status Button (placed above all other buttons)
            status_button = QPushButton("Statuses")
            status_button.setStyleSheet(f"color: {SALMON};")
            self.buttonsStatusListList.append(status_button)
            status_button.clicked.connect(
                lambda _, c=character: self.open_status_window(c)
            )

            # Saving Throws Button
            saving_throws_button = QPushButton("Saving Throws")
            saving_throws_button.setStyleSheet(f"color: {GOLDEN_ROD};")  # Set the text color to ROYAL_BLUE
            self.buttonsSavingThrowsListList.append(saving_throws_button)
            saving_throws_button.clicked.connect(
                lambda _, c=character: self.open_saving_throws_window(c)
            )

            # Skills Button
            skills_button = QPushButton("Skills")
            skills_button.setStyleSheet(f"color: {TEAL};")  # Set the text color to ROYAL_BLUE
            self.buttonsSkillsListList.append(skills_button)
            skills_button.clicked.connect(
                lambda _, c=character: self.open_skills_window(c)
            )

            # Feature List Button
            features_button = QPushButton("Features")
            features_button.setStyleSheet(f"color: cyan;")  # Set the text color to ROYAL_BLUE
            self.buttonsFeatureListList.append(features_button)
            features_button.clicked.connect(
                lambda _, c=character: self.open_features_window(c)
            )
            
            # Spell List Button
            spell_list_button = QPushButton(f"Show {character.name}'s Spells")
            spell_list_button.setStyleSheet(f"color: {ROYAL_BLUE};")  # Set the text color to ROYAL_BLUE
            self.buttonsSpellListList.append(spell_list_button)
            if not character.spells_known:
                spell_list_button.setEnabled(False)  # Disable the button if there are no spells known

            # connect to open spell list window for this character
            spell_list_button.clicked.connect(
                lambda _, c=character: self.open_spell_list_window(c)
            )

            # Spell Slots button (new)
            spell_slots_button = QPushButton(f"Show {character.name}'s Spell Slots")
            spell_slots_button.setStyleSheet(f"color: {LIGHT_MAGENTA};")  # Set the text color to LIGHT_MAGENTA
            self.buttonsSpellSlotsListList.append(spell_slots_button)
            spell_slots = getattr(character, "spell_slots", {})
            total_slots = sum(v for k, v in spell_slots.items() if k.startswith("spell_slots_level_"))
            if total_slots == 0:
                spell_slots_button.setEnabled(False)  # Disable if no spell slots

            # connect to open spell slots window for this character
            spell_slots_button.clicked.connect(
                lambda _, c=character: self.open_spell_slots_window(c)
            )

            # Item list button (new)
            item_list_button = QPushButton(f"Show {character.name}'s Inventory")
            item_list_button.setStyleSheet(f"color:yellow;")  # Set the text color to yellow
            self.buttonsItemListList.append(item_list_button)
            item_list_button.clicked.connect(
                lambda _, c=character: self.open_item_list_window(c)
            )

            # Invocations Button
            if character.class_name == 'Warlock':
                invocations_button = QPushButton(f"Show {character.name}'s Invocations")
                invocations_button.setStyleSheet(f"color: {TEAL};")  # Set the text color to TEAL
                self.buttonsInvocationsListList.append(invocations_button)
                if not character.spells_known:
                    invocations_button.setEnabled(False)  # Disable the button if there are no spells known
            
                #  connect to open invocations window for this character
                invocations_button.clicked.connect(
                    lambda _, c=character: self.open_invocations_window(c)
                )

            # Metamagic Button
            if character.class_name == 'Sorcerer':
                metamagic_button = QPushButton(f"Show {character.name}'s Metamagic Feats")
                metamagic_button.setStyleSheet(f"color: {TEAL};")  # Set the text color to TEAL
                self.buttonsMetamagicListList.append(metamagic_button)
                if not character.spells_known:
                    metamagic_button.setEnabled(False)  # Disable the button if there are no spells known

                # connect to open metamagic window for this character
                metamagic_button.clicked.connect(
                    lambda _, c=character: self.open_metamagic_window(c)
                )

            # Item list button (new)
            item_list_button = QPushButton(f"Show {character.name}'s Inventory")
            item_list_button.setStyleSheet(f"color:yellow;")  # Set the text color to yellow
            self.buttonsItemListList.append(item_list_button)
            item_list_button.clicked.connect(
                lambda _, c=character: self.open_item_list_window(c)
            )

            # connect to open spell list window for this character
            spell_list_button.clicked.connect(
                lambda _, c=character: self.open_spell_list_window(c)
            )

            # Add widgets and button to layout
            layout = QVBoxLayout()
            # Reduce vertical spacing between LabelandLineEdit widgets and buttons
            layout.setSpacing(4)                 # default is larger; 4 is tighter
            layout.setContentsMargins(0, 0, 0, 0)  # small margins so widgets are closer to each other
            layout.addWidget(self.labelsNameList[-1])  # Add name widget
            layout.addWidget(self.labelsClassLevelList[-1])  # Add class and level widget
            layout.addWidget(self.labelsSpeedList[-1])  # Add speed widget
            layout.addWidget(self.labelsMaxHPList[-1])  # Add max HP widget
            layout.addWidget(self.labelAndLineEditHP[-1])  # Add current HP widget
            layout.addWidget(self.labelsArmorClassList[-1])  # Add armor class widget
            layout.addWidget(self.labelsInitiativeList[-1])  # Add initiative widget
            layout.addWidget(self.labelsProfBonusList[-1])  # Add proficiency bonus widget
            layout.addWidget(self.labelsAndLineEditStrAttackBonusList[-1])  # Add strength attack bonus widget
            layout.addWidget(self.labelsAndLineEditDexAttackBonusList[-1])  # Add dexterity attack bonus widget
            layout.addWidget(self.labelsAndLineEditSpellAttackBonusList[-1])  # Add spell attack bonus widget
            layout.addWidget(self.labelsAndLineEditSpellDCList[-1])  # Add spell DC widget
            
            # Buttons (Status first)
            layout.addWidget(self.buttonsStatusListList[-1])      # Status
            layout.addWidget(self.buttonsSavingThrowsListList[-1])  # Saving throws
            layout.addWidget(self.buttonsSkillsListList[-1])        # Skills
            layout.addWidget(self.buttonsFeatureListList[-1])       # Features
            layout.addWidget(self.buttonsSpellListList[-1])         # Spells
            layout.addWidget(self.buttonsSpellSlotsListList[-1])    # Spell Slots
            if character.class_name == 'Warlock':
                layout.addWidget(self.buttonsInvocationsListList[-1])
            if character.class_name == 'Sorcerer':
                layout.addWidget(self.buttonsMetamagicListList[-1])
            layout.addWidget(self.buttonsItemListList[-1])          # Inventory

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

        self._dice_window = None
        self._feet_to_meters_window = None
        self._spells_by_level_window = None
        self._monsters_by_cr_window = None
        self._rules_window = None
        self._create_menu()

    def _create_menu(self):
        menubar = self.menuBar()
        # Tools menu (existing)
        tools_menu = menubar.addMenu("Tools")

        open_dice_action = QAction("Dice Roller", self)
        open_dice_action.triggered.connect(self.open_dice_window)
        tools_menu.addAction(open_dice_action)

        # Feet to meters converter
        open_ftm_action = QAction("Feet to Meters Converter", self)
        open_ftm_action.triggered.connect(self.open_feet_to_meters_window)
        tools_menu.addAction(open_ftm_action)

        # New: Lists menu (no actions wired yet)
        lists_menu = menubar.addMenu("Lists")
        
        spells_by_level_action = QAction("Spell List by Level", self)
        spells_by_level_action.triggered.connect(self.open_spells_by_level_window)
        lists_menu.addAction(spells_by_level_action)

        monsters_by_cr_action = QAction("Monster List by CR", self)
        monsters_by_cr_action.triggered.connect(self.open_monsters_by_cr_window)
        lists_menu.addAction(monsters_by_cr_action)

        # You can add actions later if you decide how to pick a character:
        # example (commented out intentionally, because no character passed):
        # spells_action = QAction("Spells", self)
        # lists_menu.addAction(spells_action)

        # New: Rules menu (no character info needed)
        rules_menu = menubar.addMenu("Rules")

        # open_rules_action = QAction("Show Rules (console)", self)
        # open_rules_action.triggered.connect(show_rules)  # uses your existing function
        # rules_menu.addAction(open_rules_action)

        # New: GUI rules view
        open_rules_view_action = QAction("Rules view", self)
        open_rules_view_action.triggered.connect(self.open_rules_window)
        rules_menu.addAction(open_rules_view_action)

    def open_saving_throws_window(self, character):
        name = getattr(character, "name", "Unknown")
        if name not in self._saving_throws_windows:
            self._saving_throws_windows[name] = SavingThrowsWindow(character, self)
        win = self._saving_throws_windows[name]
        win.show()
        win.raise_()
        win.activateWindow()

    def open_skills_window(self, character):
        name = getattr(character, "name", "Unknown")
        if name not in self._skills_windows:
            self._skills_windows[name] = SkillsWindow(character, self)
        win = self._skills_windows[name]
        win.show()
        win.raise_()
        win.activateWindow()

    def open_features_window(self, character):
        name = getattr(character, "name", "Unknown")
        if name not in self._features_windows:
            self._features_windows[name] = FeaturesWindow(character, self)
        win = self._features_windows[name]
        win.show()
        win.raise_()
        win.activateWindow()

    def open_dice_window(self):
        if self._dice_window is None:
            self._dice_window = DiceWindow(self)
        self._dice_window.show()
        self._dice_window.raise_()
        self._dice_window.activateWindow()

    def open_feet_to_meters_window(self):
        if self._feet_to_meters_window is None:
            self._feet_to_meters_window = FeetToMetersWindow(self)
        self._feet_to_meters_window.show()
        self._feet_to_meters_window.raise_()
        self._feet_to_meters_window.activateWindow()

    def open_spells_by_level_window(self):
        if self._spells_by_level_window is None:
            self._spells_by_level_window = SpellsByLevelWindow(self)
        self._spells_by_level_window.show()
        self._spells_by_level_window.raise_()
        self._spells_by_level_window.activateWindow()

    def open_monsters_by_cr_window(self):
        if self._monsters_by_cr_window is None:
            self._monsters_by_cr_window = MonstersByCRWindow(self)
        self._monsters_by_cr_window.show()
        self._monsters_by_cr_window.raise_()
        self._monsters_by_cr_window.activateWindow()

    def open_item_list_window(self, character):
        name = getattr(character, "name", "Unknown")
        if name not in self._item_windows:
            self._item_windows[name] = ItemListWindow(character, self)
        win = self._item_windows[name]
        win.show()
        win.raise_()
        win.activateWindow()

    def open_spell_list_window(self, character):
        name = getattr(character, "name", "Unknown")
        if name not in self._spell_windows:
            self._spell_windows[name] = SpellListWindow(character, self)
        win = self._spell_windows[name]
        win.show()
        win.raise_()
        win.activateWindow()

    def open_spell_slots_window(self, character):
        name = getattr(character, "name", "Unknown")
        if name not in self._spell_slots_windows:
            self._spell_slots_windows[name] = SpellSlotsWindow(character, self)
        win = self._spell_slots_windows[name]
        win.show()
        win.raise_()
        win.activateWindow()

    def open_invocations_window(self, character):
        name = getattr(character, "name", "Unknown")
        if name not in self._invocations_windows:
            self._invocations_windows[name] = InvocationsWindow(character, self)
        win = self._invocations_windows[name]
        win.show()
        win.raise_()
        win.activateWindow()

    def open_metamagic_window(self, character):
        name = getattr(character, "name", "Unknown")
        if name not in self._metamagic_windows:
            self._metamagic_windows[name] = MetamagicWindow(character, self)
        win = self._metamagic_windows[name]
        win.show()
        win.raise_()
        win.activateWindow()

    def open_rules_window(self):
        if self._rules_window is None:
            self._rules_window = RulesWindow(self)
        self._rules_window.show()
        self._rules_window.raise_()
        self._rules_window.activateWindow()

    def open_status_window(self, character):
        name = getattr(character, "name", "Unknown")
        if name not in self._status_windows:
            self._status_windows[name] = StatusWindow(character, self)
        win = self._status_windows[name]
        win.show()
        win.raise_()
        win.activateWindow()

app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()