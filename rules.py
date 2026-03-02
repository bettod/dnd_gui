from SRD import SRD_rules
from pprint import pprint
from termcolor import colored, cprint
import json

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def show_rules():
    iii = 0
    first_depth_keys = []
    print(bcolors.OKCYAN + "#################################" + bcolors.ENDC)
    for key in SRD_rules.keys():
        print(str(iii) + ': ' + key)
        iii += 1
        first_depth_keys.append(key)
    key_selection = input("Which key do you want?    ")
    first_key = first_depth_keys[int(key_selection)]
    print(bcolors.OKCYAN + "#################################" + bcolors.ENDC)
    iii = 0
    second_depth_keys = []
    print(bcolors.OKCYAN + "#################################" + bcolors.ENDC)
    for key in SRD_rules[first_key].keys():
        print(str(iii) + ': ' + key)
        iii += 1
        second_depth_keys.append(key)
    key_selection = input("Which key do you want?    ")
    second_key = second_depth_keys[int(key_selection)]
    splitted = SRD_rules[first_key][second_key].split('#')
    splitted = list(filter(None, splitted))
    print(bcolors.OKCYAN + "#################################" + bcolors.ENDC)
    third_depth_keys = []
    print(bcolors.OKCYAN + "#################################" + bcolors.ENDC)
    for jjj in range(len(splitted)):
        print(str(jjj) + ': ' + splitted[jjj].split('\n')[0])
    key_selection = input("Which key do you want?    ")

    print(bcolors.OKCYAN + "#################################" + bcolors.ENDC)
    # pprint(SRD.SRD_rules[first_key][second_key], width=200)
    # print(splitted[int(key_selection)].replace('#', bcolors.OKBLUE + '#' + bcolors.ENDC))
    print(splitted[int(key_selection)].replace('#', bcolors.OKBLUE + '#' + bcolors.ENDC))
    print(bcolors.OKCYAN + "###############################" + bcolors.ENDC)
