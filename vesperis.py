from character import Character
# from classes import CLASSES
from SRD import SRD, SRD_classes, SRD_class_levels, SRD_rules, SRD_species
from spellcasting import SPELLS
from equipment import SRD_equipment, Item
from magicitems import SRD_magicitems, MagicItem
from feats import SRD_feats, FEATS
    
Vesperis = Character(classs=SRD_classes['twilight-cleric'], 
                                    name='Vesperis',
                                    gender='Female',
                                    description='Blue healer lady',
                                    level=5,
                                    initiative=0,
                                    strength=16,
                                    dexterity=11,
                                    constitution=15,
                                    intelligence=12,
                                    wisdom=19,
                                    charisma=14,
                                    max_hp=39,
                                    current_hp=39,
                                    armor_class=19,
                                    speciess=SRD_species['protector-aasimar']
                                    )

# Spell Book
Vesperis.cantrips_known.append(SPELLS['light'])
Vesperis.cantrips_known.append(SPELLS['guidance'])
Vesperis.cantrips_known.append(SPELLS['sacred-flame'])
Vesperis.cantrips_known.append(SPELLS['toll-the-dead'])
Vesperis.cantrips_known.append(SPELLS['thaumaturgy'])
Vesperis.cantrips_known.append(SPELLS['mage-hand'])
Vesperis.spells_known.append(SPELLS['faerie-fire'])
Vesperis.spells_known.append(SPELLS['sleep'])
Vesperis.spells_known.append(SPELLS['bless'])
Vesperis.spells_known.append(SPELLS['guiding-bolt'])
Vesperis.spells_known.append(SPELLS['healing-word'])
Vesperis.spells_known.append(SPELLS['cure-wounds'])
Vesperis.spells_known.append(SPELLS['shield-of-faith'])
Vesperis.spells_known.append(SPELLS['see-invisibility'])
Vesperis.spells_known.append(SPELLS['moonbeam'])
Vesperis.spells_known.append(SPELLS['prayer-of-healing'])
Vesperis.spells_known.append(SPELLS['spiritual-weapon'])
Vesperis.spells_known.append(SPELLS['aura-of-vitality'])
Vesperis.spells_known.append(SPELLS['tiny-hut'])

# Items
for iii in range(len(Vesperis.inventory)):
     _ = Vesperis.inventory.pop()   # remove all items
Vesperis.give_item('warhammer')
Vesperis.inventory[0].name = 'Warhammer+1'
Vesperis.inventory[0].damage['damage_dice'] = '1d8'
Vesperis.inventory[0].two_handed_damage['damage_dice'] = '1d10'
Vesperis.inventory[0].special = '+1'

Vesperis.give_item('dagger')

Vesperis.give_item('plate-armor')

Vesperis.give_item('priests pack')

Vesperis.give_magic_item('cloak-of-protection')

# Feats
Vesperis.give_feat('telekinetic')

# Skills
Vesperis.set_skill_proficiency('insight')
Vesperis.set_skill_proficiency('medicine')
Vesperis.set_skill_bonuses()

# Saving throws
for key in Vesperis.saving_throws.keys():
     Vesperis.saving_throws[key] += 1