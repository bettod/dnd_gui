import logging
import json
from typing import Union, Optional
from dataclasses import dataclass, asdict
from SRD import SRD, SRD_endpoints

LOG = logging.getLogger(__package__)
# SRD_pacts = {
#     pact["index"]: SRD(pact["url"])
#     for pact in SRD('/api/features/pact-')['feature_specific']['pacts']
# }
SRD_metamagic = {
    metamagic['item']["index"].replace('metamagic-', ''): SRD(metamagic['item']["url"])
    for metamagic in SRD('/api/features/metamagic-1')['feature_specific']['subfeature_options']['from']['options']
}
for metamagic in SRD_metamagic.keys():
    _ = SRD_metamagic[metamagic].pop('class')
    if 'parent' not in SRD_metamagic[metamagic].keys():
        SRD_metamagic[metamagic].update({'parent': []})

# Custom metamagic
# with open('./json_cache/api_2014_metamagic.json') as json_file:
    # data = json.load(json_file)
# SRD_metamagic.update({data['index']:data})

@dataclass(kw_only=True, frozen=True, slots=True)
class _METAMAGIC:
    """
    Dataclass for metamagic. metamagic are suggested to be constants. (Immutable.)
    So deserialization shouldn't be necessary, but is possible with _metamagic(**dict).
    Or get the constant version from metamagic[spell_name]`
    """

    index: str
    name: str
    level: int
    prerequisites: Optional[dict]
    parent: Optional[dict]
    desc: list[str]
    url: str
    updated_at: str

    def __iter__(self):
        me = asdict(self)
        for k, v in me.items():
            yield k, v


METAMAGIC: dict[str, _METAMAGIC] = {
    index: _METAMAGIC(**metamagic) for index, metamagic in SRD_metamagic.items()
}

class MetamagicList(list):
    """A list for storing metamagic"""

    def __init__(self, initial: Optional[list["_METAMAGIC"]]) -> None:
        initial = initial if initial is not None else []
        super().__init__(initial)

    def append(self, new_val: "_METAMAGIC") -> None:
        super().append(new_val)