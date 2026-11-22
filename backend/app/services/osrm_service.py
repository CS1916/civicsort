import math
import requests
from typing import List, Tuple
from app.config import settings

def haversine_distance(coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
    """
    Calculates great-circle distance (in meters) between two points on Earth using Haversine formula.
    coord: (latitude, longitude)
    """
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    R = 6371000  # Earth radius in meters

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    # Apply city road detour index (typically 1.35x crow-fly distance in urban street grids)
    return R * c * 1.35

def get_distance_matrix(coordinates: List[Tuple[float, float]]) -> List[List[float]]:
    """
    Fetches real street network distance matrix (in meters) via OSRM API.
    coordinates: List of (lat, lng) tuples.
    Falls back gracefully to urban-adjusted Haversine distance matrix if offline.
    """
    n = len(coordinates)
    if n <= 1:
        return [[0.0]]

    # Attempt OSRM API call if coordinate count is within reasonable free OSRM limits
    if n <= 30:
        try:
            # OSRM expects coordinates formatted as lon,lat;lon,lat
            coord_str = ";".join([f"{lng:.6f},{lat:.6f}" for lat, lng in coordinates])
            url = f"{settings.OSRM_BASE_URL}/table/v1/driving/{coord_str}?annotations=distance"
            
            response = requests.get(url, timeout=3.5)
            if response.status_code == 200:
                data = response.json()
                if data.get("code") == "Ok" and "distances" in data:
                    return data["distances"]
        except Exception:
            # Fallback to local mathematical model
            pass

    # High-fidelity Haversine distance matrix fallback
    matrix = []
    for i in range(n):
        row = []
        for j in range(n):
            if i == j:
                row.append(0.0)
            else:
                dist = haversine_distance(coordinates[i], coordinates[j])
                row.append(dist)
        matrix.append(row)

    return matrix
