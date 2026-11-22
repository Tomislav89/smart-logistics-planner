# Smart Logistics Planner

Python application for transport route optimization, developed as a technical assignment.

The application uses Google OR-Tools to assign transport orders to trucks and optimize routes while respecting vehicle capacities and pickup/delivery constraints.

## Technologies

- Python 3.10+
- Google OR-Tools
- Streamlit
- Pandas
- Pytest

## Features

- Two trucks with different capacities
- Ten transport orders
- Automatic route optimization
- Pickup and delivery constraints
- Weight and machine-count capacity validation
- Maximum 9 hours of driving per truck
- Average driving speed of 60 km/h
- Loading/unloading time of 20 minutes per action
- Current truck load after each stop
- Completed and unassigned orders
- Interactive Streamlit interface
- Automated tests

## Project Structure

- app.py - Streamlit application
- src/models.py - Trucks, machines, locations and orders
- src/distance.py - Distance calculations
- src/time_utils.py - Driving and service time calculations
- src/lookup.py - Data lookup functions
- src/constraints.py - Capacity validation
- src/route.py - Route execution and validation
- src/optimizer.py - OR-Tools optimization
- tests/test_optimizer.py - Automated optimizer tests
- requirements.txt - Python dependencies

## Installation

Create a virtual environment:

    python3 -m venv .venv
    source .venv/bin/activate

Install dependencies:

    python -m pip install -r requirements.txt

## Running the Application

    streamlit run app.py

Open http://localhost:8501 and click "Optimize Routes".

## Running Tests

    python -m pytest tests/ -v

## Optimization Approach

The application models transport orders as pickup and delivery nodes.

Google OR-Tools minimizes the total driving distance subject to:

- Pickup and delivery performed by the same truck
- Pickup before delivery
- Maximum simultaneous weight capacity
- Maximum simultaneous machine count
- Maximum driving distance of 540 km per truck

A truck may remain unused if the optimizer finds a shorter solution using fewer vehicles.

The solver returns the best solution found within the configured time limit. Global optimality is not guaranteed.

## Time Calculation

- Average speed: 60 km/h
- Maximum driving time: 9 hours per truck
- Pickup service time: 20 minutes
- Delivery service time: 20 minutes

The 9-hour limit applies to driving time only. Total elapsed time, including service operations, is displayed separately.

## Unassigned Orders

Orders that cannot be included in a feasible solution are reported as unassigned.

High penalties encourage the optimizer to complete as many transport orders as possible.

## AI Assistance Disclosure

ChatGPT was used for code generation, implementation guidance, debugging, automated test creation and documentation.

The application was executed and tested locally, with generated routes validated against the implemented constraints.

## Development Time

Estimated active development time: approximately 7 hours.

This includes requirements analysis, project setup, optimization algorithm implementation, Streamlit interface development, business constraint testing, debugging, and documentation.

AI assistance was used to accelerate implementation, while the application was executed and tested locally.
