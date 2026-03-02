from character import Character
# from classes import CLASSES
from SRD import SRD, SRD_classes, SRD_class_levels, SRD_rules, SRD_species
from spellcasting import SPELLS
from equipment import SRD_equipment, Item
from magicitems import SRD_magicitems, MagicItem
from feats import SRD_feats, FEATS

Dagl = Character(
    name="Dagl Violet",
    age="23",
    level=5,
    gender="Female",
    description="Hard-rock star with red hair and violet clothes. She has never held a sword",
    background="Sketchy past of drug abuse",
    alignment='CG',
    armor_class=14,
    strength=9,
    dexterity=14,
    constitution=14,
    intelligence=11,
    wisdom=10,
    charisma=20,
    speed=9,
    max_hp=41,
    current_hp=41,
    temp_hp=0,
    hd=8,
    classs=SRD_classes["bard"],
    speciess=SRD_species['human'],
    initiative=2,
)

# Spell Book
Dagl.cantrips_known.append(SPELLS["eldritch-blast"])
Dagl.cantrips_known.append(SPELLS["lightning-lure"])
Dagl.cantrips_known.append(SPELLS["prestidigitation"])
Dagl.cantrips_known.append(SPELLS["vicious-mockery"])
Dagl.cantrips_known.append(SPELLS["mage-hand"])
Dagl.spells_known.append(SPELLS["sleep"])
Dagl.spells_known.append(SPELLS["faerie-fire"])
Dagl.spells_known.append(SPELLS["healing-word"])
Dagl.spells_known.append(SPELLS["charm-person"])
Dagl.spells_known.append(SPELLS["cure-wounds"])
Dagl.spells_known.append(SPELLS["hex"])
Dagl.spells_known.append(SPELLS["hideous-laughter"])
Dagl.spells_known.append(SPELLS["shatter"])
Dagl.spells_known.append(SPELLS["invisibility"])
Dagl.spells_known.append(SPELLS["dissonant-whispers"])
Dagl.spells_known.append(SPELLS["hypnotic-pattern"])

# Items
for iii in range(len(Dagl.inventory)):
     _ = Dagl.inventory.pop()   # remove all items
Dagl.give_item('rapier')
Dagl.give_item('dagger')
Dagl.give_item('leather-armor')

# Skills
Dagl.set_skill_proficiency('perception')
Dagl.set_skill_proficiency('acrobatics')
Dagl.set_skill_proficiency('sleight-of-hand')
Dagl.set_skill_proficiency('stealth')
Dagl.set_skill_proficiency('arcana')
Dagl.set_skill_proficiency('investigation')
Dagl.set_skill_proficiency('deception')
Dagl.set_skill_proficiency('intimidation')
Dagl.set_skill_proficiency('performance')
Dagl.set_skill_proficiency('persuasion')
Dagl.set_skill_bonuses()
Dagl.skill_bonuses['persuasion'] += Dagl.prof_bonus
Dagl.skill_bonuses['deception'] += Dagl.prof_bonus