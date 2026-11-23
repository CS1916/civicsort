from .yolo_service import detect_multi_objects_image, process_waste_video
from .vrp_solver import optimize_waste_routes
from .osrm_service import get_distance_matrix, haversine_distance

# Backward-compatibility alias
analyze_waste_image = detect_multi_objects_image

__all__ = [
    "detect_multi_objects_image",
    "process_waste_video",
    "analyze_waste_image",
    "optimize_waste_routes",
    "get_distance_matrix",
    "haversine_distance",
]
