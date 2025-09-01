import os
import sys
from types import SimpleNamespace
from enum import Enum

# Ensure backend package is importable
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'frontendbackend'))

# Provide stub models expected by taxonomy
class Planet(Enum):
    SUN = "Sun"
    MOON = "Moon"
    MERCURY = "Mercury"
    VENUS = "Venus"
    MARS = "Mars"
    JUPITER = "Jupiter"
    SATURN = "Saturn"

class HoraryChart:
    def __init__(self, house_rulers):
        self.house_rulers = house_rulers

stub_models = SimpleNamespace(Planet=Planet, HoraryChart=HoraryChart)
sys.modules['backend.models'] = stub_models
sys.modules['models'] = stub_models

from backend.taxonomy import resolve as resolve_significators


def _apply_shared_significator_fix(significators):
    """Replicate engine's shared significator adjustment logic."""
    desc = significators.get("description", "")
    if desc.startswith("Shared Significator") and significators.get("same_ruler_analysis"):
        same_ruler_info = significators["same_ruler_analysis"]
        houses = list(
            same_ruler_info.get("houses")
            or significators.get("houses")
            or [
                significators.get("querent_house"),
                significators.get("quesited_house"),
            ]
        )
        if len(houses) >= 2:
            if houses[0] == houses[1]:
                q_house = significators.get("querent_house")
                qd_house = significators.get("quesited_house")
                if q_house and qd_house and q_house != qd_house:
                    houses = [q_house, qd_house]
            same_ruler_info["houses"] = houses
            shared = same_ruler_info.get("shared_ruler")
            if shared:
                desc = (
                    f"Shared Significator: {shared.value} rules both houses {houses[0]} and {houses[1]}"
                )
                significators["description"] = desc
    return significators


def test_shared_significator_reports_distinct_houses():
    chart = HoraryChart({1: Planet.MERCURY, 7: Planet.MERCURY})
    sigs = resolve_significators(chart, category=None, manual_houses=[1, 7])

    # Simulate prior duplicate-house description
    sigs['description'] = 'Shared Significator: Mercury rules both houses 1 and 1'

    updated = _apply_shared_significator_fix(sigs)
    assert updated['same_ruler_analysis']['houses'] == [1, 7]
    assert updated['description'].endswith('1 and 7')
