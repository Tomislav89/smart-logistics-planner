from dataclasses import dataclass

from ortools.constraint_solver import pywrapcp, routing_enums_pb2

from src.models import TRUCKS, ORDERS, MACHINES, LOCATIONS
from src.distance import calculate_distance
from src.route import RouteStop, validate_truck_route


@dataclass
class OptimizationResult:
    routes: dict[str, list[RouteStop]]
    distances: dict[str, float]
    completed_orders: list[str]
    unassigned_orders: list[str]
    total_distance: float


def optimize_routes(time_limit_seconds: int = 15) -> OptimizationResult:
    # Locate the depot and prepare lookup dictionaries for transport data.
    depot = next(loc for loc in LOCATIONS if loc.id == "L0")
    machine_by_id = {machine.id: machine for machine in MACHINES}
    location_by_id = {loc.id: loc for loc in LOCATIONS}

    # Represent each transport order with separate pickup and delivery nodes.
    # Positive weights represent loading; negative weights represent unloading.
    nodes = [depot]
    node_data = [{"action": "depot", "order_id": None, "weight": 0}]

    pickup_delivery_pairs = []

    for order in ORDERS:
        machine = machine_by_id.get(order.machine_id)
        pickup = location_by_id.get(order.pickup_location_id)
        delivery = location_by_id.get(order.delivery_location_id)

        if machine is None or pickup is None or delivery is None:
            continue

        pickup_node = len(nodes)
        nodes.append(pickup)
        node_data.append({
            "action": "pickup",
            "order_id": order.id,
            "weight": machine.weight_kg,
        })

        delivery_node = len(nodes)
        nodes.append(delivery)
        node_data.append({
            "action": "delivery",
            "order_id": order.id,
            "weight": -machine.weight_kg,
        })

        pickup_delivery_pairs.append(
            (pickup_node, delivery_node, order.id)
        )

    # Initialize the OR-Tools routing model with one shared depot.
    manager = pywrapcp.RoutingIndexManager(
        len(nodes), len(TRUCKS), 0
    )
    routing = pywrapcp.RoutingModel(manager)

    # Calculate travel distance between nodes in integer units (km * 10).
    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)

        return int(round(
            calculate_distance(nodes[from_node], nodes[to_node]) * 10
        ))

    # Register the distance callback as the travel cost for all trucks.
    distance_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(distance_index)

    # Limit driving to 540 km per truck, equivalent to 9 hours at 60 km/h.
    routing.AddDimension(
        distance_index,
        0,
        5400,
        True,
        "DrivingDistance",
    )

    # Track cargo weight as machines are picked up and delivered.
    def weight_callback(from_index):
        node = manager.IndexToNode(from_index)
        return node_data[node]["weight"]

    weight_index = routing.RegisterUnaryTransitCallback(weight_callback)

    # Enforce each truck's maximum carrying weight.
    routing.AddDimensionWithVehicleCapacity(
        weight_index,
        0,
        [truck.capacity_kg for truck in TRUCKS],
        True,
        "Weight",
    )

    # Track the number of machines currently loaded on each truck.
    def machine_count_callback(from_index):
        node = manager.IndexToNode(from_index)
        action = node_data[node]["action"]

        if action == "pickup":
            return 1
        if action == "delivery":
            return -1
        return 0

    count_index = routing.RegisterUnaryTransitCallback(
        machine_count_callback
    )

    # Enforce each truck's maximum number of machines.
    routing.AddDimensionWithVehicleCapacity(
        count_index,
        0,
        [truck.max_machines for truck in TRUCKS],
        True,
        "MachineCount",
    )

    # Connect pickup and delivery nodes and enforce routing constraints.
    # Both actions must use the same truck, with pickup before delivery.
    solver = routing.solver()
    driving_dimension = routing.GetDimensionOrDie("DrivingDistance")

    for pickup_node, delivery_node, order_id in pickup_delivery_pairs:
        pickup_index = manager.NodeToIndex(pickup_node)
        delivery_index = manager.NodeToIndex(delivery_node)

        routing.AddPickupAndDelivery(pickup_index, delivery_index)

        solver.Add(
            routing.VehicleVar(pickup_index)
            == routing.VehicleVar(delivery_index)
        )

        solver.Add(
            driving_dimension.CumulVar(pickup_index)
            <= driving_dimension.CumulVar(delivery_index)
        )

        # Allow skipping an order with a high penalty.
        # Pickup and delivery must be completed or skipped together.
        routing.AddDisjunction([pickup_index], 1_000_000)
        routing.AddDisjunction([delivery_index], 1_000_000)

        solver.Add(
            routing.ActiveVar(pickup_index)
            == routing.ActiveVar(delivery_index)
        )

    # Configure route optimization.
    # Parallel Cheapest Insertion builds the initial solution.
    # Guided Local Search improves it within the configured time limit.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()

    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PARALLEL_CHEAPEST_INSERTION
    )

    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    )

    search_parameters.time_limit.FromSeconds(time_limit_seconds)

    # Execute the solver and retrieve the best solution found.
    # A time-limited search does not guarantee global optimality.
    solution = routing.SolveWithParameters(search_parameters)

    # Prepare result containers for routes, distances, and completed orders.
    routes = {}
    distances = {}
    completed_orders = set()

    # Return all orders as unassigned if no feasible solution was found.
    if solution is None:
        return OptimizationResult(
            routes={},
            distances={},
            completed_orders=[],
            unassigned_orders=[order.id for order in ORDERS],
            total_distance=0.0,
        )

    # Extract each truck's route from the OR-Tools solution.
    for vehicle_id, truck in enumerate(TRUCKS):
        index = routing.Start(vehicle_id)

        route = [RouteStop("L0", "start", None)]
        distance_units = 0

        while not routing.IsEnd(index):
            next_index = solution.Value(routing.NextVar(index))

            distance_units += routing.GetArcCostForVehicle(
                index, next_index, vehicle_id
            )

            if not routing.IsEnd(next_index):
                node = manager.IndexToNode(next_index)
                data = node_data[node]

                route.append(RouteStop(
                    location_id=nodes[node].id,
                    action=data["action"],
                    order_id=data["order_id"],
                ))

                if data["action"] == "delivery":
                    completed_orders.add(data["order_id"])

            index = next_index

        route.append(RouteStop("L0", "end", None))

        # Independently validate the route against business rules.
        if not validate_truck_route(truck, route):
            raise RuntimeError(
                f"Optimizer generated an invalid route for truck {truck.id}"
            )

        routes[truck.id] = route
        distances[truck.id] = round(distance_units / 10, 1)

    # Collect completed and unassigned orders and calculate total distance.
    completed = sorted(completed_orders)
    unassigned = [
        order.id for order in ORDERS
        if order.id not in completed_orders
    ]

    return OptimizationResult(
        routes=routes,
        distances=distances,
        completed_orders=completed,
        unassigned_orders=unassigned,
        total_distance=round(sum(distances.values()), 1),
    )
