AVERAGE_SPEED_KMH = 60
MAX_DRIVING_HOURS = 9
SERVICE_TIME_MINUTES = 20


def calculate_driving_time(distance_km: float) -> float:
    """
    Calculate driving time in hours based on distance.
    """
    return distance_km / AVERAGE_SPEED_KMH


def calculate_service_time(number_of_actions: int) -> float:
    """
    Calculate total loading and unloading time in hours.

    Each loading or unloading action takes 20 minutes.
    """
    total_minutes = number_of_actions * SERVICE_TIME_MINUTES

    return total_minutes / 60


def calculate_route_time(
    distance_km: float,
    number_of_actions: int
) -> dict:
    """
    Calculate driving, service and total route time in hours.
    """
    driving_hours = calculate_driving_time(distance_km)
    service_hours = calculate_service_time(number_of_actions)

    total_hours = driving_hours + service_hours

    return {
        "driving_hours": driving_hours,
        "service_hours": service_hours,
        "total_hours": total_hours
    }


def is_driving_time_valid(distance_km: float) -> bool:
    """
    Check whether driving time is within the daily limit.
    """
    driving_hours = calculate_driving_time(distance_km)

    return driving_hours <= MAX_DRIVING_HOURS
