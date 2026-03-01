import logging
import json
from typing import Union, Optional
from dataclasses import dataclass, asdict
from SRD import SRD, SRD_endpoints

LOG = logging.getLogger(__package__)
SRD_feats = {
    feat["index"]: SRD(feat["url"])
    for feat in SRD(SRD_endpoints["feats"])["results"]
}
# Custom feats
with open('./json_cache/api_2014_feats_telekinetic.json') as json_file:
    data = json.load(json_file)
SRD_feats.update({data['index']:data})

@dataclass(kw_only=True, frozen=True, slots=True)
class _FEAT:
    """
    Dataclass for feats. Feats are suggested to be constants. (Immutable.)
    So deserialization shouldn't be necessary, but is possible with _FEAT(**dict).
    Or get the constant version from `dnd_character.feats.FEATS[feat_name]`
    """

    index: str
    name: str
    prerequisites: Optional[dict]
    desc: list[str]
    url: str
    updated_at: str

    def __iter__(self):
        me = asdict(self)
        for k, v in me.items():
            yield k, v


FEATS: dict[str, _FEAT] = {
    index: _FEAT(**feat) for index, feat in SRD_feats.items()
}