
import re

GROUND_FLOOR_NAMES = """
CAMPUS GATE 2
CAMPUS GATE 1
FACULTY ROOM G35
AMITY STORE G36
FACULTY ROOM G34
FACULTY ROOM G33
FACULTY ROOM G32
ADMISSION OFFICE
FACULTY ROOM G30
FACULTY ROOM G29
ENTRY GATE 1
AUDITORIUM ENTERANCE
AUDITORIUM
VIP WAITING ROOM G19
ENTRY GATE 2
ENTRY GATE 3
STAIRS 14
CONFERENCE ROOM G31
SERVER ROOM
MEDICAL ROOM G37
STAIRS 1
WASHROOM
Placement Cell G28
ENTRY GATE 8
BADMINTON COURT
G27
INFORMATION DESK
ADMIN AND SPORTS G20
ACCOUNTS G21
G22
STAIRS 7
WASHROOM
STAIRS 2
ENTRY GATE 4
BADMINTON COURT
LAB G18
LAB G17
LAB G16
COMPUTER ADMIN G1
STAIRS 13
LIFT 4
LIFT 3
STAIRS 6
G26 NCC
G25
G24
ENTRY GATE 7
Cafeteria G23
STAIRS 8
LIFT 2
LIFT 1
STAIRS 3
ENTRY GATE 5
STAIRS 10
LAB G14
LAB G15
G5
G4
OFFICE G2
OFFICE G3
STAIRS 12
GYM G6
STAIRS 5
WASHROOM
G7
G9
G8
BACKSIDE
ENTRY GATE 6
STAIRS 4
WASHROOM
MESS G12
G10
G11
STAIRS 11
MAIN HALL / ATRIUM
LAB G13
""".strip().splitlines()

FIRST_FLOOR_NAMES = """
107
106
STAIRS 14
105
104
103
FACULTY ROOM 135
136
137
MEDIA 138
166
REGISTRAR 165
STAIRS 9
108
109
110
114
FACULTY ROOM 113
FACULTY ROOM 111
102
101
STAIRS 1
WASHROOM
134
133
132
FACULTY ROOM 131
140
139
141
EXAM 163
WASHROOM
STAIRS 2
162
ADMISSION 164
LAB160
LAB 159
112
STAIRS 13
115
116
117
LIFT 4
LIFT 3
STAIRS 6
130
129
FACULTY ROOM 142
STAIRS 7
143
STAIRS 8
144
LAB 161
LIFT 2
LIFT 1
LAB 156
STAIRS 3
STAIRS 10
LAB 157
LAB 158
LAB 121
LAB 120
LAB 119
STAIRS 12
LAB 122
LAB 123
LAB 124
128
WASHROOM
STAIRS 5
126
FACULTY ROOM 127
FACULTY ROOM 125
145
146
STAIRS 4
WASHROOM
155
147
154
148
149
153
152
STAIRS 11
150
151
""".strip().splitlines()


def normalize_name(name):
    """Standardize inconsistent labels from the campus diagram."""
    name = re.sub(r"<[^>]*>", " ", name)
    name = re.sub(r"\s+", " ", name).strip()

    if name.casefold() in {"washroom", "wahroom"}:
        return "WASHROOM"

    return name


def location_type(name):
    """Infer a basic location type from its label."""
    upper = name.upper()

    if "STAIRS" in upper or "STAIRCASE" in upper:
        return "staircase"
    if "LIFT" in upper or "ELEVATOR" in upper:
        return "elevator"
    if "WASHROOM" in upper:
        return "washroom"
    if "LAB" in upper:
        return "laboratory"
    if "GATE" in upper or "ENTRANCE" in upper:
        return "entrance"
    if "CORRIDOR" in upper or "HALL" in upper or "ATRIUM" in upper:
        return "corridor"
    if "CAFETERIA" in upper or "MESS" in upper:
        return "food_service"
    if "OFFICE" in upper or "FACULTY ROOM" in upper:
        return "office"
    if "AUDITORIUM" in upper:
        return "auditorium"
    if "BADMINTON" in upper or "GYM" in upper:
        return "sports_facility"
    if "INFORMATION DESK" in upper:
        return "information_desk"
    if "ROOM" in upper:
        return "room"

    return "other"


# Normalize labels and count duplicates across both floors.
ground_names = [normalize_name(n) for n in GROUND_FLOOR_NAMES]
first_names = [normalize_name(n) for n in FIRST_FLOOR_NAMES]
all_names = ground_names + first_names

name_counts = {}
for name in all_names:
    name_counts[name] = name_counts.get(name, 0) + 1

used_names = set()
duplicate_counts = {}
LOCATIONS = {}


def add_floor_locations(names, floor):
    floor_label = "Ground Floor" if floor == 0 else "First Floor"

    for original_name in names:
        name = original_name

        # Distinguish names repeated on different floors.
        if name_counts[name] > 1:
            candidate = f"{name} ({floor_label})"
        else:
            candidate = name

        # Number duplicate names on the same floor.
        if candidate in used_names:
            key = (name, floor)
            duplicate_counts[key] = duplicate_counts.get(key, 1) + 1
            candidate = f"{name} ({duplicate_counts[key]})"

            while candidate in used_names:
                duplicate_counts[key] += 1
                candidate = f"{name} ({duplicate_counts[key]})"

        used_names.add(candidate)

        slug = re.sub(r"[^a-z0-9]+", "_", candidate.casefold()).strip("_")
        location_id = f"floor_{floor}_{slug}"

        is_staircase = location_type(name) == "staircase"
        is_elevator = location_type(name) == "elevator"

        LOCATIONS[candidate] = {
            "id": location_id,
            "name": candidate,
            "type": location_type(name),
            "building": "Academic Block",
            "floor": floor,
            "accessible": False if is_staircase else True,
        }

        if is_staircase or is_elevator:
            LOCATIONS[candidate]["connects_floors"] = [0, 1]


add_floor_locations(ground_names, 0)
add_floor_locations(first_names, 1)
