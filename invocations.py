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
SRD_invocations = {
    invocation["index"]: SRD(invocation["url"])
    for invocation in SRD('/api/features/eldritch-invocations')['feature_specific']['invocations']
}
for invocation in SRD_invocations.keys():
    _ = SRD_invocations[invocation].pop('class')
# Custom invocations
# with open('./json_cache/api_2014_invocations.json') as json_file:
    # data = json.load(json_file)
# SRD_invocations.update({data['index']:data})

@dataclass(kw_only=True, frozen=True, slots=True)
class _INVOCATION:
    """
    Dataclass for invocations. Invocations are suggested to be constants. (Immutable.)
    So deserialization shouldn't be necessary, but is possible with _INVOCATIONS(**dict).
    Or get the constant version from INVOCATIONS[spell_name]`
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


INVOCATIONS: dict[str, _INVOCATION] = {
    index: _INVOCATION(**invocation) for index, invocation in SRD_invocations.items()
}

class InvocationList(list):
    """A list for storing invocations"""

    def __init__(self, initial: Optional[list["_INVOCATION"]]) -> None:
        initial = initial if initial is not None else []
        super().__init__(initial)

    def append(self, new_val: "_INVOCATION") -> None:
        super().append(new_val)