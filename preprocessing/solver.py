from matrix import * 
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import folium
import random

def visualize_routes(res, postal_to_coords, map_filename="routes_map.html"):
    sg_center = [1.3521, 103.8198]
    m = folium.Map(location=sg_center, zoom_start=12)

    def get_random_color():
        return "#{:06x}".format(random.randint(0, 0xFFFFFF))

    for i, route in enumerate(res):
        color = get_random_color()
        route_coords = []

        for postal in route:
            if postal not in postal_to_coords:
                print(f"Warning: Postal {postal} not in coords mapping.")
                continue
            lat, lon = postal_to_coords[postal]
            route_coords.append((lat, lon))
            folium.Marker(location=(lat, lon), popup=f"Vehicle {i} - {postal}", icon=folium.Icon(color="blue")).add_to(m)

        # Draw the polyline for the route
        folium.PolyLine(route_coords, color=color, weight=5, opacity=0.7, tooltip=f"Route {i}").add_to(m)

    m.save(map_filename)
    print(f"Map saved to {map_filename}")

def print_solution(num_vehicles, manager, routing, solution, index_to_postal):
    max_route_time = 0
    total_route_time = 0  
    res = []
    for vehicle_id in range(num_vehicles):
        if not routing.IsVehicleUsed(solution, vehicle_id):
            print(f"Vehicle {vehicle_id} was not used.\n")
            continue
        else: 
            route = []
        index = routing.Start(vehicle_id)
        plan_output = f"Route for vehicle {vehicle_id}:\n"
        route_time = 0

        while not routing.IsEnd(index):
            node = manager.IndexToNode(index)
            
            postal = index_to_postal[node] if index_to_postal else node
            route.append(int(postal))
            plan_output += f"{postal} -> "
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_time += routing.GetArcCostForVehicle(previous_index, index, vehicle_id)

        # End node
        end_node = manager.IndexToNode(index)

        plan_output += f"{index_to_postal[end_node] if index_to_postal else end_node}\n"
        route.append(int(index_to_postal[end_node]))
        # Print time in hours + minutes
        hours = route_time // 3600
        minutes = (route_time % 3600) // 60
        plan_output += f"Total time of the route: {hours}h {minutes}m \n"
        print(plan_output)

        total_route_time += route_time
        max_route_time = max(route_time, max_route_time)
        res.append(route)
    # Final summary
    total_hours = total_route_time // 3600
    total_minutes = (total_route_time % 3600) // 60
    print(f"Total time across all vehicles: {total_hours}h {total_minutes}m")

    max_hours = max_route_time // 3600
    max_minutes = (max_route_time % 3600) // 60
    print(f"Maximum single vehicle route time: {max_hours}h {max_minutes}m")

    return res


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
    max_travel_time = 3 * 60 * 60 
    routing.AddDimension(
        transit_callback_index,
        0,  # IMPORTANT: for now, assume no waiting/slack time
        max_travel_time, 
        True, 
        dimension_name,
    )

    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    )
    search_parameters.time_limit.FromSeconds(15) 
    print("Step 3: Solving the routing problem...")
    solution = routing.SolveWithParameters(search_parameters)
    if solution:
        res = print_solution(num_vehicles, manager, routing, solution, index_to_postal)
        visualize_routes(res, postal_to_coords)
        print("Step 4: Solution found!")
        print("Routes:", res)
    else:
        print("No solution found !")
        return



if __name__ == "__main__":
    print("Executing OR-Tools Vehicle Routing Problem Solver...")
    main(3)