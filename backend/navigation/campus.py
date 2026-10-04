CAMPUS_GRAPH = {

    "Main Gate": [
        ("Academic Block Entrance", 50),
        ("Cafeteria", 120)
    ],

    "Academic Block Entrance": [
        ("Main Gate", 50),
        ("Ground Floor Corridor", 30)
    ],

    "Ground Floor Corridor": [
        ("Academic Block Entrance", 30),
        ("Staircase A", 20),
        ("Elevator A", 25),
        ("Room 101", 15)
    ],

    "Room 101": [
        ("Ground Floor Corridor", 15)
    ],

    "Staircase A": [
        ("Ground Floor Corridor", 20),
        ("First Floor Corridor", 15)
    ],

    "First Floor Corridor": [
        ("Staircase A", 15),
        ("Elevator A", 20),
        ("CSE Lab", 25),
        ("Room 204", 20)
    ],

    "Elevator A": [
        ("Ground Floor Corridor", 25),
        ("First Floor Corridor", 20)
    ],

    "CSE Lab": [
        ("First Floor Corridor", 25)
    ],

    "Room 204": [
        ("First Floor Corridor", 20)
    ],

    "Cafeteria": [
        ("Main Gate", 120)
    ]
}