
def generate_directions(path, locations=None, transitions=None):
    """
    Convert a navigation path into human-friendly instructions.

    Args:
        path: Ordered list of location names in the route.
        locations: Location metadata from campus_map_data.py.
        transitions: Bidirectional floor-transition mapping from
                     floor_transitions.py.

    Returns:
        A list of human-readable navigation instructions.
    """

    if not path:
        return []

    locations = locations or {}
    transitions = transitions or {}

    def get_floor_name(floor):
        """Convert a floor number into a readable name."""
        if floor == 0:
            return "Ground Floor"
        elif floor == 1:
            return "First Floor"
        elif floor is None:
            return "an unknown floor"
        else:
            return f"Floor {floor}"

    # Starting location
    start = path[0]
    start_info = locations.get(start, {})
    start_floor = start_info.get("floor")

    directions = [
        f"Start at {start} ({get_floor_name(start_floor)})."
    ]

    # Instructions for the remaining route
    for i in range(1, len(path)):
        previous = path[i - 1]
        current = path[i]

        previous_info = locations.get(previous, {})
        current_info = locations.get(current, {})

        previous_floor = previous_info.get("floor")
        current_floor = current_info.get("floor")

        # Check whether this edge is a configured floor transition.
        transition = transitions.get((previous, current))

        if transition:
            transition_type = transition.get("type", "stairs")

            if transition_type == "elevator":
                directions.append(
                    f"From {previous}, take {current} (lift) "
                    f"from {get_floor_name(previous_floor)} "
                    f"to {get_floor_name(current_floor)}."
                )
            else:
                directions.append(
                    f"From {previous}, take {current} (stairs) "
                    f"from {get_floor_name(previous_floor)} "
                    f"to {get_floor_name(current_floor)}."
                )

        # Handle a floor change if metadata identifies one,
        # even if a transition was not found in the mapping.
        elif (
            previous_floor is not None
            and current_floor is not None
            and previous_floor != current_floor
        ):
            directions.append(
                f"Move from {get_floor_name(previous_floor)} "
                f"to {get_floor_name(current_floor)} via {current}. "
                "The transition type has not been verified."
            )

        # Final destination
        elif i == len(path) - 1:
            directions.append(
                f"You have arrived at {current} "
                f"({get_floor_name(current_floor)})."
            )

        # Ordinary horizontal movement
        else:
            directions.append(f"Continue to {current}.")

    # Ensure arrival is stated if the path has multiple locations
    # and the last instruction was a transition.
    if len(path) > 1:
        last = path[-1]
        arrival_text = f"You have arrived at {last}"
        if not any(
            instruction.startswith(arrival_text)
            for instruction in directions
        ):
            directions.append(
                f"You have arrived at {last} "
                f"({get_floor_name(locations.get(last, {}).get('floor'))})."
            )

    return directions
