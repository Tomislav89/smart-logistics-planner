from src.models import TRUCKS, ORDERS
from src.optimizer import optimize_routes
from src.route import (
    validate_truck_route,
    calculate_truck_route_distance,
    calculate_truck_route_time,
)


def test_optimizer_returns_valid_routes():
    result = optimize_routes(5)

    assert result.routes

    for truck in TRUCKS:
        assert truck.id in result.routes
        assert validate_truck_route(
            truck,
            result.routes[truck.id],
        )


def test_all_orders_are_accounted_for():
    result = optimize_routes(5)

    completed = set(result.completed_orders)
    unassigned = set(result.unassigned_orders)
    expected = {order.id for order in ORDERS}

    assert completed.isdisjoint(unassigned)
    assert completed | unassigned == expected


def test_orders_are_not_duplicated():
    result = optimize_routes(5)

    pickups = []
    deliveries = []

    for route in result.routes.values():
        for stop in route:
            if stop.action == "pickup":
                pickups.append(stop.order_id)
            elif stop.action == "delivery":
                deliveries.append(stop.order_id)

    assert len(pickups) == len(set(pickups))
    assert len(deliveries) == len(set(deliveries))
    assert sorted(pickups) == sorted(deliveries)
    assert sorted(deliveries) == sorted(result.completed_orders)


def test_driving_limit():
    result = optimize_routes(5)

    for route in result.routes.values():
        route_time = calculate_truck_route_time(route)

        assert route_time is not None
        assert route_time["driving_hours"] <= 9


def test_total_distance():
    result = optimize_routes(5)

    calculated_total = 0

    for truck_id, route in result.routes.items():
        distance = calculate_truck_route_distance(route)

        assert distance is not None
        assert abs(distance - result.distances[truck_id]) < 0.01

        calculated_total += distance

    assert abs(calculated_total - result.total_distance) < 0.01
