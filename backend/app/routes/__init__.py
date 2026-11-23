from .classify import router as classify_router
from .route_optimizer import router as route_optimizer_router
from .bins import router as bins_router
from .settings_router import router as settings_router
from .auth_router import router as auth_router
from .fleet_router import router as fleet_router
from .collections_router import router as collections_router
from .notifications_router import router as notifications_router

__all__ = [
    "classify_router",
    "route_optimizer_router",
    "bins_router",
    "settings_router",
    "auth_router",
    "fleet_router",
    "collections_router",
    "notifications_router",
]
