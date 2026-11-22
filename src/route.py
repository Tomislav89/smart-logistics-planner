from dataclasses import dataclass
from src.time_utils import calculate_route_time, is_driving_time_valid

from src.lookup import get_location_by_id
from src.distance import calculate_route_distance


from src.models import Truck, Machine
from src.lookup import get_order_by_id
from src.constraints import try_load_order, try_unload_order



@dataclass(frozen=True)
class RouteStop:
    location_id: str
    action: str
    order_id: str | None


def execute_route_stop(
    truck: Truck,
    current_load: list[Machine],
    stop: RouteStop
) -> list[Machine] | None:
    """
    Execute a pickup or delivery at a route stop.
    Return the updated load, or None if the action is invalid.
    """
    if stop.action not in ("pickup", "delivery"):
        return None

    if stop.order_id is None:
        return None

    order = get_order_by_id(stop.order_id)

    if order is None:
        return None

    if stop.action == "pickup":
        if stop.location_id != order.pickup_location_id:
            return None

        return try_load_order(truck, current_load, order)

    if stop.location_id != order.delivery_location_id:
        return None

    return try_unload_order(current_load, order)


def execute_route(
    truck: Truck,
    route: list[RouteStop]
) -> list[Machine] | None:
    """
    Execute all stops in a route.
    Return the final load, or None if any action fails.
    """
    current_load = []

    for stop in route:
        if stop.action in ("start", "end"):
            continue

        updated_load = execute_route_stop(truck, current_load, stop)

        if updated_load is None:
            print(f"Invalid action at {stop.location_id}: {stop.action}")
            return None

        current_load = updated_load
        print(f"{stop.location_id} - {stop.action}: {current_load}")

    return current_load


def calculate_truck_route_distance(
    route: list[RouteStop]
) -> float | None:
    """
    Calculate total distance for all stops in a truck route.
    Return None if any location does not exist.
    """
    locations = []

    for stop in route:
        location = get_location_by_id(stop.location_id)

        if location is None:
            return None

        locations.append(location)

    return calculate_route_distance(locations)


def calculate_truck_route_time(
    route: list[RouteStop]
) -> dict | None:
    """
    Calculate driving, service and total time for a truck route.
    """
    distance = calculate_truck_route_distance(route)

    if distance is None:
        return None

    number_of_actions = sum(
        1 for stop in route
        if stop.action in ("pickup", "delivery")
    )

    return calculate_route_time(distance, number_of_actions)


def is_truck_route_time_valid(
    route: list[RouteStop]
) -> bool:
    """
    Check whether a truck route respects the driving time limit.
    """
    distance = calculate_truck_route_distance(route)

    if distance is None:
        return False

    return is_driving_time_valid(distance)


def is_route_depot_valid(route: list[RouteStop]) -> bool:
    """
    Check whether a route starts and ends at depot L0.
    """
    if len(route) < 2:
        return False

    first_stop = route[0]
    last_stop = route[-1]

    if first_stop.location_id != "L0" or first_stop.action != "start":
        return False

    if last_stop.location_id != "L0" or last_stop.action != "end":
        return False

    return True


def is_pickup_delivery_order_valid(route: list[RouteStop]) -> bool:
    """
    Check that every delivery happens after its pickup
    and that orders are not picked up or delivered twice.
    """
    picked_up_orders = set()
    delivered_orders = set()

    for stop in route:
        if stop.action == "pickup":
            if stop.order_id is None:
                return False

            if stop.order_id in picked_up_orders:
                return False

            picked_up_orders.add(stop.order_id)

        elif stop.action == "delivery":
            if stop.order_id is None:
                return False

            if stop.order_id not in picked_up_orders:
                return False

            if stop.order_id in delivered_orders:
                return False

            delivered_orders.add(stop.order_id)

    return picked_up_orders == delivered_orders


def validate_truck_route(
    truck: Truck,
    route: list[RouteStop]
) -> bool:
    """
    Validate depot, pickup/delivery order, capacity,
    locations and driving time.
    """
    if not is_route_depot_valid(route):
        return False

    if not is_pickup_delivery_order_valid(route):
        return False

    if not is_truck_route_time_valid(route):
        return False

    if any(
        stop.action not in ("start", "pickup", "delivery", "end")
        for stop in route
    ):
        return False

    if any(
        stop.action in ("start", "end")
        for stop in route[1:-1]
    ):
        return False

    current_load = []

    for stop in route[1:-1]:
        updated_load = execute_route_stop(truck, current_load, stop)

        if updated_load is None:
            return False

        current_load = updated_load

    return len(current_load) == 0
