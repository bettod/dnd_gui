import argparse
import json
from pprint import pprint
from datetime import datetime
import code
import os
import signal
import threading
import time
if os.name == "nt":
    from pyreadline3 import Readline
    readline = Readline()
else:
    import readline
import rlcompleter
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

# CLASS_NAMES = list(CLASSES.keys())

def signal_handler(signum, frame):
    global is_exit
    is_exit = True
    # logger.info (f"receive a signal {signum} is_exit = {is_exit}")
    # self._recv_thread.join()
    # logger.info("RCV Thread exited")
    sys.exit()

def help():
    print('autocompletion with TAB is your friend')
    print("type <a Character's name>.help()")
    print('type show_rules() for the rules')
    print('type show_monster(<name>), show_monster_list(), show_monster_by_rating()')
    print('type show_spell(<name>), show_spell_list(), show_spells_by_class_level(<class>, <level>)')

def main():
    """
    main
    ----
    Entry point for the interactive console. Sets up the instance, signal handlers,
    and launches an interactive Python shell for user commands.
    """
    namespace = globals()

    # signal.signal(signal.SIGTSTP, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    readline.set_completer(rlcompleter.Completer(namespace).complete)
    readline.parse_and_bind("tab: complete")
    code.InteractiveConsole(namespace).interact(
        banner=f"DnD interactive console\n", exitmsg=""
    )


if __name__ == "__main__":
    main()
