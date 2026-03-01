from character import Character
# from classes import CLASSES
from SRD import SRD, SRD_classes, SRD_class_levels, SRD_rules, SRD_species
from spellcasting import SPELLS
from equipment import SRD_equipment, Item
from magicitems import SRD_magicitems, MagicItem
from feats import SRD_feats, FEATS
    
Hrothgeirr = Character(classs=SRD_classes['barbarian'], 
                                    name='Hrothgeirr',
                                    gender='Male',
                                    description='Cannibal viking, still better than a pedophile viking',
                                    level=5,
                                    initiative=1,
                                    strength=18,
                                    dexterity=12,
                                    constitution=13,
                                    intelligence=10,
                                    wisdom=9,
                                    charisma=9,
                                    max_hp=52,
                                    current_hp=52,
                                    armor_class=17,
                                    speciess=SRD_species['human']
                                    )

# Spell Book
#AHAHHAHAHAH

# Items
for iii in range(len(Hrothgeirr.inventory)):
     _ = Hrothgeirr.inventory.pop()   # remove all items
Hrothgeirr.give_item('battleaxe')
Hrothgeirr.inventory[0].name = 'Axe of the lightning'
Hrothgeirr.inventory[0].damage['damage_dice'] = '1d6+1'
Hrothgeirr.inventory[0].two_handed_damage['damage_dice'] = '1d10+1'
Hrothgeirr.inventory[0].special = '+1 weapon'
Hrothgeirr.give_item('greataxe')
Hrothgeirr.inventory[-1].name = 'Great Axe of the Angry Dane'
Hrothgeirr.inventory[-1].damage['damage_dice'] = '1d12+1'
Hrothgeirr.inventory[-1].special = '+1 weapon'

Hrothgeirr.give_item('spear')
Hrothgeirr.give_item('javelin')

Hrothgeirr.give_item('plate-armor')
Hrothgeirr.give_item('shield')

Hrothgeirr.give_random_item('various shit')

# Feats
# Hrothgeirr.give_feat('telekinetic')

# Skills
Hrothgeirr.set_skill_proficiency('animal-handling')
Hrothgeirr.set_skill_proficiency('acrobatics')
Hrothgeirr.set_skill_proficiency('survival')
Hrothgeirr.set_skill_bonuses()

# Saving throws
# for key in Hrothgeirr.saving_throws.keys():
    #  Hrothgeirr.saving_throws[key] += 1