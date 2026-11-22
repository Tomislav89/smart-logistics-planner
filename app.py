import pandas as pd
import streamlit as st

from src.models import TRUCKS, ORDERS
from src.lookup import get_order_by_id, get_machine_by_id
from src.optimizer import optimize_routes
from src.route import calculate_truck_route_time

st.set_page_config(
    page_title="Smart Logistics Planner",
    page_icon="🚚",
    layout="wide",
)

st.title("🚚 Smart Logistics Planner")
st.write("Truck route optimization using Google OR-Tools")

with st.sidebar:
    st.header("Optimization Settings")
    time_limit = st.slider(
        "Optimization time (seconds)",
        min_value=5,
        max_value=60,
        value=15,
        step=5,
    )

    optimize_button = st.button(
        "Optimize Routes",
        type="primary",
        use_container_width=True,
    )

st.subheader("Fleet")

fleet_data = [
    {
        "Truck": truck.id,
        "Capacity (kg)": truck.capacity_kg,
        "Max machines": truck.max_machines,
    }
    for truck in TRUCKS
]

st.dataframe(pd.DataFrame(fleet_data), use_container_width=True, hide_index=True)

st.subheader("Transport Orders")

order_data = []

for order in ORDERS:
    machine = get_machine_by_id(order.machine_id)

    order_data.append({
        "Order": order.id,
        "Machine": order.machine_id,
        "Weight (kg)": machine.weight_kg if machine else None,
        "Pickup": order.pickup_location_id,
        "Delivery": order.delivery_location_id,
    })

st.dataframe(pd.DataFrame(order_data), use_container_width=True, hide_index=True)

if optimize_button:
    with st.spinner("Optimizing routes..."):
        result = optimize_routes(time_limit)

    st.session_state["optimization_result"] = result

if "optimization_result" in st.session_state:
    result = st.session_state["optimization_result"]

    st.divider()
    st.header("Optimization Results")

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Distance", f"{result.total_distance:.1f} km")
    col2.metric("Completed Orders", len(result.completed_orders))
    col3.metric("Unassigned Orders", len(result.unassigned_orders))

    if result.unassigned_orders:
        st.warning(
            "Unassigned orders: " + ", ".join(result.unassigned_orders)
        )
    else:
        st.success("All transport orders successfully assigned.")

    for truck in TRUCKS:
        route = result.routes.get(truck.id, [])

        if not route:
            continue

        st.subheader(f"Truck {truck.id}")

        completed_count = sum(
            1 for stop in route if stop.action == "delivery"
        )
        st.write(f"Completed orders: **{completed_count}**")

        route_time = calculate_truck_route_time(route)

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Distance",
            f"{result.distances[truck.id]:.1f} km",
        )

        if route_time:
            c2.metric(
                "Driving Time",
                f"{route_time['driving_hours']:.2f} h",
            )
            c3.metric(
                "Total Time",
                f"{route_time['total_hours']:.2f} h",
            )

        current_load = {}
        route_rows = []

        for position, stop in enumerate(route, start=1):
            if stop.order_id:
                order = get_order_by_id(stop.order_id)

                if order:
                    machine = get_machine_by_id(order.machine_id)

                    if machine:
                        if stop.action == "pickup":
                            current_load[machine.id] = machine.weight_kg
                        elif stop.action == "delivery":
                            current_load.pop(machine.id, None)

            route_rows.append({
                "Stop": position,
                "Location": stop.location_id,
                "Action": stop.action,
                "Order": stop.order_id or "-",
                "Current Load": ", ".join(current_load) or "Empty",
                "Load (kg)": sum(current_load.values()),
            })

        st.dataframe(
            pd.DataFrame(route_rows),
            use_container_width=True,
            hide_index=True,
        )

        route_description = " → ".join(
            stop.location_id for stop in route
        )

        st.caption(f"Route: {route_description}")

    st.divider()
    st.subheader("Completed Orders")

    st.write(", ".join(result.completed_orders) or "None")
