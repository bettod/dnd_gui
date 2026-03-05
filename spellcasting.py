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
        output += f"<span style='color:green;'>School: </span>{str(self.school['name'])}\n"
        output += f"<span style='color:green;'>Classes: </span>"
        for item in self.classes:
            output += f"<span style='color:cyan;'>{item['name']}: </span>"
        output += f"\n"
        output += f"<span style='color:green;'>Components:</span> {', '.join([item for item in self.components])}\n"
        if self.material:
            output += f"<span style='color:yellow;'>\tMaterial: </span><span style='color:white;'>{self.material}</span>\n"
        output += f"<span style='color:green;'>Casting Time: </span><span style='color:white;'>{self.casting_time}</span>\n"
        output += f"<span style='color:green;'>Duration: </span><span style='color:white;'>{self.duration}</span>\n"
        if self.concentration:
            output += f"<span style='color:yellow;'>Concentration: TRUE </span>"
        if self.ritual:
            output += f"<span style='color:yellow;'>Ritual: TRUE </span>"
        output += f"<span style='color:green;'>Range:</span> {self.range}\n"
        if self.area_of_effect:
            output += f"<span style='color:green;'>Area of Effect: </span>"
            for key in self.area_of_effect:
                output += f"<span style='color:cyan;'>{key}: </span>{str(self.area_of_effect[key])}, "
            output += f"\n"
        if self.attack_type:
            output += f"<span style='color:green;'>Attack Type: </span><span style='color:white;'>{self.attack_type}</span>\n"
        if self.damage:
            output += f"<span style='color:green;'>Damage: </span>"
            if 'damage_type' in self.damage.keys():
                output += f"<span style='color:yellow;'>\tDamage Type: </span><span style='color:white;'>{str(self.damage['damage_type']['name'])}</span>, "
            if self.level == 0:
                output += f"<span style='color:yellow;'>\tDamage at Char Level: </span><span style='color:white;'>{str(self.damage['damage_at_character_level'])}</span>, "
            else:
                output += f"<span style='color:yellow;'>\tDamage at Slot Level: </span><span style='color:white;'>{str(self.damage['damage_at_slot_level'])}</span>, "
            output += f"\n"
        if self.dc:
            output += f"<span style='color:green;'>DC: </span>"
            output += f"<span style='color:yellow;'>\tType: </span><span style='color:white;'>{str(self.dc['dc_type']['name'])}</span>, "
            output += f"<span style='color:yellow;'>\tSuccess: </span><span style='color:white;'>{str(self.dc['dc_success'])}</span>, "
            output += f"\n"
        if self.heal_at_slot_level:
            output += f"<span style='color:green;'>Heal at Slot Level: </span><span style='color:white;'>{', '.join([item for item in self.heal_at_slot_level])}</span>\n"
        output += f"<span style='color:green;'>Description: </span><span style='color:white;'>{self.desc}</span>\n"
        output += f"<span style='color:green;'>Higher Level: </span><span style='color:white;'>{self.higher_level}</span>\n"
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
        print(f"<span style='color:red;'>{SRD_spells[key]['name']}</span>:\tLevel = {SRD_spells[key]['level']}")

def show_spells_by_class_level(classs: str, level: int) -> None:
    """
    Print the list of spell by class and level
    """
    for key in SRD_spells:
        if SRD_spells[key]['level'] == level:
            for item in SRD_spells[key]['classes']:
                if classs.lower() == item['name'].lower():
                    print(f"<span style='color:red;'>{SRD_spells[key]['name']}</span>")

def show_spell(spell: str) -> None:
    """
    Print details of a spell
    """
    # print(str(Spell(spell.lower().replace(' ', '-').replace("'", '').replace("/", '-'))))
    return str(Spell(spell.lower().replace(' ', '-').replace("'", '').replace("/", '-')))