def calculate_walking_time(distance_meters):
    """
    Estimate walking time assuming an average
    walking speed of 1.4 meters per second.
    """

    walking_speed = 1.4

    seconds = distance_meters / walking_speed
    minutes = round(seconds / 60)

    return max(1, minutes)