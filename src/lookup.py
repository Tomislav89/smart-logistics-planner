from src.models import Machine, MACHINES, Location, LOCATIONS, TransportOrder, ORDERS


def get_machine_by_id(machine_id: str) -> Machine | None:
    """
    Find a machine by its ID.

    Return None if the machine does not exist.
    """
    for machine in MACHINES:
        if machine.id == machine_id:
            return machine

    return None


def get_location_by_id(location_id: str) -> Location | None:
    """
    Find a location by its ID.
    Return None if the location does not exist.
    """
    for location in LOCATIONS:
        if location.id == location_id:
            return location

    return None


def get_order_locations(
    order: TransportOrder
) -> tuple[Location, Location] | None:
    """
    Return pickup and delivery locations for a transport order.
    Return None if either location does not exist.
    """
    pickup = get_location_by_id(order.pickup_location_id)
    delivery = get_location_by_id(order.delivery_location_id)

    if pickup is None or delivery is None:
        return None

    return pickup, delivery


def get_order_by_id(order_id: str) -> TransportOrder | None:
    """
    Find a transport order by its ID.
    Return None if the order does not exist.
    """
    for order in ORDERS:
        if order.id == order_id:
            return order

    return None
