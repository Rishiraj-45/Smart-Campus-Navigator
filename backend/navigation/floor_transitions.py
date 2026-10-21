"""
Provisional Ground Floor <-> First Floor transitions.
Stairs 9 is excluded until its Ground Floor counterpart is verified.
Vertical distances are unknown.
"""

FLOOR_TRANSITIONS = {
    ("LIFT 1", "LIFT 1 (2)"): {"type": "elevator", "distance_m": None},
    ("LIFT 2", "LIFT 2 (2)"): {"type": "elevator", "distance_m": None},
    ("LIFT 3", "LIFT 3 (2)"): {"type": "elevator", "distance_m": None},
    ("LIFT 4", "LIFT 4 (2)"): {"type": "elevator", "distance_m": None},
    ("STAIRS 1", "STAIRS 1 (2)"): {"type": "stairs", "distance_m": None},
    ("STAIRS 2", "STAIRS 2 (2)"): {"type": "stairs", "distance_m": None},
    ("STAIRS 3", "STAIRS 3 (2)"): {"type": "stairs", "distance_m": None},
    ("STAIRS 4", "STAIRS 4 (2)"): {"type": "stairs", "distance_m": None},
    ("STAIRS 5", "STAIRS 5 (2)"): {"type": "stairs", "distance_m": None},
    ("STAIRS 6", "STAIRS 6 (2)"): {"type": "stairs", "distance_m": None},
    ("STAIRS 7", "STAIRS 7 (2)"): {"type": "stairs", "distance_m": None},
    ("STAIRS 8", "STAIRS 8 (2)"): {"type": "stairs", "distance_m": None},
    ("STAIRS 10", "STAIRS 10 (2)"): {"type": "stairs", "distance_m": None},
    ("STAIRS 11", "STAIRS 11 (2)"): {"type": "stairs", "distance_m": None},
    ("STAIRS 12", "STAIRS 12 (2)"): {"type": "stairs", "distance_m": None},
    ("STAIRS 13", "STAIRS 13 (2)"): {"type": "stairs", "distance_m": None},
    ("STAIRS 14", "STAIRS 14 (2)"): {"type": "stairs", "distance_m": None},
}


def get_floor_transitions():
    """Return all configured transitions in both directions."""
    transitions = {}

    for (ground, first), metadata in FLOOR_TRANSITIONS.items():
        transitions[(ground, first)] = metadata
        transitions[(first, ground)] = metadata

    return transitions
