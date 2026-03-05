from typing import Union, Optional
from dataclasses import dataclass, asdict
from uuid import uuid4
from SRD import SRD_endpoints, SRD


SRD_equipment = {
    result["index"]: SRD(result["url"])
    for result in SRD(SRD_endpoints["equipment"])["results"]
}


@dataclass(kw_only=True)
class _Item:
    """Dataclass for items. Deserialize item with `_Item(**dict)` or Item() function"""

    uid: str = uuid4().hex
    contents: list[dict[str, Union[int, dict[str, str]]]]
    cost: dict[str, Union[str, int]]
    desc: list[str]
    index: str
    name: str
    properties: list[dict[str, str]]
    special: list
    url: str
    weight: int = 0
    quantity: int = 1
    stealth_disadvantage: bool = False
    str_minimum: int = 0

    # All items have an equipment category
    # This hints which of the below subcategories it belongs to
    equipment_category: dict[str, str]

    # Gear category
    gear_category: Optional[dict[str, str]] = None

    # Tool category
    tool_category: Optional[str] = None

    # Armor category
    armor_category: Optional[str] = None
    armor_class: Optional[dict[str, Union[int, bool]]] = None

    # Weapon category
    weapon_category: Optional[str] = None
    category_range: Optional[str] = None
    weapon_range: Optional[str] = None
    range: Optional[dict[str, int]] = None
    throw_range: Optional[dict[str, int]] = None
    damage: Optional[dict[str, Union[str, dict[str, str]]]] = None
    two_handed_damage: Optional[dict[str, Union[str, dict[str, str]]]] = None

    # Vehicle category
    vehicle_category: Optional[str] = None
    capacity: Optional[str] = None
    speed: Optional[dict[str, Union[str, int]]] = None

    def __iter__(self):
        me = asdict(self)
        for k, v in me.items():
            yield k, v
    
    def __str__(self) -> str:
        output = ''
        output += f"<span style='color:green'>Inventory:</span>\n"
        for item in self.inventory:
            output += f"<span style='color:green'>\t{item.name}</span>\n"
            if item.desc:
                output += f"<span style='color:white'>\t\t{item.desc}</span>\n"
            if item.special:
                output += f"<span style='color:white'>\t\t{item.special}</span>\n"
            if item.damage:
                output += f"<span style='color:white'>\t\t{item.damage['damage_dice']}, {item.damage['damage_type']['name']}</span>\n"
            if item.properties:
                for prop in item.properties:
                    output += f"<span style='color:white'>\t\t{prop['name']}</span>\n"
            if item.armor_class:
                output += f"<span style='color:white'>\t\tAC: {str(item.armor_class['base'])}, Dex bonus: {item.armor_class['dex_bonus']}</span>\n"
            if item.armor_category:
                output += f"<span style='color:white'>\t\t{item.armor_category}</span>\n"
        for item in self.magicinventory:
            output += f"<span style='color:green'>\t{item.name}</span>\n"
            output += f"<span style='color:white'>\t\t{item.desc}</span>\n"
        return output


def Item(item: Union[str, dict]) -> _Item:
    """
    Create new Item by calling with string (e.g., torch)
    Deserialize item by calling with a dict
    """
    if type(item) == str:
        return _Item(**SRD_equipment[item])
    else:
        return _Item(**item)
