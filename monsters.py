from uuid import uuid4
from typing import Optional, Union
from dataclasses import dataclass, asdict
from termcolor import colored
from SRD import SRD_endpoints, SRD


SRD_monsters = {
    result["index"]: SRD(result["url"])
    for result in SRD(SRD_endpoints["monsters"])["results"]
}


@dataclass(kw_only=True)
class _Monster:
    """Dataclass for monsters. Deserialize monster with `_Monster(**dict)` or Monster() function"""

    index: str
    uid: str = uuid4().hex
    type: str
    subtype: Optional[str] = None
    desc: Optional[str] = None
    image: Optional[str] = None
    images: Optional[str] = None
    url: str
    name: str
    size: str
    alignment: str
    armor_class: list[dict[str, Union[str, int]]]
    hit_points: int
    hit_dice: str
    hit_points_roll: str
    speed: dict[str, str]
    strength: int
    dexterity: int
    constitution: int
    intelligence: int
    wisdom: int
    charisma: int
    proficiencies: list[dict[str, Union[str, dict[str, str]]]]
    damage_vulnerabilities: list[str] = None
    damage_resistances: list[str] = None
    damage_immunities: list[str] = None
    condition_immunities: list[dict[str, str]] = None
    senses: dict[str, Union[str, int]] = None
    languages: str
    challenge_rating: float
    xp: int
    special_abilities: list[dict[str, str]] = None
    legendary_actions: list[dict[str, str]] = None
    actions: list[dict]
    reactions: Optional[list[dict]] = None
    forms: Optional[list[dict[str, str]]] = None

    def __iter__(self):
        me = asdict(self)
        for k, v in me.items():
            yield k, v

    def __str__(self) -> str:
        output = ""
        output += f"<span style='color:green;'>Size: </span>" + f"<span style='color:white;'>{self.size}\n</span>"
        output += f"<span style='color:green;'>Speed: </span>"
        for key in self.speed:
            output += f"<span style='color:cyan;'>{key}: </span>" + f"{str(self.speed[key])}, "
        output += f"\n"
        output += f"<span style='color:green;'>Alignment: </span>" + f"<span style='color:white;'>{self.alignment}\n</span>"
        output += f"<span style='color:green;'>Hit Points: </span>" + f"<span style='color:white;'>{str(self.hit_points)}\n</span>"
        output += f"<span style='color:green;'>Armor Class: </span>" + f"<span style='color:white;'>{str(self.armor_class[0]['value'])}, </span>" + f"<span style='color:white;'>{str(self.armor_class[0]['type'])}\n</span>"
        if self.desc:
            output += f"<span style='color:green;'>Description: </span>" + f"<span style='color:white;'>{self.desc}\n</span>"
        output += f"<span style='color:green;'>Challenge Rating: </span>" + f"<span style='color:white;'>{str(self.challenge_rating)}\n</span>"
        output += f"<span style='color:green;'>Senses:\n</span>"
        for key in self.senses:
            output += f"<span style='color:cyan;'>\t{key}: </span>" + f"{str(self.senses[key])}\n"
        output += f"<span style='color:green;'>Actions:\n</span>"
        for value in self.actions:
            output += f"<span style='color:cyan;'>\t{value['name']}: </span>" + f"{value['desc']}\n"
        if self.reactions:
            output += f"<span style='color:green;'>Reactions:\n</span>"
            for value in self.reactions:
                output += f"<span style='color:cyan;'>\t{value['name']}: </span>" + f"{value['desc']}\n"
        if self.damage_resistances:
            output += f"<span style='color:green;'>Damage Resistances:</span>" + f"\t{', '.join([item for item in self.damage_resistances])}\n"
        if self.damage_immunities:
            output += f"<span style='color:green;'>Damage Immunities:</span>" + f"\t{', '.join([item for item in self.damage_immunities])}\n"
        if self.damage_vulnerabilities:
            output += f"<span style='color:green;'>Damage Vulnerabilities:</span>" + f"\t{', '.join([item for item in self.damage_vulnerabilities])}\n"
        if self.condition_immunities:
            output += f"<span style='color:green;'>Condition immunities:</span>" + f"\t{', '.join([item['name'] for item in self.condition_immunities])}\n"
        if self.special_abilities:
            output += f"<span style='color:green;'>Special Abilities:\n</span>"
            for value in self.special_abilities:
                output += f"<span style='color:cyan;'>\t{value['name']}: </span>" + f"{value['desc']}\n"
        if self.legendary_actions:
            output += f"<span style='color:green;'>Legendary Actions:\n</span>"
            for value in self.legendary_actions:
                output += f"<span style='color:cyan;'>\t{value['name']}: </span>" + f"{value['desc']}\n"
        return output

def Monster(monster: Union[str, dict]) -> _Monster:
    """
    Create new Monster by calling with string (e.g., zombie)
    Deserialize monster by calling with a dict
    """
    if type(monster) == str:
        # new monster
        return _Monster(**SRD_monsters[monster])
    else:
        # deserialized monster
        return _Monster(**monster)



def show_monster_list() -> None:
    """
    Print the list of monsters
    """
    for key in SRD_monsters:
        print(colored(SRD_monsters[key]['name'], 'red') + ':\tchallenge rating = ' + str(SRD_monsters[key]['challenge_rating']))

def show_monsters_by_rating(rating: int) -> None:
    """
    Print the list of monsters by challenge rating
    """
    for key in SRD_monsters:
        if SRD_monsters[key]['challenge_rating'] == rating:
            print(SRD_monsters[key]['name'])

def show_monster(monster: str) -> None:
    """
    Print details of a monster
    """
    if monster.lower().startswith('were') or monster.lower().startswith('vampire'):
        monster = monster.lower().replace(' ', '-').replace(",", "").replace('-form', '')
    # print(str(Monster(monster.lower().replace(' ', '-').replace("(", "").replace(")", "").replace(",", "").replace("'", "").replace("/", "-"))))
    return str(Monster(monster.lower().replace(' ', '-').replace("(", "").replace(")", "").replace(",", "").replace("'", "").replace("/", "-")))