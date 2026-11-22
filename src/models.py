from dataclasses import dataclass


@dataclass(frozen=True)
class Truck:
    id: str
    capacity_kg: int
    max_machines: int


TRUCKS = [
    Truck(
        id="A",
        capacity_kg=3500,
        max_machines=2
    ),
    Truck(
        id="B",
        capacity_kg=10000,
        max_machines=3
    )
]


@dataclass(frozen=True)
class Machine:
    id: str
    weight_kg: int


MACHINES = [
    Machine(id="M01", weight_kg=800),
    Machine(id="M02", weight_kg=1300),
    Machine(id="M03", weight_kg=1800),
    Machine(id="M04", weight_kg=2400),
    Machine(id="M05", weight_kg=3100),
    Machine(id="M06", weight_kg=3900),
    Machine(id="M07", weight_kg=4800),
    Machine(id="M08", weight_kg=6100),
    Machine(id="M09", weight_kg=7500),
    Machine(id="M10", weight_kg=9400),
]


@dataclass(frozen=True)
class Location:
    id: str
    x: float
    y: float


LOCATIONS = [
    Location(id="L0", x=0, y=0),
    Location(id="L1", x=3, y=8),
    Location(id="L2", x=10, y=11),
    Location(id="L3", x=17, y=9),
    Location(id="L4", x=9, y=-6),
    Location(id="L5", x=26, y=3),
    Location(id="L6", x=-7, y=13),
    Location(id="L7", x=20, y=-8),
    Location(id="L8", x=23, y=15),
    Location(id="L9", x=-8, y=-5),
]


@dataclass(frozen=True)
class TransportOrder:
    id: str
    machine_id: str
    pickup_location_id: str
    delivery_location_id: str


ORDERS = [
    TransportOrder("N01", "M01", "L1", "L3"),
    TransportOrder("N02", "M02", "L2", "L5"),
    TransportOrder("N03", "M03", "L9", "L4"),
    TransportOrder("N04", "M04", "L3", "L0"),
    TransportOrder("N05", "M05", "L0", "L8"),
    TransportOrder("N06", "M06", "L5", "L7"),
    TransportOrder("N07", "M07", "L8", "L2"),
    TransportOrder("N08", "M08", "L4", "L9"),
    TransportOrder("N09", "M09", "L6", "L1"),
    TransportOrder("N10", "M10", "L7", "L3"),
]
