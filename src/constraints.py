from src.models import Truck, Machine, TransportOrder
from src.lookup import get_machine_by_id


def can_truck_carry_machine(truck: Truck, machine: Machine) -> bool:
    """
    Check whether a truck can carry a single machine
    based on its weight capacity.
    """
    return machine.weight_kg <= truck.capacity_kg


def can_truck_carry_load(truck: Truck, machines: list[Machine]) -> bool:
    """
    Check whether the combined load respects both
    the truck's weight and machine count limits.
    """
    total_weight = sum(machine.weight_kg for machine in machines)
    machine_count = len(machines)

    return (
        total_weight <= truck.capacity_kg
        and machine_count <= truck.max_machines
    )


def can_truck_handle_order(truck: Truck, order: TransportOrder) -> bool:
    """
    Check whether a truck can carry the machine
    required by a transport order.
    """
    machine = get_machine_by_id(order.machine_id)

    if machine is None:
        return False

    return can_truck_carry_machine(truck, machine)


def try_load_machine(
    truck: Truck,
    current_load: list[Machine],
    new_machine: Machine
) -> list[Machine] | None:
    """
    Try adding a machine to the current truck load.

    Return the updated load if valid, otherwise None.
    """
    updated_load = current_load + [new_machine]

    if not can_truck_carry_load(truck, updated_load):
        return None

    return updated_load


def try_unload_machine(
    current_load: list[Machine],
    machine_to_unload: Machine
) -> list[Machine] | None:
    """
    Try removing a machine from the current truck load.

    Return the updated load if the machine exists,
    otherwise None.
    """
    if machine_to_unload not in current_load:
        return None

    updated_load = [
        machine for machine in current_load
        if machine.id != machine_to_unload.id
    ]

    return updated_load


def try_load_order(
    truck: Truck,
    current_load: list[Machine],
    order: TransportOrder
) -> list[Machine] | None:
    """
    Try loading the machine associated with a transport order.
    """
    machine = get_machine_by_id(order.machine_id)

    if machine is None:
        return None

    return try_load_machine(truck, current_load, machine)


def try_unload_order(
    current_load: list[Machine],
    order: TransportOrder
) -> list[Machine] | None:
    """
    Try unloading the machine associated with a transport order.
    """
    machine = get_machine_by_id(order.machine_id)

    if machine is None:
        return None

    return try_unload_machine(current_load, machine)
