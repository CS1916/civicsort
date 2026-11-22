from typing import List, Tuple, Dict, Any, Optional
from datetime import datetime
from app.models.schemas import (
    SmartBin,
    DepotLocation,
    RoutePoint,
    RouteStats,
    RouteSavings,
    RouteBreakdown,
    OptimizeRouteResponse,
)
from app.config import settings
from app.services.osrm_service import get_distance_matrix

# Try importing OR-Tools
try:
    from ortools.constraint_solver import routing_enums_pb2
    from ortools.constraint_solver import pywrapcp
    ORTOOLS_AVAILABLE = True
except ImportError:
    ORTOOLS_AVAILABLE = False


def solve_tsp_ortools(distance_matrix: List[List[float]], depot_index: int = 0) -> List[int]:
    """
    Solves Traveling Salesperson Problem using Google OR-Tools.
    Returns the ordered list of node indices starting and ending at depot.
    """
    n = len(distance_matrix)
    if n <= 1:
        return [0]
    if n == 2:
        return [0, 1, 0]

    if not ORTOOLS_AVAILABLE:
        return solve_tsp_nearest_neighbor(distance_matrix, depot_index)

    try:
        # Create the routing index manager: n locations, 1 vehicle, depot is 0
        manager = pywrapcp.RoutingIndexManager(n, 1, depot_index)
        routing = pywrapcp.RoutingModel(manager)

        def distance_callback(from_index, to_index):
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return int(distance_matrix[from_node][to_node])

        transit_callback_index = routing.RegisterTransitCallback(distance_callback)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

        # Set search parameters
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
        )
        search_parameters.local_search_metaheuristic = (
            routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
        )
        search_parameters.time_limit.seconds = 2

        solution = routing.SolveWithParameters(search_parameters)
        if solution:
            index = routing.Start(0)
            route = []
            while not routing.IsEnd(index):
                route.append(manager.IndexToNode(index))
                index = solution.Value(routing.NextVar(index))
            route.append(manager.IndexToNode(index))
            return route
    except Exception as e:
        print(f"OR-Tools solver warning ({e}), falling back to 2-Opt heuristic.")

    return solve_tsp_nearest_neighbor(distance_matrix, depot_index)


def solve_tsp_nearest_neighbor(distance_matrix: List[List[float]], depot_index: int = 0) -> List[int]:
    """
    High-performance 2-opt TSP solver fallback when OR-Tools is not installed.
    """
    n = len(distance_matrix)
    if n <= 1:
        return [0]
    if n == 2:
        return [0, 1, 0]

    unvisited = set(range(n))
    unvisited.remove(depot_index)
    current = depot_index
    route = [current]

    while unvisited:
        next_node = min(unvisited, key=lambda node: distance_matrix[current][node])
        route.append(next_node)
        unvisited.remove(next_node)
        current = next_node

    route.append(depot_index)

    # Simple 2-opt improvement
    improved = True
    iterations = 0
    while improved and iterations < 25:
        improved = False
        iterations += 1
        for i in range(1, len(route) - 2):
            for j in range(i + 1, len(route) - 1):
                if j - i == 1:
                    continue
                a, b = route[i - 1], route[i]
                c, d = route[j], route[j + 1]
                current_cost = distance_matrix[a][b] + distance_matrix[c][d]
                new_cost = distance_matrix[a][c] + distance_matrix[b][d]
                if new_cost < current_cost:
                    route[i : j + 1] = reversed(route[i : j + 1])
                    improved = True
    return route


def calculate_route_metrics(route_order: List[int], distance_matrix: List[List[float]], bins_count: int) -> RouteStats:
    total_dist_meters = 0.0
    for i in range(len(route_order) - 1):
        from_n = route_order[i]
        to_n = route_order[i + 1]
        total_dist_meters += distance_matrix[from_n][to_n]

    total_km = round(total_dist_meters / 1000.0, 1)
    
    # Travel time + service time per bin stop
    travel_time_mins = (total_km / settings.AVERAGE_SPEED_KMH) * 60.0
    service_time_mins = bins_count * settings.SERVICE_TIME_PER_BIN_MINS
    total_time_mins = int(round(travel_time_mins + service_time_mins))

    fuel_consumed = round(total_km * settings.DIESEL_CONSUMPTION_L_PER_KM, 1)
    co2_emitted = round(fuel_consumed * settings.CO2_EMISSION_KG_PER_LITER, 1)

    return RouteStats(
        totalDistanceKm=total_km,
        estimatedTimeMins=total_time_mins,
        fuelConsumedLiters=fuel_consumed,
        co2EmittedKg=co2_emitted,
        binsVisited=bins_count,
        totalBinsAvailable=len(distance_matrix) - 1,
    )


def optimize_waste_routes(
    bins: List[SmartBin],
    depot: Optional[DepotLocation] = None,
    fill_threshold: float = 75.0,
) -> OptimizeRouteResponse:
    if depot is None:
        depot = DepotLocation()

    total_bins_count = len(bins)

    # 1. Standard Route: Visits ALL bins regardless of fill level
    all_coords = [(depot.lat, depot.lng)] + [(b.lat, b.lng) for b in bins]
    std_distance_matrix = get_distance_matrix(all_coords)
    std_node_order = solve_tsp_ortools(std_distance_matrix, 0)
    std_stats = calculate_route_metrics(std_node_order, std_distance_matrix, total_bins_count)

    std_points: List[RoutePoint] = []
    for order_idx, node in enumerate(std_node_order):
        if node == 0:
            std_points.append(
                RoutePoint(
                    lat=depot.lat,
                    lng=depot.lng,
                    name=depot.name,
                    isDepot=True,
                    order=order_idx,
                )
            )
        else:
            bin_obj = bins[node - 1]
            std_points.append(
                RoutePoint(
                    lat=bin_obj.lat,
                    lng=bin_obj.lng,
                    binId=bin_obj.id,
                    name=bin_obj.name,
                    isDepot=False,
                    order=order_idx,
                    fillLevel=bin_obj.fillLevel,
                )
            )

    # 2. AI Smart Route: Visits ONLY bins that require immediate pickup (fillLevel >= threshold)
    full_bins = [b for b in bins if b.fillLevel >= fill_threshold]
    
    # If no bins are >= threshold, pick the top 3 highest fill bins to service
    if not full_bins and bins:
        full_bins = sorted(bins, key=lambda x: x.fillLevel, reverse=True)[:3]

    ai_coords = [(depot.lat, depot.lng)] + [(b.lat, b.lng) for b in full_bins]
    ai_distance_matrix = get_distance_matrix(ai_coords)
    ai_node_order = solve_tsp_ortools(ai_distance_matrix, 0)
    ai_stats = calculate_route_metrics(ai_node_order, ai_distance_matrix, len(full_bins))

    ai_points: List[RoutePoint] = []
    for order_idx, node in enumerate(ai_node_order):
        if node == 0:
            ai_points.append(
                RoutePoint(
                    lat=depot.lat,
                    lng=depot.lng,
                    name=depot.name,
                    isDepot=True,
                    order=order_idx,
                )
            )
        else:
            bin_obj = full_bins[node - 1]
            ai_points.append(
                RoutePoint(
                    lat=bin_obj.lat,
                    lng=bin_obj.lng,
                    binId=bin_obj.id,
                    name=bin_obj.name,
                    isDepot=False,
                    order=order_idx,
                    fillLevel=bin_obj.fillLevel,
                )
            )

    # 3. Compute Savings
    dist_saved = round(max(0.0, std_stats.totalDistanceKm - ai_stats.totalDistanceKm), 1)
    dist_pct = round((dist_saved / std_stats.totalDistanceKm) * 100, 1) if std_stats.totalDistanceKm > 0 else 0.0

    time_saved = max(0, std_stats.estimatedTimeMins - ai_stats.estimatedTimeMins)
    time_pct = round((time_saved / std_stats.estimatedTimeMins) * 100, 1) if std_stats.estimatedTimeMins > 0 else 0.0

    fuel_saved = round(max(0.0, std_stats.fuelConsumedLiters - ai_stats.fuelConsumedLiters), 1)
    co2_saved = round(max(0.0, std_stats.co2EmittedKg - ai_stats.co2EmittedKg), 1)

    savings = RouteSavings(
        distanceSavedKm=dist_saved,
        distanceSavedPercent=dist_pct,
        timeSavedMins=time_saved,
        timeSavedPercent=time_pct,
        fuelSavedLiters=fuel_saved,
        co2SavedKg=co2_saved,
    )

    solver_name = "Google OR-Tools VRP" if ORTOOLS_AVAILABLE else "Dynamic 2-Opt TSP Engine"

    return OptimizeRouteResponse(
        depot=depot,
        standardRoute=RouteBreakdown(points=std_points, stats=std_stats),
        aiSmartRoute=RouteBreakdown(points=ai_points, stats=ai_stats),
        savings=savings,
        lastCalculated=f"Just now ({solver_name})",
    )
