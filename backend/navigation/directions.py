from backend.navigation.locations import LOCATIONS


def generate_directions(path):
    """
    Convert a navigation path into human-friendly instructions.
    """

    directions = []

    if not path:
        return directions

    start = path[0]
    start_info = LOCATIONS.get(start, {})

    start_floor = start_info.get("floor")

    if start_floor == 0:
        floor_name = "Ground Floor"
    elif start_floor == 1:
        floor_name = "First Floor"
    else:
        floor_name = f"Floor {start_floor}"

    directions.append(
        f"Start at {start} ({floor_name})."
    )

    for i in range(1, len(path)):

        previous = path[i - 1]
        current = path[i]

        current_info = LOCATIONS.get(current, {})

        current_type = current_info.get("type")

        # Staircase
        if current_type == "staircase":

            connects = current_info.get(
                "connects_floors",
                []
            )

            if len(connects) >= 2:

                directions.append(
                    f"Take {current} from Floor "
                    f"{connects[0]} to Floor {connects[1]}."
                )

            else:

                directions.append(
                    f"Take {current}."
                )

        # Destination
        elif i == len(path) - 1:

            directions.append(
                f"You have arrived at {current}."
            )

        # Normal movement
        else:

            directions.append(
                f"Continue to {current}."
            )

    return directions