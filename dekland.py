from character import Character
# from classes import CLASSES
from SRD import SRD, SRD_classes, SRD_class_levels, SRD_rules, SRD_species
from invocations import SRD_invocations
from spellcasting import SPELLS
from equipment import SRD_equipment, Item
from magicitems import SRD_magicitems, MagicItem
from feats import SRD_feats, FEATS
    
Dekland = Character(classs=SRD_classes['warlock'], 
                                    name='Dekland',
                                    gender='Male',
                                    description='Rothe enjoyer',
                                    level=5,
                                    initiative=3,
                                    strength=11,
                                    dexterity=16,
                                    constitution=17,
                                    intelligence=13,
                                    wisdom=12,
                                    charisma=19,
                                    max_hp=51,
                                    current_hp=51,
                                    armor_class=16,
                                    speciess=SRD_species['half-elf']
                                    )

# Spell Book
Dekland.cantrips_known.append(SPELLS['eldritch-blast'])
Dekland.cantrips_known.append(SPELLS['poison-spray'])
Dekland.spells_known.append(SPELLS['faerie-fire'])
Dekland.spells_known.append(SPELLS['hex'])
Dekland.spells_known.append(SPELLS['witch-bolt'])
Dekland.spells_known.append(SPELLS['hideous-laughter'])
Dekland.spells_known.append(SPELLS['hellish-rebuke'])
Dekland.spells_known.append(SPELLS['find-familiar'])
Dekland.spells_known.append(SPELLS['shatter'])
Dekland.spells_known.append(SPELLS['dispel-magic'])

# Items
for iii in range(len(Dekland.inventory)):
     _ = Dekland.inventory.pop()   # remove all items
Dekland.give_item('crossbow-light')
Dekland.give_item('dagger')
Dekland.give_item('leather-armor')

Dekland.give_magic_item('ring-of-protection')

# Feats
# Dekland.give_feat('telekinetic')

# Skills
Dekland.set_skill_proficiency('deception')
Dekland.set_skill_proficiency('arcana')
Dekland.set_skill_proficiency('perception')
Dekland.set_skill_bonuses()

# Saving throws
for key in Dekland.saving_throws.keys():
     Dekland.saving_throws[key] += 1

# Class specific
Dekland.patron = 'The Great Old One'
Dekland.invocations.append(SRD_invocations['eldritch-invocation-eldritch-sight'])
Dekland.invocations.append(SRD_invocations['eldritch-invocation-agonizing-blast'])
Dekland.invocations.append(SRD_invocations['eldritch-invocation-eldritch-spear'])
