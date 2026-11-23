from src.models import TRUCKS
from src.route import RouteStop, validate_truck_route


def make_route(*stops):
    return [
        RouteStop("L0", "start", None),
        *stops,
        RouteStop("L0", "end", None),
    ]


# TEST: Verify that a truck cannot carry a load exceeding its maximum weight capacity.
def test_truck_cannot_exceed_weight_capacity():
    route = make_route(
        RouteStop("L1", "pickup", "N01"),
        RouteStop("L2", "pickup", "N02"),
        RouteStop("L3", "pickup", "N04"),
        RouteStop("L3", "delivery", "N01"),
        RouteStop("L5", "delivery", "N02"),
        RouteStop("L0", "delivery", "N04"),
    )

    assert not validate_truck_route(TRUCKS[0], route)


# TEST: Verify that a truck cannot carry more machines simultaneously than allowed.
def test_truck_cannot_exceed_machine_count():
    from src.constraints import can_truck_carry_load
    from src.models import Machine, Truck

    truck = Truck(id="TEST", capacity_kg=10000, max_machines=2)
    machines = [
        Machine("T01", 500),
        Machine("T02", 500),
        Machine("T03", 500),
    ]

    assert sum(machine.weight_kg for machine in machines) < truck.capacity_kg
    assert not can_truck_carry_load(truck, machines)


# TEST: Verify that a delivery is rejected if the machine has not been picked up first.
def test_delivery_before_pickup_is_rejected():
    route = make_route(
        RouteStop("L3", "delivery", "N01"),
        RouteStop("L1", "pickup", "N01"),
    )

    assert not validate_truck_route(TRUCKS[0], route)


# TEST: Verify that a route is rejected if the truck does not return to depot L0.
def test_missing_return_to_depot_is_rejected():
    route = [
        RouteStop("L0", "start", None),
        RouteStop("L1", "pickup", "N01"),
        RouteStop("L3", "delivery", "N01"),
    ]

    assert not validate_truck_route(TRUCKS[0], route)


# TEST: Verify that a valid route satisfying all business constraints is accepted.
def test_correct_route_is_accepted():
    route = make_route(
        RouteStop("L1", "pickup", "N01"),
        RouteStop("L3", "delivery", "N01"),
    )

    assert validate_truck_route(TRUCKS[0], route)
