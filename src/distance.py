import math

from src.models import Location


def calculate_distance(
    start: Location,
    end: Location
) -> float:
    """
    Calculate Euclidean distance between two locations.

    Distance is rounded to one decimal place.
    """
    distance = math.sqrt(
        (end.x - start.x) ** 2 +
        (end.y - start.y) ** 2
    )

    return round(distance, 1)


def calculate_route_distance(route: list[Location]) -> float:
    """
    Calculate total distance of a route.

    Each individual segment is rounded to one decimal place.
    """
    total_distance = 0.0

    for i in range(len(route) - 1):
        start = route[i]
        end = route[i + 1]

        segment_distance = calculate_distance(start, end)
        total_distance += segment_distance

    return round(total_distance, 1)
