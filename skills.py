from typing import Union, Optional
from dataclasses import dataclass, asdict
from uuid import uuid4
from termcolor import colored
from SRD import SRD_endpoints, SRD


SRD_skills = {
    result["index"]: SRD(result["url"])
    for result in SRD(SRD_endpoints["skills"])["results"]
}


@dataclass(kw_only=True)
class _Skill:
    """Dataclass for skills. Deserialize item with `_Skill(**dict)` or Skill() function"""

    uid: str = uuid4().hex
    index: str
    name: str
    url: str
    ability_score: str
    desc: str
    updated_at: Optional[str] = None

    def __iter__(self):
        me = asdict(self)
        for k, v in me.items():
            yield k, v
    
    def __str__(self) -> str:
        output = ""
        output += colored(f"Name: ", 'green') + colored(f"{self.name}\n", 'red')
        output += colored(f"Ability Score: ", 'green') + colored(f"{self.ability_score['name']}\n", 'white')
        output += colored(f"Description: ", 'green') + colored(f"{self.desc}\n", 'white')
        return output


def Skill(item: Union[str, dict]) -> _Skill:
    """
    Create new Skill by calling with string (e.g., persuasion)
    Deserialize item by calling with a dict
    """
    if type(item) == str:
        return _Skill(**SRD_skills[item])
    else:
        return _Skill(**item)


def show_skill(skill: str) -> None:
    """
    Print details of a skill
    """
    print(str(Skill(skill.lower().replace(' ', '-'))))