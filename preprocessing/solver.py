from matrix import * 
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp


def print_solution(num_vehicles, manager, routing, solution, index_to_postal):
    max_route_time = 0
    total_route_time = 0  # in seconds

    for vehicle_id in range(num_vehicles):
        if not routing.IsVehicleUsed(solution, vehicle_id):
            print(f"Vehicle {vehicle_id} was not used.\n")
            continue

        index = routing.Start(vehicle_id)
        plan_output = f"Route for vehicle {vehicle_id}:\n"
        route_time = 0

        while not routing.IsEnd(index):
            node = manager.IndexToNode(index)
            postal = index_to_postal[node] if index_to_postal else node
            plan_output += f"{postal} -> "
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_time += routing.GetArcCostForVehicle(previous_index, index, vehicle_id)

        # End node
        end_node = manager.IndexToNode(index)
        plan_output += f"{index_to_postal[end_node] if index_to_postal else end_node}\n"

        # Print time in hours + minutes
        hours = route_time // 3600
        minutes = (route_time % 3600) // 60
        plan_output += f"Total time of the route: {hours}h {minutes}m \n"
        print(plan_output)

        total_route_time += route_time
        max_route_time = max(route_time, max_route_time)

    # Final summary
    total_hours = total_route_time // 3600
    total_minutes = (total_route_time % 3600) // 60
    print(f"Total time across all vehicles: {total_hours}h {total_minutes}m")

    max_hours = max_route_time // 3600
    max_minutes = (max_route_time % 3600) // 60
    print(f"Maximum single vehicle route time: {max_hours}h {max_minutes}m")


def main(num_vehicles: int): 
    print("Step 1: Starting OR-Tools Vehicle Routing Problem Solver...")

    index_to_postal, _, postal_to_coords = generate_util_mappings()
    distance_df = generate_haversine_distance_matrix()
    data = update_k_closest_locations(distance_df, index_to_postal, postal_to_coords)
    data = data * 60  # minutes to seconds
    data = data.round().astype(int)
    print(data)

    print("Step 2: Setting up OR-Tools routing model...")
    manager = pywrapcp.RoutingIndexManager(
        len(data),
        num_vehicles, # max number of vehicles available
        0, # depot index
    ) 

    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index, to_index):
        # returns cost between two nodes where cost is time in seconds, either estimated from Haversine or from Google Maps API
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return int(data.iat[from_node, to_node])
    
    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    dimension_name = "Time"
    max_travel_time = 6 * 60 * 60 
    routing.AddDimension(
        transit_callback_index,
        0,  # IMPORTANT: for now, assume no waiting/slack time
        max_travel_time, 
        True, 
        dimension_name,
    )


    time_dimension = routing.GetDimensionOrDie(dimension_name)
    time_dimension.SetGlobalSpanCostCoefficient(100)

    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )
    print("Step 3: Solving the routing problem...")
    solution = routing.SolveWithParameters(search_parameters)
    if solution:
        print_solution(num_vehicles, manager, routing, solution, index_to_postal)
    else:
        print("No solution found !")
        return



if __name__ == "__main__":
    print("Executing OR-Tools Vehicle Routing Problem Solver...")
    main(5)