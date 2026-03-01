from typing import Optional
from dataclasses import dataclass
from SRD import SRD_species

@dataclass(kw_only=True, frozen=True, slots=True)
class _SPECIES:
    """
    Dataclass for (D&D 5e) species. Species are suggested to be constants. (Immutable.)
    So deserialization shouldn't be necessary, but is possible with _SPECIES(**dict).
    Or get the constant version from `dnd_character.species.SPECIES[species_name]`
    """

    index: str
    name: str
    url: str
    speed: int
    ability_bonuses: list[dict]
    age: str
    alignment: str
    size_description: str
    languages: list[dict]
    language_desc: str
    traits: list[dict]
    subraces: list[dict]
    size: str
    updated_at: str
    ability_bonus_options: Optional[dict] = None
    language_options: Optional[dict] = None

SPECIES = {
    species_index: _SPECIES(**species_data) for species_index, species_data in SRD_species.items()
}
