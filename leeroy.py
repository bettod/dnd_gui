from character import Character
# from classes import CLASSES
from SRD import SRD, SRD_classes, SRD_class_levels, SRD_rules, SRD_species
from spellcasting import SPELLS
from equipment import SRD_equipment, Item
from magicitems import SRD_magicitems, MagicItem
from feats import SRD_feats, FEATS
from metamagic import SRD_metamagic
    
Leeroy = Character(classs=SRD_classes['sorcerer'], 
                                    name='Leeroy Blackbane',
                                    gender='Male',
                                    description='Glass-blower, party-blower',
                                    level=5,
                                    alignment='CG',
                                    initiative=3,
                                    strength=11,
                                    dexterity=16,
                                    constitution=16,
                                    intelligence=16,
                                    wisdom=15,
                                    charisma=18,
                                    max_hp=43,
                                    current_hp=43,
                                    armor_class=16,
                                    speciess=SRD_species['human']
                                    )

# Spell Book
Leeroy.cantrips_known.append(SPELLS['light'])
Leeroy.cantrips_known.append(SPELLS['mage-hand'])
Leeroy.cantrips_known.append(SPELLS['friends'])
Leeroy.cantrips_known.append(SPELLS['fire-bolt'])
Leeroy.spells_known.append(SPELLS['burning-hands'])
Leeroy.spells_known.append(SPELLS['scorching-ray'])
Leeroy.spells_known.append(SPELLS['magic-missile'])
Leeroy.spells_known.append(SPELLS['witch-bolt'])
Leeroy.spells_known.append(SPELLS['crown-of-madness'])
Leeroy.spells_known.append(SPELLS['fireball'])
Leeroy.spells_known.append(SPELLS['dispel-magic'])

# Items
for iii in range(len(Leeroy.inventory)):
     _ = Leeroy.inventory.pop()   # remove all items
Leeroy.give_item('crossbow-light')
Leeroy.give_item('dagger')
Leeroy.give_item('leather-armor')

Leeroy.give_magic_item('ring-of-protection')

# Feats
# Leeroy.give_feat('telekinetic')

# Skills
Leeroy.set_skill_proficiency('arcana')
Leeroy.set_skill_proficiency('perception')
Leeroy.set_skill_bonuses()

# Class specific
Leeroy.dragon_ancestor = 'red'
Leeroy.origin = 'Draconic Bloodline'
Leeroy.metamagic_feats.append(SRD_metamagic['twinned-spell'])
Leeroy.metamagic_feats.append(SRD_metamagic['quickened-spell'])