from typing import Optional, Union, Iterator, TYPE_CHECKING
from uuid import uuid4, UUID
import logging
import json
from termcolor import colored

if TYPE_CHECKING:
    from classes import _CLASS
    from spellcasting import _SPELL
    from species import _SPECIES
    from invocations import _INVOCATION

from SRD import SRD, SRD_class_levels, SRD_classes, SRD_species
from equipment import _Item, Item
from magicitems import _MagicItem, MagicItem
from experience import Experience, experience_at_level, level_at_experience
from spellcasting import SpellList, SPELLS
from invocations import InvocationList, INVOCATIONS
from metamagic import MetamagicList, METAMAGIC
from dice import sum_rolls
from features import get_class_features_data
from feats import SRD_feats

# Custom classes
with open('./json_cache/api_classes_twilight-cleric.json') as json_file:
    data = json.load(json_file)
SRD_classes.update({data['index']:data})
with open('./json_cache/api_classes_twilight_cleric_levels.json') as json_file:
    data = json.load(json_file)
SRD_class_levels.update({'twilight-cleric':data})

with open('./json_cache/api_2014_races_protector-aasimar.json') as json_file:
    data = json.load(json_file)
SRD_species.update({data['index']:data})
with open('./json_cache/api_2014_races_aasimar.json') as json_file:
    data = json.load(json_file)
SRD_species.update({data['index']:data})

LOG = logging.getLogger(__package__)

coin_value = {"pp": 10, "gp": 1, "ep": 0.5, "sp": 0.1, "cp": 0.01}


class InvalidParameterError(Exception):
    pass


class Character:
    """
    Character object deals with all aspects of a player character including
    name, class features, level/experience, wealth, and all ability scores.
    All can be omitted to create a blank, level 1 character.
    """

    def __init__(
        self,
        *,  # This * forces the caller to use keyword arguments
        uid: Optional[Union[UUID, str]] = None,
        classs: Optional["_CLASS"] = None,
        class_name: Optional[str] = None,
        class_index: Optional[str] = None,
        name: Optional[str] = None,
        age: Optional[str] = None,
        gender: Optional[str] = None,
        speciess: Optional["_SPECIES"] = None,
        speed: Optional[int] = None,
        initiative: Optional[int] = 0,
        size: Optional[str] = None,
        size_description: Optional[str] = None,
        alignment: Optional[str] = None,
        description: Optional[str] = None,
        background: Optional[str] = None,
        personality: Optional[str] = None,
        ideals: Optional[str] = None,
        bonds: Optional[str] = None,
        flaws: Optional[str] = None,
        level: Optional[int] = None,
        experience: Union[int, None, Experience] = None,
        wealth: Optional[Union[int, float]] = None,
        wealth_detailed: Optional[dict] = None,
        strength: Optional[int] = None,
        dexterity: Optional[int] = None,
        constitution: Optional[int] = None,
        wisdom: Optional[int] = None,
        intelligence: Optional[int] = None,
        charisma: Optional[int] = None,
        max_hp: Optional[int] = None,
        current_hp: Optional[int] = None,
        temp_hp: Optional[int] = None,
        hd: int = 8,
        max_hd: Optional[int] = None,
        current_hd: Optional[int] = None,
        traits: Optional[dict] = None,
        proficiencies: Optional[dict] = None,
        saving_throws_proficiency: Optional[list] = None,
        cantrips_known: Optional[list["_SPELL"]] = None,
        spells_known: Optional[list["_SPELL"]] = None,
        spells_prepared: Optional[list["_SPELL"]] = None,
        spell_slots: Optional[dict[str, int]] = None,
        skills_strength: Optional[dict] = None,
        skills_dexterity: Optional[dict] = None,
        skills_wisdom: Optional[dict] = None,
        skills_intelligence: Optional[dict] = None,
        skills_charisma: Optional[dict] = None,
        skills_proficiency: Optional[dict] = None,
        inventory: Optional[list[dict]] = None,
        magicinventory: Optional[list[dict]] = None,
        prof_bonus: int = 0,
        ability_score_bonus: int = 0,
        class_features: Optional[dict] = None,
        class_features_enabled: Optional[list] = None,
        spellcasting_stat: Optional[str] = None,
        feats: Optional[dict] = None,
        player_options: Optional[dict] = None,
        armor_class: Optional[int] = None,
        death_saves: int = 0,
        death_fails: int = 0,
        exhaustion: int = 0,
        dead: bool = False,
        conditions: Optional[dict] = None,
    ):
        """
        Typical Arguments:
                name         (str)
                age          (str)
                gender       (str)
                alignment    (str): two letter alignment (LE, TN, CN, LG, etc.)
                description  (str): physical description of character
                background   (str): one-word backstory of character (e.g. knight, chef)
                level        (int): character's starting level
                wealth       (int): character's starting wealth
                strength     (int): character's starting strength
                dexterity    (int):  character's starting dexterity
                constitution (int):  character's starting constitution
                wisdom       (int):  character's starting wisdom
                intelligence (int):  character's starting intelligence
                charisma     (int):  character's starting charisma
        """
        # Decorative attrs that don't affect program logic
        self.uid: UUID = (
            uuid4() if uid is None else uid if isinstance(uid, UUID) else UUID(uid)
        )
        self.name = name
        self.age = age
        self.gender = gender
        self.description = description
        self.background = background
        self.personality = personality
        self.ideals = ideals
        self.bonds = bonds
        self.flaws = flaws
        # self.species = species
        self.speed = 30 if speed is None else int(speed)
        self.initiative = initiative
        self.player_options = (
            player_options if player_options is not None else {"starting_equipment": []}
        )
        self.alignment = alignment
        if self.alignment is not None:
            assert (
                len(self.alignment) == 2
            ), "Alignments must be 2 letters (i.e LE, LG, TN, NG, CN)"
            self.alignment = self.alignment.upper()

        # Ability Scores
        self.strength = self.set_initial_ability_score(strength)
        self._dexterity = self.set_initial_ability_score(dexterity)
        self.constitution = self.set_initial_ability_score(constitution)
        self.wisdom = self.set_initial_ability_score(wisdom)
        self.intelligence = self.set_initial_ability_score(intelligence)
        self.charisma = self.set_initial_ability_score(charisma)

        # DND Class
        self.class_name = class_name
        self.class_index = class_index
        self._class_levels = (
            [] if class_index not in SRD_class_levels else SRD_class_levels[class_index]
        )
        self._level = 1  # may be increased later in this method
        self.prof_bonus = prof_bonus
        self.ability_score_bonus = ability_score_bonus
        self.class_features = class_features if class_features is not None else {}
        self.class_features_enabled = (
            class_features_enabled if class_features_enabled is not None else []
        )
        self._class_features_data = get_class_features_data(character=self)

        self.feats = feats if feats is not None else {}

        # Hit Dice and Hit Points: self.hd == 8 is a d8, 10 is a d10, etc
        self.hd = 8 if hd is None else hd
        self.max_hd = 1 if max_hd is None else max_hd
        self.current_hd = 1 if current_hd is None else current_hd
        self.max_hp = (
            Character.get_maximum_hp(
                self.hd, 1 if level is None else int(level), self.constitution
            )
            if max_hp is None
            else max_hp
        )
        self._current_hp = current_hp if current_hp is not None else int(self.max_hp)
        self.temp_hp = 0 if temp_hp is None else int(temp_hp)

        # Spells, Skills, Proficiencies, Traits
        self.traits = traits if traits is not None else {}
        self.proficiencies = proficiencies if proficiencies is not None else {}
        self.saving_throws_proficiency = saving_throws_proficiency if saving_throws_proficiency is not None else []
        self.spellcasting_stat = spellcasting_stat
        self._cantrips_known: SpellList["_SPELL"] = SpellList(cantrips_known)
        self._spells_known: SpellList["_SPELL"] = SpellList(spells_known)
        self._spells_prepared: SpellList["_SPELL"] = SpellList(spells_prepared)
        self.set_spell_slots(spell_slots)

        # Experience points
        # self.level could be altered by Experience object below
        if experience is None:
            experience = 0
        self._experience = Experience(character=self, experience=int(experience))

        # Levels
        # self.level could be altered by Experience object above
        if level is not None:
            if self._experience.experience == 0:
                # if only level is specified, set the experience to the amount for that level
                self._experience._experience = experience_at_level(level)
                self._experience.update_level()
                # Experience alters self.level so it is now the correct value
            else:
                # if level is specified AND experience is not zero:
                # the Experience object normally handles the self.level attr
                # but if a user changes their level manually, it should override this anyway
                LOG.info(
                    f"Custom level for {str(self.name)}: {str(level)} instead of {str(self.level)}"
                )
                self._level = level

        if skills_charisma is None:
            self.skills_charisma = {
                "deception": False,
                "intimidation": False,
                "performance": False,
                "persuasion": False,
            }
        else:
            self.skills_charisma = skills_charisma
        if skills_wisdom is None:
            self.skills_wisdom = {
                "animal-handling": False,
                "insight": False,
                "medicine": False,
                "perception": False,
                "survival": False,
            }
        else:
            self.skills_wisdom = skills_wisdom
        if skills_dexterity is None:
            self.skills_dexterity = {
                "acrobatics": False,
                "sleight-of-hand": False,
                "stealth": False,
            }
        else:
            self.skills_dexterity = skills_dexterity
        if skills_intelligence is None:
            self.skills_intelligence = {
                "arcana": False,
                "history": False,
                "investigation": False,
                "nature": False,
                "religion": False,
            }
        else:
            self.skills_intelligence = skills_intelligence
        if skills_strength is None:
            self.skills_strength = {
                "athletics": False,
            }
        else:
            self.skills_strength = skills_strength
        
        if skills_proficiency is None:
            self.skills_proficiency = {
                "acrobatics": False,
                "sleight-of-hand": False,
                "stealth": False,
                "athletics": False,
                "arcana": False,
                "history": False,
                "investigation": False,
                "nature": False,
                "religion": False,
                "animal-handling": False,
                "insight": False,
                "medicine": False,
                "perception": False,
                "survival": False,
                "deception": False,
                "intimidation": False,
                "performance": False,
                "persuasion": False,
            }
        else:
            self.skills_proficiency = skills_proficiency

        self.skill_bonuses = {
            "acrobatics": 0,
            "sleight-of-hand": 0,
            "stealth": 0,
            "athletics": 0,
            "arcana": 0,
            "history": 0,
            "investigation": 0,
            "nature": 0,
            "religion": 0,
            "animal-handling": 0,
            "insight": 0,
            "medicine": 0,
            "perception": 0,
            "survival": 0,
            "deception": 0,
            "intimidation": 0,
            "performance": 0,
            "persuasion": 0,
        }

        self.saving_throws = {
            "STR": 0,
            "DEX": 0,
            "CON": 0,
            "INT": 0,
            "WIS": 0,
            "CHA": 0,
        }

        # Inventory & Wealth
        final_wealth = None
        if wealth_detailed is None:
            final_wealth = float(sum_rolls(d10=4)) if wealth is None else wealth
            self.wealth_detailed = self.infer_wealth(final_wealth)
        else:
            self.wealth_detailed = wealth_detailed
            final_wealth = sum(
                [coin_value[u] * v for u, v in self.wealth_detailed.items()]
            )

        # if both wealth parameters provided
        if wealth is not None and float(wealth) != final_wealth:
            raise InvalidParameterError(
                "Both 'wealth' and 'wealth_detailed' parameters are provided, but 'wealth' seems incorrect."
            )
        self.wealth = final_wealth

        # Inventory. Deserialize items and give them one by one
        self._inventory: list[_Item] = []
        if inventory is not None:
            for item in inventory:
                self.give_item(_Item(**item))

        # Magic Inventory. Deserialize items and give them one by one
        self._magicinventory: list[_MagicItem] = []
        if magicinventory is not None:
            for item in magicinventory:
                self.give_magicitem(_MagicItem(**item))

        # Final steps of initialization -- the speciess.setter does lots of work here
        # setting the self.speciess attr applies "species traits" appropriate to the character
        self.speciess = speciess

        # Final steps of initialization -- the classs.setter does lots of work here
        # setting the self.classs attr applies "class features" appropriate to character's level
        self.classs = classs

        #Class specific features, e.g. for warlocks, the patron and invocations
        if self.class_name == 'Warlock':
            self._patron = None
            self.patron_features = []
            self.invocations: InvocationList["_INVOCATION"] = InvocationList(initial=[])
            self.arcanum_spells: SpellList["_SPELL"] = []
        # the patron.setter does lots of work here
        # setting the self.patron attr applies "patron features" appropriate to character's level

        if self.class_name == 'Sorcerer':
            self._origin = None
            self.dragon_ancestor = None
            self.origin_features = []
            self.metamagic_feats: MetamagicList["_METAMAGIC"] = MetamagicList(initial=[])

        self.set_saving_throw_bonuses()

        # base armor class is 10 + DEX; will be affected by inventory
        if armor_class is not None:
            self.armor_class = armor_class
        elif not hasattr(self, "armor_class"):
            self.armor_class = self.base_armor_class
        self._dead = dead
        self._death_saves = death_saves
        self._death_fails = death_fails
        self.exhaustion = exhaustion

        if self.level == level_at_experience(self._experience._experience):
            self.level = self._level
            if current_hp is None:
                # Set character's HP to the maximum for their level,
                # only if the level isn't custom! (if it matches experience points according to SRD)
                self.current_hp = Character.get_maximum_hp(
                    self.hd, self.level, self.constitution
                )

        # Conditions
        all_conditions = [
            "blinded",
            "charmed",
            "deafened",
            "frightened",
            "grappled",
            "incapacitated",
            "invisible",
            "paralyzed",
            "petrified",
            "poisoned",
            "prone",
            "restrained",
            "stunned",
            "unconscious",
        ]
        if conditions is None:
            self.conditions = {k: False for k in all_conditions}
        else:
            self.conditions = {
                k: conditions[k] if k in conditions.keys() else False
                for k in all_conditions
            }


    def __str__(self) -> str:
        output = ""
        output += f"<span style='color:green;'>Gender:: </span>" + f"{self.gender}\n"
        output += f"<span style='color:green;'>Species:: </span>" + f"{self.species_name}\n"
        output += f"<span style='color:green;'>Class:: </span>" + f"{self.class_name}\n"
        output += f"<span style='color:green;'>Level:: </span>" + f"{self.level}\n"
        output += f"<span style='color:green;'>Description:: </span>" + f"{self.description}\n"
        output += f"<span style='color:green;'>Size:: </span>" + f"{self.size}\n"
        output += f"<span style='color:green;'>Speed:: </span>" + f"{str(self.speed)}\n"
        output += f"<span style='color:green;'>Aligment: </span>" + f"{self.alignment}\n"
        output += f"<span style='color:red;'>Max Hit Points:: </span>" + f"<span style='color:red;'>{str(self.max_hp)}\n</span>"
        output += f"<span style='color:red;'>Current Hit Points:: </span>" + f"<span style='color:red;'>{str(self.current_hp)}\n</span>"
        output += f"<span style='color:green;'>Armor Class:: </span>" + f"{str(self.armor_class)}\n"
        output += f"<span style='color:green;'>Proficiencies:\t</span>" + f"{', '.join([value['name'] for value in self.proficiencies.values()])}\n"
        output += f"<span style='color:green;'>Traits:\n</span>"
        for value in self.traits.values():
            output += f"<span style='color:cyan;'>\t{value['name']}: </span>" + f"{value['desc']}\n"
        output += f"<span style='color:green;'>Class Features:\n</span>"
        for value in self.class_features.values():
            if 'desc' in value.keys():
                output += f"<span style='color:cyan;'>\t{value['name']}:</span> " + f"{value['desc']}\n"
            else:
                output += f"<span style='color:cyan;'>\t{value['name']}\n</span>"
        output += f"<span style='color:green;'>Class Features Data:\n</span>"
        for key in self.class_features_data.keys():
            output += f"<span style='color:cyan;'>\t{key}: </span>" + f"{self.class_features_data[key]}\n"
        output += f"<span style='color:green;'>Cantrips Known:\n</span>"
        output += f"\t{', '.join([item.name for item in self.cantrips_known])}\n\n"
        output += f"<span style='color:green;'>Spells Known:\n</span>"
        output += f"\t{', '.join([item.name for item in self.spells_known])}\n\n"
        if self.class_name == 'Warlock':
            output += f"<span style='color:green;'>Patron:: </span>" + f"{self.patron}\n"
            output += f"<span style='color:green;'>Patron Features:\n</span>"
            for feature in self.patron_features:
                output += f"<span style='color:green;'>\t{feature['name']}:: </span>" + f"{feature['desc']}\n\n"
            output += colored(f"Invocations:\n", 'green')
            output += f"\t{', '.join([item['name'].replace('Eldritch Invocation: ', '') for item in self.invocations])}\n\n"
            output += f"<span style='color:green;'>Arcanum Spells:\n</span>"
            output += f"\t{', '.join([item.name for item in self.arcanum_spells])}\n\n"
        if self.class_name == 'Sorcerer':
            output += f"<span style='color:green;'>Origin:: </span>" + f"{self.origin}\n"
            output += f"<span style='color:green;'>Origin Features:\n</span>"
            for feature in self.origin_features:
                output += f"<span style='color:green;'>\t{feature['name']}:: </span>" + f"{feature['desc']}\n\n"
            output += f"<span style='color:green;'>Metamagic:\n</span>"
            output += f"\t{', '.join([item['name'].replace('Metamagic: ', '') for item in self.metamagic_feats])}\n\n"
        output += f"<span style='color:green;'>Feats:\n</span>"
        for key in self.feats.keys():
            output += f"<span style='color:cyan;'>\t{key}: </span>" + f"{self.feats[key]['desc']}\n"
        output += f"<span style='color:green;'>Inventory:\n</span>"
        output += f"\t{', '.join([item.name for item in self.inventory])}\n"
        output += f"\t{', '.join([item.name for item in self.magicinventory])}\n"
        output += f"<span style='color:green;'>Saving Throws:\n</span>"
        for save in self.saving_throws.keys():
            if save in self.saving_throws_proficiency:
                output += "<span style='color:yellow;'>\t" + save  + f'</span>: {self.saving_throws[save]} + {self.prof_bonus}'
            else:
                output += "\t<span style='color:yellow;'>" + save + f'</span>: {self.saving_throws[save]}'
        output += f"\n"
        output += f"<span style='color:green;'>Skills:\n</span>"
        for skill in self.skill_bonuses.keys():
            mod = self.skill_bonuses[skill]
            if self.skills_proficiency[skill]:
                output += "\t<span style='color:yellow;'>" + skill + f'</span>: {mod} + {self.prof_bonus}'
            else:
                output += "\t<span style='color:yellow;'>" + skill + f'</span>: {mod}'
        output += f"\n"
        return output

    def help(self) -> None:
        print('type .show() to print a summary')
        print('type .show_spells_known()')
        print('type .show_spells_prepared()')
        print('type .show_saving_throws()')
        print('type .show_skill_bonuses()')
        print('type .prepare_spell(<spell>)')
        print('type .remove_spell(<spell>)')
        print('type .show_inventory()')
        print('type .give_item(<item>)')
        print('type .give_magicitem(<item>)')
        print('type .give_randomitem(<item>)')
        print('type .remove_item(<item>)')
        print('type .remove_magicitem(<item>)')
        print('set values with <name>.<property> = <value>')
        print('type .show_invocations_known() if you are a warlock')
        print('type .show_metamagic_feats() if you are a sorcerer')


    def show(self) -> None:
        return(str(self))

    def show_features(self) -> str:
        output = ""
        output += f"<span style='color:green;'>Size:: </span>" + f"{self.size}\n"
        output += f"<span style='color:green;'>Aligment: </span>" + f"{self.alignment}\n"
        output += f"<span style='color:green;'>Proficiencies:\t</span>" + f"{', '.join([value['name'] for value in self.proficiencies.values()])}\n"
        output += f"<span style='color:green;'>Traits:\n</span>"
        for value in self.traits.values():
            output += f"<span style='color:cyan;'>\t{value['name']}: </span>" + f"{value['desc']}\n"
        output += f"<span style='color:green;'>Class Features:\n</span>"
        for value in self.class_features.values():
            if 'desc' in value.keys():
                output += f"<span style='color:cyan;'>\t{value['name']}:</span> " + f"{value['desc']}\n"
            else:
                output += f"<span style='color:cyan;'>\t{value['name']}\n</span>"
        output += f"<span style='color:green;'>Class Features Data:\n</span>"
        for key in self.class_features_data.keys():
            if self.class_features_data[key] is not 0:
                output += f"<span style='color:cyan;'>\t{key}: </span>" + f"{self.class_features_data[key]}\n"
        output += f"<span style='color:green;'>Cantrips Known:\n</span>"
        output += f"\t{', '.join([item.name for item in self.cantrips_known])}\n\n"
        output += f"<span style='color:green;'>Spells Known:\n</span>"
        output += f"\t{', '.join([item.name for item in self.spells_known])}\n\n"
        if self.class_name == 'Warlock':
            output += f"<span style='color:green;'>Patron:: </span>" + f"{self.patron}\n"
            output += f"<span style='color:green;'>Patron Features:\n</span>"
            for feature in self.patron_features:
                output += f"<span style='color:green;'>\t{feature['name']}:: </span>" + f"{feature['desc']}\n\n"
            output += colored(f"Invocations:\n", 'green')
            output += f"\t{', '.join([item['name'].replace('Eldritch Invocation: ', '') for item in self.invocations])}\n\n"
            output += f"<span style='color:green;'>Arcanum Spells:\n</span>"
            output += f"\t{', '.join([item.name for item in self.arcanum_spells])}\n\n"
        if self.class_name == 'Sorcerer':
            output += f"<span style='color:green;'>Origin:: </span>" + f"{self.origin}\n"
            output += f"<span style='color:green;'>Origin Features:\n</span>"
            for feature in self.origin_features:
                output += f"<span style='color:green;'>\t{feature['name']}:: </span>" + f"{feature['desc']}\n\n"
            output += f"<span style='color:green;'>Metamagic:\n</span>"
            output += f"\t{', '.join([item['name'].replace('Metamagic: ', '') for item in self.metamagic_feats])}\n\n"
        output += f"<span style='color:green;'>Feats:\n</span>"
        for key in self.feats.keys():
            output += f"<span style='color:cyan;'>\t{key}: </span>" + f"{self.feats[key]['desc']}\n"
        output += f"<span style='color:green;'>Inventory:\n</span>"
        output += f"\t{', '.join([item.name for item in self.inventory])}\n"
        output += f"\t{', '.join([item.name for item in self.magicinventory])}\n"
        return output
        
    def show_saving_throws(self) -> str:
        output = ""
        output += f"<span style='color:green;'>Saving Throws:\n</span>"
        for save in self.saving_throws.keys():
            if save in self.saving_throws_proficiency:
                output += "<span style='color:yellow;'>\t" + save  + f'</span>: {self.saving_throws[save]} + {self.prof_bonus}'
            else:
                output += "\t<span style='color:yellow;'>" + save + f'</span>: {self.saving_throws[save]}'
        return output

    def show_skill_bonuses(self) -> str:
        output = ""
        output += f"<span style='color:green;'>Skills:\n</span>"
        for skill in self.skill_bonuses.keys():
            mod = self.skill_bonuses[skill]
            if self.skills_proficiency[skill]:
                output += "\t<span style='color:yellow;'>" + skill + f'</span>: {mod} + {self.prof_bonus}\n'
            else:
                output += "\t<span style='color:yellow;'>" + skill + f'</span>: {mod}\n'
        output += f"\n"
        return output

    def show_inventory(self) -> None:
        output = ''
        output += colored(f"Inventory:\n", 'green')
        for item in self.inventory:
            output += colored(f"\t{item.name}\n", 'green')
            if item.desc:
                output += colored(f"\t\t{item.desc}\n", 'white')
            if item.special:
                output += colored(f"\t\t{item.special}\n", 'white')
            if item.damage:
                output += colored(f"\t\t{item.damage['damage_dice']}, {item.damage['damage_type']['name']}\n", 'white')
            if item.properties:
                for prop in item.properties:
                    output += colored(f"\t\t{prop['name']}\n", 'white')
            if item.armor_class:
                output += colored(f"\t\tAC: {str(item.armor_class['base'])}, Dex bonus: {item.armor_class['dex_bonus']}\n", 'white')
            if item.armor_category:
                output += colored(f"\t\t{item.armor_category}\n", 'white')
        for item in self.magicinventory:
            output += colored(f"\t{item.name}\n", 'green')
            output += colored(f"\t\t{item.desc}\n", 'white')
        print(output)

    def format_single_item(self, item) -> str:
        """
        Return a formatted string for a single ITEMS object, in the same
        style as show_inventory() uses for each item.
        """
        output = ''
        if item in self.inventory:
            # output += f"\t{item.name}\n", 'green')
            if item.desc:
                output += f"<span style='color:green;'>Description: </span>\t\t{item.desc}\n"
            if item.special:
                output += f"<span style='color:green;'>Specials: </span>\t\t{item.special}\n"
            if item.damage:
                output += f"<span style='color:red;'>Damage: </span>\t\t{item.damage['damage_dice']}, {item.damage['damage_type']['name']}\n"
            if item.properties:
                output += f"<span style='color:green;'>Properties: </span>"
                for prop in item.properties:
                    output += f"\t\t{prop['name']}, "
            if item.armor_class:
                output += f"\n<span style='color:green;'>Armor Class: </span>\t\t{str(item.armor_class['base'])}, <span style='color:green;'>Dex Bonus:</span> {item.armor_class['dex_bonus']}\n"
            if item.armor_category:
                output += f"<span style='color:green;'>Category: </span>\t\t{item.armor_category}\n"
        elif item in self.magicinventory:
            # output += f"<span style='color:green;'>\t{item.name}\n"
            output += f"<span style='color:green;'>Description: </span>\t\t{item.desc}\n"
        return output

    def show_invocations_known(self) -> None:
        if self.class_name != 'Warlock':
            print("Only warlocks have invocations.")
            return
        output = ""
        for invocation in self.invocations:
            output += colored(f"\t{invocation['name'].replace('Eldritch Invocation: ', '')}\n", 'green')
            output += colored(f"\t\tPrerequisites: {invocation['prerequisites']}\n", 'white')
            output += colored(f"\t\tDescription: {invocation['desc']}\n", 'white')
        print(output)

    def show_metamagic_feats(self) -> None:
        if self.class_name != 'Sorcerer':
            print("Only sorcerers have metamagic feats.")
            return
        output = ""
        for feat in self.metamagic_feats:
            output += colored(f"\t{feat['name'].replace('Metamagic: ', '')}\n", 'green')
            output += colored(f"\t\tPrerequisites: {feat['prerequisites']}\n", 'white')
            output += colored(f"\t\tDescription: {feat['desc']}\n", 'white')
        print(output)

    def show_spells_known(self) -> None:
        output = ""
        for spells_level in range(10):
            output += colored(f"Level {str(spells_level)}:\n", 'light_magenta')
            if 0 == spells_level:
                for spell in self.cantrips_known:
                    output += colored(f"\t{spell.name}\n", 'green')
                    output += colored(f"\t\tSchool: {spell.school['name']}\n", 'white')
                    output += colored(f"\t\tRitual: {spell.ritual}\n", 'white')
                    output += colored(f"\t\tComponents: {spell.components}, {spell.material}\n", 'white')
                    output += colored(f"\t\tConcentration: {spell.concentration}\n", 'white')
                    output += colored(f"\t\tCasting time: {spell.casting_time}\n", 'white')
                    output += colored(f"\t\tDuration: {spell.duration}\n", 'white')
                    if spell.name == 'Eldritch Blast' and self.class_name == 'Warlock':
                        for invocation in self.invocations:
                            if invocation['name'] == 'Eldritch Invocation: Eldritch Spear':
                                output += colored(f"\t\tRange: 300 feet, because of Eldritch Spear\n", 'white')
                    else:
                        output += colored(f"\t\tRange: {spell.range}\n", 'white')
                    if spell.name == 'Eldritch Blast' and self.class_name == 'Warlock':
                        for invocation in self.invocations:
                            if invocation['name'] == 'Eldritch Invocation: Agonizing Blast':
                                output += colored(f"\t\tDamage: {spell.damage['damage_type']['name']}, Damage at char level: {spell.damage['damage_at_character_level']},  Damage bonus for Agonizing Blast: +{str(self.get_ability_modifier(self.charisma))}\n", 'white') 
                    elif spell.damage is not None:
                        if 'damage_at_character_level' in spell.damage.keys():
                            output += colored(f"\t\tDamage: {spell.damage['damage_type']['name']}, Damage at char level: {spell.damage['damage_at_character_level']}  \n", 'white')
                        else:
                            output += colored(f"\t\tDamage: {spell.damage['damage_type']['name']}\n", 'white')
                    if spell.dc is not None:
                        output += colored(f"\t\tDC: {spell.dc['dc_type']['name']}, DC success: {spell.dc['dc_success']}\n", 'white')
                    output += colored(f"\t\tDescription: {spell.desc}\n", 'white')
                    if spell.name == 'Eldritch Blast' and self.class_name == 'Warlock':
                        for invocation in self.invocations:
                            if invocation['name'] == 'Eldritch Invocation: Repelling Blast':
                                output += colored(f"\t\tEldritch Blast also pushes target up to 10 feet away from you, because of Repelling Blast\n", 'white')
                    output += colored(f"\t\tHigher Level: {spell.higher_level}\n", 'white')
            else:
                for spell in self.spells_known:
                    if spell.level == spells_level:
                        output += colored(f"\t{spell.name}\n", 'green')
                        output += colored(f"\t\tSchool: {spell.school['name']}\n", 'white')
                        output += colored(f"\t\tRitual: {spell.ritual}\n", 'white')
                        output += colored(f"\t\tComponents: {spell.components}, {spell.material}\n", 'white')
                        output += colored(f"\t\tConcentration: {spell.concentration}\n", 'white')
                        output += colored(f"\t\tCasting time: {spell.casting_time}\n", 'white')
                        output += colored(f"\t\tDuration: {spell.duration}\n", 'white')
                        output += colored(f"\t\tRange: {spell.range}\n", 'white')
                        if spell.damage is not None:
                            if 'damage_at_slot_level' in spell.damage.keys():
                                output += colored(f"\t\tDamage: {spell.damage['damage_type']['name']}, Damage at slot level: {spell.damage['damage_at_slot_level']}  \n", 'white')
                            else:
                                output += colored(f"\t\tDamage: {spell.damage['damage_type']['name']}\n", 'white')
                        if spell.dc is not None:
                            output += colored(f"\t\tDC: {spell.dc['dc_type']['name']}, DC success: {spell.dc['dc_success']}\n", 'white')
                        output += colored(f"\t\tDescription: {spell.desc}\n", 'white')
                        output += colored(f"\t\tHigher Level: {spell.higher_level}\n", 'white')
        print(output)

    def format_single_spell(self, spell) -> str:
        """
        Return a formatted string for a single SPELLS object, in the same
        style as show_spells_known() uses for each spell.
        """
        output = ""
        if 0 == spell.level:
            # output += f"<span style='color:{green};'>\t{spell.name}\n</span>"
            output += f"<span style='color:#FF55FF;'>Level {str(spell.level)}:\n</span>"
            output += f"<span style='color:green;'>\t\tSchool: </span>{spell.school['name']}\n"
            output += f"<span style='color:green;'>\t\tRitual: </span>{spell.ritual}\n"
            output += f"<span style='color:green;'>\t\tComponents: </span>{spell.components}, {spell.material}\n"
            output += f"<span style='color:green;'>\t\tConcentration: </span>{spell.concentration}\n"
            output += f"<span style='color:green;'>\t\tCasting time: </span>{spell.casting_time}\n"
            output += f"<span style='color:green;'>\t\tDuration: </span>{spell.duration}\n"
            if spell.name == 'Eldritch Blast' and self.class_name == 'Warlock':
                for invocation in self.invocations:
                    if invocation['name'] == 'Eldritch Invocation: Eldritch Spear':
                        output += f"\t\t<span style='color:green;'>Range:</span> 300 feet, because of Eldritch Spear\n"
            else:
                output += f"<span style='color:green;'>\t\tRange:</span> {spell.range}\n"
            if spell.name == 'Eldritch Blast' and self.class_name == 'Warlock':
                for invocation in self.invocations:
                    if invocation['name'] == 'Eldritch Invocation: Agonizing Blast':
                        output += f"<span style='color:red;'>\t\tDamage:</span> {spell.damage['damage_type']['name']}, <span style='color:red;'>Damage at char level:</span> {spell.damage['damage_at_character_level']},  <span style='color:red;'>Damage bonus for Agonizing Blast:</span> +{str(self.get_ability_modifier(self.charisma))}\n"
            elif spell.damage is not None:
                if 'damage_at_character_level' in spell.damage.keys():
                    output += f"<span style='color:red;'>\t\tDamage: </span>{spell.damage['damage_type']['name']}, <span style='color:red;'>Damage at char level:</span> {spell.damage['damage_at_character_level']}  \n"
                else:
                    output += f"<span style='color:red;'>\t\tDamage:</span> {spell.damage['damage_type']['name']}\n"
            if spell.dc is not None:
                output += f"<span style='color:red;'>\t\tDC:</span> {spell.dc['dc_type']['name']}, <span style='color:red;'>DC success:</span> {spell.dc['dc_success']}\n"
            output += f"<span style='color:green;'>\t\tDescription:</span> {spell.desc}\n"
            if spell.name == 'Eldritch Blast' and self.class_name == 'Warlock':
                for invocation in self.invocations:
                    if invocation['name'] == 'Eldritch Invocation: Repelling Blast':
                        output += f"\t\tEldritch Blast also pushes target up to 10 feet away from you, because of Repelling Blast\n"
            output += f"<span style='color:green;'>\t\tHigher Level:</span> {spell.higher_level}\n"
        else:
            # output += f"<span style='color:green;'>\t{spell.name}\n</span>"
            output += f"<span style='color:#FF55FF;'>Level {str(spell.level)}:\n</span>"
            output += f"<span style='color:green;'>\t\tSchool:</span> {spell.school['name']}\n"
            output += f"<span style='color:green;'>\t\tRitual:</span> {spell.ritual}\n"
            output += f"<span style='color:green;'>\t\tComponents:</span> {spell.components}, {spell.material}\n"
            output += f"<span style='color:green;'>\t\tConcentration:</span> {spell.concentration}\n"
            output += f"<span style='color:green;'>\t\tCasting time:</span> {spell.casting_time}\n"
            output += f"<span style='color:green;'>\t\tDuration:</span> {spell.duration}\n"
            output += f"<span style='color:green;'>\t\tRange: </span>{spell.range}\n"
            if spell.damage is not None:
                if 'damage_at_slot_level' in spell.damage.keys():
                    output += f"<span style='color:red;'>\t\tDamage:</span> {spell.damage['damage_type']['name']},<span style='color:red;'> Damage at slot level:</span> {spell.damage['damage_at_slot_level']}  \n"
                else:
                    output += f"<span style='color:red;'>\t\tDamage:</span> {spell.damage['damage_type']['name']}\n"
            if spell.dc is not None:
                output += f"<span style='color:red;'>\t\tDC:</span> {spell.dc['dc_type']['name']}, <span style='color:red;'>DC success:</span> {spell.dc['dc_success']}\n"
            output += f"<span style='color:green;'>\t\tDescription: </span>{spell.desc}\n"
            output += f"<span style='color:green;'>\t\tHigher Level:</span> {spell.higher_level}\n"
        return output        


    def show_spells_prepared(self) -> None:
        output = ""
        for spells_level in range(10):
            output += colored(f"Level {str(spells_level)}:\n", 'light_magenta')
            if 0 == spells_level:
                for spell in self.cantrips_known:
                    output += colored(f"\t{spell.name}\n", 'green')
                    output += colored(f"\t\tSchool: {spell.school['name']}\n", 'white')
                    output += colored(f"\t\tRitual: {spell.ritual}\n", 'white')
                    output += colored(f"\t\tComponents: {spell.components}, {spell.material}\n", 'white')
                    output += colored(f"\t\tConcentration: {spell.concentration}\n", 'white')
                    output += colored(f"\t\tCasting time: {spell.casting_time}\n", 'white')
                    output += colored(f"\t\tDuration: {spell.duration}\n", 'white')
                    if spell.name == 'Eldritch Blast' and self.class_name == 'Warlock':
                        for invocation in self.invocations:
                            if invocation['name'] == 'Eldritch Invocation: Eldritch Spear':
                                output += colored(f"\t\tRange: 300 feet, because of Eldritch Spear\n", 'white')
                    else:
                        output += colored(f"\t\tRange: {spell.range}\n", 'white')
                    if spell.name == 'Eldritch Blast' and self.class_name == 'Warlock':
                        for invocation in self.invocations:
                            if invocation['name'] == 'Eldritch Invocation: Agonizing Blast':
                                output += colored(f"\t\tDamage: {spell.damage['damage_type']['name']}, Damage at char level: {spell.damage['damage_at_character_level']},  Damage bonus for Agonizing Blast: +{str(self.get_ability_modifier(self.charisma))}\n", 'white') 
                    elif spell.damage is not None:
                        if 'damage_at_character_level' in spell.damage.keys():
                            output += colored(f"\t\tDamage: {spell.damage['damage_type']['name']}, Damage at char level: {spell.damage['damage_at_character_level']}  \n", 'white')
                        else:
                            output += colored(f"\t\tDamage: {spell.damage['damage_type']['name']}\n", 'white')
                    if spell.dc is not None:
                        output += colored(f"\t\tDC: {spell.dc['dc_type']['name']}, DC success: {spell.dc['dc_success']}\n", 'white')
                    output += colored(f"\t\tDescription: {spell.desc}\n", 'white')
                    if spell.name == 'Eldritch Blast' and self.class_name == 'Warlock':
                        for invocation in self.invocations:
                            if invocation['name'] == 'Eldritch Invocation: Repelling Blast':
                                output += colored(f"\t\tEldritch Blast also pushes target up to 10 feet away from you, because of Repelling Blast\n", 'white')
            else:
                for spell in self.spells_prepared:
                    if spell.level == spells_level:
                        output += colored(f"\t{spell.name}\n", 'green')
                        output += colored(f"\t\tSchool: {spell.school['name']}\n", 'white')
                        output += colored(f"\t\tRitual: {spell.ritual}\n", 'white')
                        output += colored(f"\t\tComponents: {spell.components}, {spell.material}\n", 'white')
                        output += colored(f"\t\tCnocentration: {spell.concentration}\n", 'white')
                        output += colored(f"\t\tCasting time: {spell.casting_time}\n", 'white')
                        output += colored(f"\t\tDuration: {spell.duration}\n", 'white')
                        output += colored(f"\t\tRange: {spell.range}\n", 'white')
                        if spell.damage is not None:
                            if 'damage_at_slot_level' in spell.damage.keys():
                                output += colored(f"\t\tDamage: {spell.damage['damage_type']['name']}, Damage at slot level: {spell.damage['damage_at_slot_level']}  \n", 'white')
                            else:
                                output += colored(f"\t\tDamage: {spell.damage['damage_type']['name']}\n", 'white')
                        if spell.dc is not None:
                            output += colored(f"\t\tDC: {spell.dc['dc_type']['name']}, DC success: {spell.dc['dc_success']}\n", 'white')
                        output += colored(f"\t\tDescription: {spell.desc}\n", 'white')
        print(output)

    def __iter__(self) -> Iterator[tuple[str, Union[dict, list, int, str, bool, None]]]:
        """
        Enables `dict(self)` to return a dictionary representation of this object.
        Iterate over this object to get (key, value) pairs.

        Attrs starting with _ are skipped, as we assume they are non-serializable.
        Such attrs must be added manually to the functions in this method.
        """

        def keys() -> list[str]:
            keys = [key for key in self.__dict__ if not key.startswith("_")]
            keys.extend(
                [
                    "experience",
                    "death_saves",
                    "death_fails",
                    "dexterity",
                    "dead",
                    "current_hp",
                    "inventory",
                    "cantrips_known",
                    "spells_known",
                    "spells_prepared",
                ]
            )
            return keys

        def values() -> list[Union[dict, list, int, str, bool, None]]:
            vals = [
                value if key != "uid" else str(value)
                for key, value in self.__dict__.items()
                if not key.startswith("_")
            ]
            vals.extend(
                [
                    self._experience._experience,
                    self._death_saves,
                    self._death_fails,
                    self._dexterity,
                    self._dead,
                    self._current_hp,
                    [dict(item) for item in self._inventory],
                    [dict(spell) for spell in self._cantrips_known],
                    [dict(spell) for spell in self._spells_known],
                    [dict(spell) for spell in self._spells_prepared],
                ]
            )
            return vals

        return zip(keys(), values())

    def __repr__(self) -> str:
        """Returns a string that could be copy-pasted to create a new instance of this object"""
        quote = lambda value: "'" if type(value) is str else ""
        kwargs = [f"{key}={quote(value)}{value}{quote(value)}" for key, value in self]
        return f"{type(self).__name__}({', '.join(kwargs)})"

    def __eq__(self, other) -> bool:
        """
        Check if `other` is an identical character to `self`
        Or if `other` is a dict that would construct an identical character
        """
        if type(other) is dict:
            other = Character(**other)
        if not isinstance(other, type(self)):
            return False
        for pair1, pair2 in zip(self, other):
            if pair1 != pair2:
                return False
        return True

    @property
    def class_features_data(self):
        return self._class_features_data

    @property
    def cantrips_known(self) -> SpellList["_SPELL"]:
        return self._cantrips_known

    @cantrips_known.setter
    def cantrips_known(self, new_val) -> None:
        if len(new_val) > self._cantrips_known.maximum:
            raise ValueError(
                f"Too many spells in list (max {self._cantrips_known.maximum})"
            )
        self._cantrips_known = (
            new_val if isinstance(new_val, SpellList) else SpellList(initial=new_val)
        )

    @property
    def spells_known(self) -> SpellList["_SPELL"]:
        return self._spells_known

    @spells_known.setter
    def spells_known(self, new_val) -> None:
        if len(new_val) > self._spells_known.maximum:
            raise ValueError(
                f"Too many spells in list (max {self._spells_known.maximum})"
            )
        self._spells_known = (
            new_val if isinstance(new_val, SpellList) else SpellList(initial=new_val)
        )

    @property
    def spells_prepared(self) -> SpellList["_SPELL"]:
        return self._spells_prepared

    @spells_prepared.setter
    def spells_prepared(self, new_val) -> None:
        if len(new_val) > self._spells_prepared.maximum:
            raise ValueError(
                f"Too many spells in list (max {self._spells_prepared.maximum})"
            )
        self._spells_prepared = (
            new_val if isinstance(new_val, SpellList) else SpellList(initial=new_val)
        )

    def prepare_spell(self, name: str) -> None:
        self.spells_prepared.append(SPELLS[name.lower().replace(' ', '-')])

    def remove_spell(self, name: str) -> None:
        self.spells_prepared.remove(SPELLS[name.lower().replace(' ', '-')])

    @property
    def inventory(self) -> list[_Item]:
        return self._inventory
    
    @property
    def magicinventory(self) -> list[_MagicItem]:
        return self._magicinventory

    @property
    def dead(self) -> bool:
        return self._dead

    @dead.setter
    def dead(self, new_value: bool) -> None:
        self._dead = new_value
        self._death_saves = 0
        self._death_fails = 0

    @property
    def death_saves(self) -> int:
        return self._death_saves

    @death_saves.setter
    def death_saves(self, new_value: int) -> None:
        if not 4 > new_value > -1:
            raise ValueError("Death saving throws must be in range 0-3")
        elif new_value == 3:
            self._death_saves = 0
            self._death_fails = 0
            self._dead = False
        else:
            self._death_saves = new_value

    @property
    def death_fails(self) -> int:
        return self._death_fails

    @death_fails.setter
    def death_fails(self, new_value: int) -> None:
        if not 4 > new_value > -1:
            raise ValueError("Death saving throws must be in range 0-3")
        elif new_value == 3:
            self._death_saves = 0
            self._death_fails = 0
            self._dead = True
        else:
            self._death_fails = new_value

    @property
    def current_hp(self) -> int:
        return self._current_hp

    @current_hp.setter
    def current_hp(self, new_value: int) -> None:
        if new_value < 0:
            new_value = 0
        elif new_value > self.max_hp:
            new_value = int(self.max_hp)
        self._current_hp = new_value

    @property
    def dexterity(self) -> int:
        return self._dexterity

    @dexterity.setter
    def dexterity(self, new_value: int) -> None:
        self._dexterity = new_value
        # self.armor_class = self.base_armor_class
        # for item in self.inventory:
        #     self.apply_armor_class(item)

    @property
    def experience(self) -> Experience:
        return self._experience.experience

    @experience.setter
    def experience(self, new_val: int) -> None:
        if new_val is None:
            pass
        elif type(new_val) is Experience:
            self._experience = new_val
        else:
            self._experience._experience = new_val
            self._experience.update_level()

    @property
    def origin(self) -> str:
        if self.class_name != 'Sorcerer':
            raise AttributeError("Only sorcerers have origins.")
        else:
            return self._origin

    @origin.setter
    def origin(self, new_origin: str) -> None:
        if new_origin not in [None, "Draconic Bloodline", "Wild Magic"]:
            raise ValueError("Invalid origin")
        self._origin = new_origin
        origin_features_list = []
        if new_origin == "Draconic Bloodline":
            self.languages.append('Draconic')
            if self.dragon_ancestor == 'red':
                origin_features_list.append('/api/2014/features/dragon-ancestor-red---fire-damage')
            elif self.dragon_ancestor == 'brass':
                origin_features_list.append('/api/2014/features/dragon-ancestor-brass---fire-damage')
            elif self.dragon_ancestor == 'black':
                origin_features_list.append('/api/2014/features/dragon-ancestor-black---acid-damage')
            elif self.dragon_ancestor == 'blue':
                origin_features_list.append('/api/2014/features/dragon-ancestor-blue---lightning-damage')
            elif self.dragon_ancestor == 'bronze':
                origin_features_list.append('/api/2014/features/dragon-ancestor-bronze---lightning-damage')
            elif self.dragon_ancestor == 'copper':
                origin_features_list.append('/api/2014/features/dragon-ancestor-copper---acid-damage')
            elif self.dragon_ancestor == 'gold':
                origin_features_list.append('/api/2014/features/dragon-ancestor-gold---fire-damage')
            elif self.dragon_ancestor == 'green':
                origin_features_list.append('/api/2014/features/dragon-ancestor-green---poison-damage')
            elif self.dragon_ancestor == 'silver':
                origin_features_list.append('/api/2014/features/dragon-ancestor-silver---cold-damage')
            elif self.dragon_ancestor == 'white':
                origin_features_list.append('/api/2014/features/dragon-ancestor-white---cold-damage')
            origin_features_list.append('/api/features/draconic-resilience')
            origin_features_list.append('/api/features/elemental-affinity')
            origin_features_list.append('/api/features/dragon-wings')
            origin_features_list.append('/api/features/draconic-presence')
        elif new_origin == "Wild Magic":
            pass
            # origin_features_list.append('/api/features/fiendish-resilience')
            # origin_features_list.append('/api/features/hellish-rebuke')
            # origin_features_list.append('/api/features/fiendish-resilience')
            # origin_features_list.append('/api/features/infernal-calling')
        if self.level >= 1:
            self.origin_features.append(SRD(origin_features_list[0]))
            self.origin_features.append(SRD(origin_features_list[1]))
        if self.level >= 6:
            self.origin_features.append(SRD(origin_features_list[2]))
        if self.level >= 14:
            self.origin_features.append(SRD(origin_features_list[3]))
        if self.level >= 18:
            self.origin_features.append(SRD(origin_features_list[4]))

    @property
    def patron(self) -> str:
        if self.class_name != 'Warlock':
            raise AttributeError("Only warlocks have patrons.")
        else:
            return self._patron

    @patron.setter
    def patron(self, new_patron: str) -> None:
        if new_patron not in [None, "The Archfey", "The Fiend", "The Great Old One"]:
            raise ValueError("Invalid patron")
        self._patron = new_patron
        patron_features_list = []
        if new_patron == "The Archfey":
            patron_features_list.append('/api/features/fey-presence')
            patron_features_list.append('/api/features/misty-escape')
            patron_features_list.append('/api/features/beguiling-defenses')
            patron_features_list.append('/api/features/dark-delirium')
        elif new_patron == "The Fiend":
            patron_features_list.append('/api/features/fiendish-resilience')
            patron_features_list.append('/api/features/hellish-rebuke')
            patron_features_list.append('/api/features/fiendish-resilience')
            patron_features_list.append('/api/features/infernal-calling')
        elif new_patron == "The Great Old One":
            patron_features_list.append('/api/features/awakened-mind')
            patron_features_list.append('/api/features/entropic-ward')
            patron_features_list.append('/api/features/thought-shield')
            patron_features_list.append('/api/features/create-thrall')
        if self.level >= 1:
            self.patron_features.append(SRD(patron_features_list[0]))
        if self.level >= 6:
            self.patron_features.append(SRD(patron_features_list[1]))
        if self.level >= 10:
            self.patron_features.append(SRD(patron_features_list[2]))
        if self.level >= 14:
            self.patron_features.append(SRD(patron_features_list[3]))

    @property
    def classs(self) -> Optional["_CLASS"]:
        return self.__class

    @classs.setter
    def classs(self, new_class: Optional["_CLASS"]) -> None:
        """
        Triggered when the character's class is changed
        """
        if isinstance(new_class, dict):
            # backwards compatibility
            from classes import CLASSES

            # LOG.warning("Implicitly converting classs dict to dataclass.")
            new_class = CLASSES[new_class["index"]]

        self.__class = new_class
        if new_class is None:
            return

        def set_class() -> None:
            """
            Set miscellaneous class-related properties such as:
            class name, hit dice, level progression data, proficiencies, saving throws,
            spellcasting, and class features
            """
            self.class_name = new_class.name
            self.class_index = new_class.index
            self.hd = new_class.hit_die
            self._class_levels = SRD_class_levels[self.class_index]
            # Set spellcasting stat to the full name of an ability score
            ability = {"wis": "wisdom", "cha": "charisma", "int": "intelligence"}
            if new_class.spellcasting:
                self.spellcasting_stat = ability[
                    new_class.spellcasting["spellcasting_ability"]["index"]
                ]
            else:
                self.spellcasting_stat = None
            self.apply_class_level()

            # create dict such as { "all-armor": {"name": "All armor", "type": "Armor"} }
            for proficiency in new_class.proficiencies:
                data = SRD(proficiency["url"])
                self.proficiencies[proficiency["index"]] = {
                    "name": data["name"],
                    "type": data["type"],
                }

            self.saving_throws_proficiency = [
                saving_throw["name"] for saving_throw in new_class.saving_throws
            ]

        def set_starting_equipment() -> None:
            """
            Sets `player_options["starting_equipment"]` to a list of strings
            """
            for starting_equipment in new_class.starting_equipment:
                new_item = Item(starting_equipment["equipment"]["index"])
                new_item.quantity = starting_equipment["quantity"]
                self.give_item(new_item.name)

            self.player_options["starting_equipment"] = []

            def add_to_starting_options(choice: str) -> None:
                self.player_options["starting_equipment"].append(choice)

            def fetch_choices_string(option: dict[str, dict[str, str]]) -> str:
                choices = SRD(option["equipment_category"]["url"])["equipment"]
                choices_names = [c["name"] for c in choices]
                return "{} (choice from {})".format(
                    option["equipment_category"]["name"], ", ".join(choices_names)
                )

            for item_option in new_class.starting_equipment_options:
                options = []
                opts = item_option["from"]
                if "options" not in opts.keys():
                    choices = fetch_choices_string(opts)
                    add_to_starting_options(choices)

                else:
                    for opt in opts["options"]:
                        opt_type = opt["option_type"]
                        if opt_type == "counted_reference":
                            options.append(
                                "{} x {}".format(opt["count"], opt["of"]["name"])
                            )
                        elif opt_type == "choice":
                            how_many = opt["choice"]["choose"]
                            choices = fetch_choices_string(opt["choice"]["from"])
                            options.append("{} x {}".format(how_many, choices))
                        elif opt_type == "multiple":
                            try:
                                combo = [
                                    str(c["count"]) + " " + c["of"]["name"]
                                    for c in opt["items"]
                                ]
                                add_to_starting_options("{}".format(", ".join(combo)))
                            except KeyError:
                                # shield or martial weapon
                                martial_weapons = fetch_choices_string(
                                    opt["items"][0]["choice"]["from"]
                                )
                                shield = opt["items"][1]["of"]["name"]
                                add_to_starting_options(
                                    "choose 1 from {} or a {}".format(
                                        martial_weapons, shield
                                    )
                                )
                                continue

                    add_to_starting_options("choose from {}".format(", ".join(options)))

        set_class()
        # set_starting_equipment()

    def set_saving_throw_bonuses(self) -> None:
        """
        Set saving throws bonuses based on ability modifiers and nothing else.
        Set a bonus manually for special modifiers. Do not include proficiency
        """
        mod = self.get_ability_modifier(self.strength)
        self.saving_throws['STR'] = mod
        mod = self.get_ability_modifier(self.dexterity)
        self.saving_throws['DEX'] = mod
        mod = self.get_ability_modifier(self.constitution)
        self.saving_throws['CON'] = mod
        mod = self.get_ability_modifier(self.intelligence)
        self.saving_throws['INT'] = mod
        mod = self.get_ability_modifier(self.wisdom)
        self.saving_throws['WIS'] = mod
        mod = self.get_ability_modifier(self.charisma)
        self.saving_throws['CHA'] = mod

    # def show_saving_throws(self) -> None:
    #     """
    #     Show saing throws bonuses
    #     """
    #     for save in self.saving_throws.keys():
    #         if save in self.saving_throws_proficiency:
    #             print(colored(save, 'green') + f': {self.saving_throws[save]} + {self.prof_bonus}')
    #         else:
    #             print(colored(save, 'green') + f': {self.saving_throws[save]}')

    def set_skill_proficiency(self, skill: str) -> None:
        """
        Sets proficiency to a skill
        """
        self.skills_proficiency[skill.lower()] = True
    
    # def show_skill_bonuses(self) -> None:
    #     """
    #     Show skill bonuses
    #     """
    #     for skill in self.skill_bonuses.keys():
    #         mod = self.skill_bonuses[skill]
    #         if self.skills_proficiency[skill]:
    #             print(colored(skill, 'green') + f': {mod} + {self.prof_bonus}')
    #         else:
    #             print(colored(skill, 'green') + f': {mod}')

    def set_skill_bonuses(self) -> None:
        """
        Set skill bonuses based on ability modifiers and nothing else.
        Set a bonus manually for special modifiers. Do not include proficiency
        """
        mod = self.get_ability_modifier(self.strength)
        for skill in self.skills_strength.keys():
            self.skill_bonuses[skill] = mod
        mod = self.get_ability_modifier(self.charisma)
        for skill in self.skills_charisma.keys():
            self.skill_bonuses[skill] = mod
        mod = self.get_ability_modifier(self.dexterity)
        for skill in self.skills_dexterity.keys():
            self.skill_bonuses[skill] = mod
        mod = self.get_ability_modifier(self.intelligence)
        for skill in self.skills_intelligence.keys():
            self.skill_bonuses[skill] = mod
        mod = self.get_ability_modifier(self.wisdom)
        for skill in self.skills_wisdom.keys():
            self.skill_bonuses[skill] = mod

    def give_feat(self, feat: str) -> None:
        self.feats[SRD_feats[feat]['index']] = SRD_feats[feat]

    def apply_class_level(self) -> None:
        """
        Applies changes based on the character's class and level
        e.g., adds new class features, spell slots
        Called by `level.setter` and `classs.setter`
        """
        if not self._class_levels or self.level > 20:
            return
        for data in self._class_levels:
            if data["level"] > self.level:
                break
            self.ability_score_bonus = data.get(
                "ability_score_bonuses", self.ability_score_bonus
            )
            self.prof_bonus = data.get("prof_bonus", self.prof_bonus)
            for feat in data["features"]:
                # print(str(self.class_features[feat["index"]]))
                self.class_features[feat["index"]] = SRD(feat["url"])

        while len(self.class_features_enabled) < len(self.class_features):
            self.class_features_enabled.append(True)

        # During level up some class specific values change. example: rage damage bonus 2 -> 4
        # Class specific counters do not reset! example: available inspirations
        new_cfd = get_class_features_data(character=self)
        if new_cfd is None:
            self._class_features_data = None
        else:
            if self._class_features_data is None:
                self._class_features_data = new_cfd
            else:
                self._class_features_data = {
                    k: v
                    if "available" not in k and "days" not in k
                    else self._class_features_data[k]
                    for k, v in new_cfd.items()
                }

        # Fetch new spell slots
        spell_slots = (
            self._class_levels[self.level - 1]
            .get("spellcasting", self.spell_slots)
            .copy()
        )
        spell_slots.pop("cantrips_known", None)
        spell_slots.pop("spells_known", None)
        self.update_spell_lists()
        self.set_spell_slots(spell_slots)

    def update_spell_lists(self) -> None:
        """Set maximum of spells_known, spells_prepared, cantrips_known"""
        spell_slots = (
            self._class_levels[self.level - 1]
            .get("spellcasting", self.spell_slots)
            .copy()
        )
        # Set maximums of _spells_known and _cantrips_known
        if "cantrips_known" in spell_slots:
            self._cantrips_known.maximum = spell_slots.pop("cantrips_known")
        if "spells_known" in spell_slots:
            self._spells_known.maximum = spell_slots.pop("spells_known")
        # Calculate new maximum of spells_prepared
        if self.spellcasting_stat is not None:
            self._spells_prepared.maximum = max(
                self.get_ability_modifier(self.__dict__[self.spellcasting_stat])
                + self.level,
                1,
            )

    def set_spell_slots(self, new_spell_slots: Optional[dict[str, int]]) -> None:
        default_spell_slots = {
            "spell_slots_level_1": 0,
            "spell_slots_level_2": 0,
            "spell_slots_level_3": 0,
            "spell_slots_level_4": 0,
            "spell_slots_level_5": 0,
            "spell_slots_level_6": 0,
            "spell_slots_level_7": 0,
            "spell_slots_level_8": 0,
            "spell_slots_level_9": 0,
        }
        self.spell_slots = new_spell_slots if new_spell_slots is not None else {}
        for key in default_spell_slots:
            if key not in self.spell_slots:
                self.spell_slots[key] = default_spell_slots[key]

    @property
    def level(self) -> int:
        return self._level

    @level.setter
    def level(self, new_level: int) -> None:
        self._level = new_level
        # if self.current_hp == self.max_hp:
        #     self.current_hp = Character.get_maximum_hp(
        #         self.hd, new_level, self.constitution
        #     )
        # self.max_hp = Character.get_maximum_hp(self.hd, new_level, self.constitution)
        if self.current_hd == self.max_hd:
            self.current_hd = new_level
        self.max_hd = new_level
        if self.current_hd > self.max_hd:
            self.current_hd = self.max_hd
        self.apply_class_level()

    def remove_shields(self) -> None:
        """Removes all shields from self._inventory. Used by self.give_item when equipping shield"""
        for i, item in enumerate(self._inventory):
            if (
                item.equipment_category["index"] == "armor"
                and item.armor_category == "Shield"
            ):
                self._inventory.pop(i)

    def remove_armor(self) -> None:
        """Removes all armor from self._inventory. Used by self.give_item when equipping armor"""
        for i, item in enumerate(self._inventory):
            if (
                item.equipment_category["index"] == "armor"
                and item.armor_category != "Shield"
            ):
                self._inventory.pop(i)

    def apply_armor_class(self, item: _Item) -> None:
        if item.equipment_category["index"] == "armor":
            if item.armor_category == "Shield":
                self.remove_shields()
                try:
                    self.armor_class += item.armor_class["base"]
                except AttributeError:
                    # shield during __init__ without armor
                    self.armor_class = (
                        10
                        + item.armor_class["base"]
                        + Character.get_ability_modifier(self.dexterity)
                    )
            else:
                self.remove_armor()
                self.armor_class = item.armor_class["base"] + (
                    0
                    if not item.armor_class["dex_bonus"]
                    else Character.get_ability_modifier(self.dexterity)
                )

    @property
    def base_armor_class(self) -> int:
        return 10 + Character.get_ability_modifier(self.dexterity)

    def give_random_item(self, item: str) -> None:
        """
        Adds an custom item to the Character's inventory list.
        """
        random_item = Item({'name': item, 'cost': 0, 'contents': [], 'desc': [], 'index': item.lower().replace(' ', '-'),
                             'properties': [], 'special': [], 'url': None, 'equipment_category': []})
        self.inventory.append(random_item)

    def give_item(self, item: str) -> None:
        """
        Adds an item to the Character's inventory list.
        If the item is armor or a shield, the armor_class attribute will be set
        and any other armor/shields in the inventory will be removed.
        """
        # self.apply_armor_class(item)
        self.inventory.append(Item(item.lower().replace(' ', '-')))

    def remove_item(self, item: str) -> None:
        self._inventory.remove(Item(item.lower().replace(' ', '-')))
    
    def give_magic_item(self, item: str) -> None:
        """
        Adds a magic item to the Character's inventory list.
        """
        self.magicinventory.append(MagicItem(item.lower().replace(' ', '-')))

    def remove_magic_item(self, item: str) -> None:

        self.magicinventory.remove(MagicItem(item.lower().replace(' ', '-')))

    def change_wealth(
        self,
        pp: int = 0,
        gp: int = 0,
        ep: int = 0,
        sp: int = 0,
        cp: int = 0,
        conversion: bool = False,
    ) -> None:
        change = locals()
        change.pop("self", None)
        change.pop("conversion", None)

        total_change = sum([coin_value[u] * v for u, v in change.items()])
        new_wealth = round(self.wealth + total_change, 2)
        if new_wealth < 0:
            raise ValueError("Character has not enough wealth to cover the change!")

        if conversion:
            self.wealth_detailed = self.infer_wealth(new_wealth)
        else:
            for unit, value in change.items():
                new_value = self.wealth_detailed[unit] + value
                if new_value < 0:
                    raise ValueError(
                        f"Character has not enough {unit}! Current balance: {self.wealth_detailed[unit]}"
                    )
                self.wealth_detailed[unit] = new_value

        self.wealth = new_wealth

    @staticmethod
    def infer_wealth(wealth: Union[int, float]) -> dict[str, int]:
        """Estimates a reasonable coin distribution from gold denominated total wealth."""
        # Convert to platinum for smaller weight/volume
        if wealth > 100:
            pp = int((wealth - 100) / 10)
            gp = wealth - 10 * pp
        else:
            pp = 0
            gp = wealth

        # Convert fractional part to silver and copper (no electrum!)
        gp_str = "{:.2f}".format(gp)  # two decimal rounded gp to two decimal string
        gp_str_decimal = gp_str.split(".")[1]
        sp = int(gp_str_decimal[0])
        cp = int(gp_str_decimal[1])
        gp = int(gp)

        return {"pp": pp, "gp": gp, "ep": 0, "sp": sp, "cp": cp}

    @staticmethod
    def set_initial_ability_score(stat: Optional[int]) -> int:
        """
        Set ability score to an int. If the argument is None, then this method
        instead rolls for the initial starting ability score.
        """
        if stat is None:
            return sum_rolls(d6=4, drop_lowest=True)  # roll 4d6, drop lowest
        else:
            return int(stat)

    @staticmethod
    def get_ability_modifier(number: int) -> int:
        """
        This method returns the modifier for the given stat (INT, CON, etc.)
        The formula for this is (STAT - 10 / 2) so e.g. 14 results in 2
        """
        return (number - 10) // 2

    @staticmethod
    def get_maximum_hp(hd: int, level: int, constitution: int) -> int:
        """
        Calculate maximum hitpoints using hit dice (HD), level and constitution modifier
        """
        return (
            hd
            + ((int(hd / 2) + 1) * (level - 1))
            + Character.get_ability_modifier(constitution)
        )

    @property
    def speciess(self) -> Optional["_SPECIES"]:
        return self.__species

    @speciess.setter
    def speciess(self, new_species: Optional["_SPECIES"]) -> None:
        """
        Triggered when the character's species is changed
        """
        if isinstance(new_species, dict):
            # backwards compatibility
            from species import SPECIES

            # LOG.warning("Implicitly converting species dict to dataclass.")
            new_species = SPECIES[new_species["index"]]

        self.__species = new_species
        if new_species is None:
            return

        def set_species() -> None:
            """
            Set miscellaneous species-related properties such as:
            species name, traits, lannguages, speed,
            size and subraces
            """
            self.species_name = new_species.name
            self.species_index = new_species.index
            self.speed = new_species.speed
            self.size = new_species.size
            self.size_description = new_species.size_description
            
            # create dict such as { "all-armor": {"name": "All armor", "type": "Armor"} }
            for trait in new_species.traits:
                data = SRD(trait["url"])
                self.traits[trait["index"]] = {
                    "name": data["name"],
                    "desc": data["desc"],
                }

            self.languages = [
                languages["name"] for languages in new_species.languages
            ]

            # self.apply_species()
        
        set_species()
        # set_starting_equipment()