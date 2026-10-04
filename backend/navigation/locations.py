LOCATIONS = {

    "Main Gate": {
        "id": "main_gate",
        "name": "Main Gate",
        "type": "entrance",
        "building": "Campus",
        "floor": 0,
        "accessible": True
    },

    "Academic Block Entrance": {
        "id": "academic_entrance",
        "name": "Academic Block Entrance",
        "type": "entrance",
        "building": "Academic Block",
        "floor": 0,
        "accessible": True
    },

    "Ground Floor Corridor": {
        "id": "ground_corridor",
        "name": "Ground Floor Corridor",
        "type": "corridor",
        "building": "Academic Block",
        "floor": 0,
        "accessible": True
    },

    "Room 101": {
        "id": "room_101",
        "name": "Room 101",
        "type": "classroom",
        "building": "Academic Block",
        "floor": 0,
        "accessible": True
    },

    "Staircase A": {
        "id": "staircase_a",
        "name": "Staircase A",
        "type": "staircase",
        "building": "Academic Block",
        "floor": 0,
        "connects_floors": [0, 1],
        "accessible": False
    },

    "First Floor Corridor": {
        "id": "first_corridor",
        "name": "First Floor Corridor",
        "type": "corridor",
        "building": "Academic Block",
        "floor": 1,
        "accessible": True
    },

    "CSE Lab": {
        "id": "cse_lab",
        "name": "CSE Lab",
        "type": "laboratory",
        "building": "Academic Block",
        "floor": 1,
        "accessible": True
    },

    "Room 204": {
        "id": "room_204",
        "name": "Room 204",
        "type": "classroom",
        "building": "Academic Block",
        "floor": 1,
        "accessible": True
    },

    "Cafeteria": {
        "id": "cafeteria",
        "name": "Cafeteria",
        "type": "cafeteria",
        "building": "Campus",
        "floor": 0,
        "accessible": True
    },

        "Elevator A": {
        "id": "elevator_a",
        "name": "Elevator A",
        "type": "elevator",
        "building": "Academic Block",
        "floor": 0,
        "connects_floors": [0, 1],
        "accessible": True
    }
}