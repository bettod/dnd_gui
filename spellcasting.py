import logging
import json
from typing import Union, Optional
from dataclasses import dataclass, asdict
from termcolor import colored
from SRD import SRD, SRD_endpoints, SRD_classes


LOG = logging.getLogger(__package__)
SRD_spells = {
    spell["index"]: SRD(spell["url"])
    for spell in SRD(SRD_endpoints["spells"])["results"]
}
# Custom spells
with open('./json_cache/api_spells_toll-the-dead.json') as json_file:
    data = json.load(json_file)
SRD_spells.update({data['index']:data})
with open('./json_cache/api_spells_aura-of-vitality.json') as json_file:
    data = json.load(json_file)
SRD_spells.update({data['index']:data})
with open('./json_cache/api_spells_lightning-lure.json') as json_file:
    data = json.load(json_file)
SRD_spells.update({data['index'] : data})
with open('./json_cache/api_spells_dissonant-whispers.json') as json_file:
    data = json.load(json_file)
SRD_spells.update({data['index'] : data})
with open('./json_cache/api_spells_hex.json') as json_file:
    data = json.load(json_file)
SRD_spells.update({data['index'] : data})
with open('./json_cache/api_spells_witch-bolt.json') as json_file:
    data = json.load(json_file)
SRD_spells.update({data['index'] : data})
with open('./json_cache/api_spells_friends.json') as json_file:
    data = json.load(json_file)
SRD_spells.update({data['index'] : data})
with open('./json_cache/api_spells_crown-of-madness.json') as json_file:
    data = json.load(json_file)
SRD_spells.update({data['index'] : data})

@dataclass(kw_only=True, frozen=True, slots=True)
class _SPELL:
    """
    Dataclass for spells. Spells are suggested to be constants. (Immutable.)
    So deserialization shouldn't be necessary, but is possible with _SPELL(**dict).
    Or get the constant version from `dnd_character.spellcasting.SPELLS[spell_name]`
    """

    area_of_effect: Optional[dict[str, Union[str, int]]] = None
    attack_type: Optional[str] = None
    casting_time: str
    classes: list[dict[str, str]]
    components: list[str]
    concentration: bool
    damage: Optional[dict[str, dict[str, str]]] = None
    dc: Optional[dict[str, Union[str, dict[str, str]]]] = None
    desc: list[str]
    duration: str
    heal_at_slot_level: Optional[list[str]] = None
    higher_level: list[str]
    material: Optional[str] = None
    index: str
    level: int
    name: str
    range: str
    ritual: bool
    school: dict[str, str]
    subclasses: list[dict[str, str]]
    url: str

    def __iter__(self):
        me = asdict(self)
        for k, v in me.items():
            yield k, v

    def __str__(self) -> str:
        output = ""
        output += colored(f"Name: ", 'green') + colored(f"{self.name}\n", 'red')
        output += colored(f"Level: ", 'green') + colored(f"{str(self.level)}\n", 'white')
        output += colored(f"School: ", 'green') + f"{str(self.school['name'])}\n"
        output += colored(f"Classes: ", 'green')
        for item in self.classes:
            output += colored(f"{item['name']}: ", 'cyan')
        output += f"\n"
        output += colored(f"Components:", 'green') + f"\t{', '.join([item for item in self.components])}\n"
        if self.material:
            output += colored(f"\tMaterial: ", 'yellow') + colored(f"{self.material}\n", 'white')   
        output += colored(f"Casting Time: ", 'green') + colored(f"{self.casting_time}\n", 'white')
        output += colored(f"Duration: ", 'green') + colored(f"{self.duration}\n", 'white')
        if self.concentration:
            output += colored(f"Concentration: TRUE ", 'yellow')
        if self.ritual:
            output += colored(f"Ritual: TRUE ", 'yellow')
        output += colored(f"Range:", 'green') + f"\t{self.range}\n"
        if self.area_of_effect:
            output += colored(f"Area of Effect: ", 'green')
            for key in self.area_of_effect:
                output += colored(f"{key}: ", 'cyan') + f"{str(self.area_of_effect[key])}, "
            output += f"\n"
        if self.attack_type:
            output += colored(f"Attack Type: ", 'green') + colored(f"{self.attack_type}\n", 'white')
        if self.damage:
            output += colored(f"Damage: ", 'green')
            output += colored(f"\tDamage Type: ", 'yellow') + f"{str(self.damage['damage_type']['name'])}, "
            if self.level == 0:
                output += colored(f"\tDamage at Char Level: ", 'yellow') + f"{str(self.damage['damage_at_character_level'])}, "
            else:
                output += colored(f"\tDamage at Slot Level: ", 'yellow') + f"{str(self.damage['damage_at_slot_level'])}, "
            output += f"\n"
        if self.dc:
            output += colored(f"DC: ", 'green')
            output += colored(f"\tType: ", 'yellow') + f"{str(self.dc['dc_type']['name'])}, "
            output += colored(f"\tSuccess: ", 'yellow') + f"{str(self.dc['dc_success'])}, "
            output += f"\n"
        if self.heal_at_slot_level:
            output += colored(f"Heat at Slot Level:", 'green') + f"\t{', '.join([item for item in self.heal_at_slot_level])}\n"
        output += colored(f"Description: ", 'green') + colored(f"{self.desc}\n", 'white')
        output += colored(f"Higher Level: ", 'green') + colored(f"{self.higher_level}\n", 'white')
        return output


SPELLS: dict[str, _SPELL] = {
    index: _SPELL(**spell) for index, spell in SRD_spells.items()
}



def Spell(spell: Union[str, dict]) -> _SPELL:
    """
    Create new Spell by calling with string (e.g., fireball)
    Deserialize spell by calling with a dict
    """
    if type(spell) == str:
        # new spell
        return _SPELL(**SRD_spells[spell])
    else:
        # deserialized monster
        return _SPELL(**spell)

class SpellList(list):
    """A list with a maximum size, for storing spells and cantrips"""

    def __init__(self, initial: Optional[list["_SPELL"]]) -> None:
        initial = initial if initial is not None else []
        self._maximum: int = len(initial)
        super().__init__(initial)

    @property
    def maximum(self) -> int:
        return self._maximum

    @maximum.setter
    def maximum(self, new_val: int) -> None:
        if len(self) > new_val:
            LOG.error("Too many spells in spell list to lower its maximum.")
            return
        self._maximum = new_val

    def append(self, new_val: "_SPELL") -> None:
        if len(self) + 1 > self.maximum:
            self.maximum += 1
        super().append(new_val)


spell_names_by_level = {
    i: [key for key, val in SRD_spells.items() if val["level"] == i] for i in range(10)
}

spell_names_by_class = {
    i: [
        key
        for key, val in SRD_spells.items()
        if i in (cindex["index"] for cindex in val["classes"])
    ]
    for i in SRD_classes.keys()
}


def spells_for_class_level(classs: str, level: int) -> set:
    if level > 9 or level < 0:
        raise ValueError("Spell levels only go from 0-9")
    return set(spell_names_by_class[classs]).intersection(
        set(spell_names_by_level[level])
    )



def show_spell_list() -> None:
    """
    Print the list of spells
    """
    for key in SRD_spells:
        print(colored(SRD_spells[key]['name'], 'red') + ':\tLevel = ' + str(SRD_spells[key]['level']))

def show_spells_by_class_level(classs: str, level: int) -> None:
    """
    Print the list of spell by class and level
    """
    for key in SRD_spells:
        if SRD_spells[key]['level'] == level:
            for item in SRD_spells[key]['classes']:
                if classs.lower() == item['name'].lower():
                    print(SRD_spells[key]['name'])

def show_spell(spell: str) -> None:
    """
    Print details of a spell
    """
    print(str(Spell(spell.lower().replace(' ', '-'))))