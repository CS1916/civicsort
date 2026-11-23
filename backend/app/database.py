import os
import sqlite3
import hashlib
import json
import random
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ecoroute.db")


def get_db_connection() -> sqlite3.Connection:
    """Returns a SQLite connection with row_factory configured for dictionary-like access."""
    conn = sqlite3.connect(DB_PATH, timeout=15.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def hash_password(password: str) -> str:
    """SHA-256 password hash with salt."""
    salt = "ecoroute_salt_2026"
    return hashlib.sha256((password + salt).encode("utf-8")).hexdigest()


def init_db():
    """Initializes tables and seeds production-grade initial data for Bengaluru."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Users table (Admin & Operator RBAC)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        full_name TEXT NOT NULL,
        role TEXT NOT NULL, -- 'admin' or 'operator'
        avatar_initials TEXT NOT NULL,
        phone TEXT,
        created_at TEXT NOT NULL
    );
    """)

    # 2. Smart Bins table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bins (
        id TEXT PRIMARY KEY,
        code TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        zone TEXT NOT NULL,
        address TEXT NOT NULL,
        lat REAL NOT NULL,
        lng REAL NOT NULL,
        fill_level REAL NOT NULL,
        category TEXT NOT NULL, -- 'recyclable', 'organic', 'hazardous', 'general'
        capacity_kg REAL NOT NULL DEFAULT 100.0,
        battery_level INTEGER NOT NULL DEFAULT 90,
        priority TEXT NOT NULL DEFAULT 'Normal', -- 'Critical', 'High', 'Normal'
        last_updated TEXT NOT NULL,
        needs_pickup INTEGER NOT NULL DEFAULT 0 -- 1 for True, 0 for False
    );
    """)

    # 3. Fleet Vehicles table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS vehicles (
        id TEXT PRIMARY KEY,
        code TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        model TEXT NOT NULL,
        plate_number TEXT NOT NULL,
        status TEXT NOT NULL, -- 'En Route', 'Available', 'Maintenance', 'Charging'
        driver_id TEXT,
        fuel_battery_pct INTEGER NOT NULL,
        capacity_tons REAL NOT NULL,
        current_lat REAL NOT NULL,
        current_lng REAL NOT NULL,
        assigned_zone TEXT,
        last_maintenance TEXT
    );
    """)

    # 4. Drivers table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS drivers (
        id TEXT PRIMARY KEY,
        employee_code TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        phone TEXT NOT NULL,
        license_no TEXT NOT NULL,
        status TEXT NOT NULL, -- 'On Duty', 'Off Duty', 'On Break'
        rating REAL NOT NULL DEFAULT 4.9,
        assigned_vehicle_id TEXT,
        shifts_completed INTEGER NOT NULL DEFAULT 142
    );
    """)

    # 5. Collection Logs table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS collection_logs (
        id TEXT PRIMARY KEY,
        run_id TEXT UNIQUE NOT NULL,
        timestamp TEXT NOT NULL,
        vehicle_code TEXT NOT NULL,
        driver_name TEXT NOT NULL,
        bins_serviced_count INTEGER NOT NULL,
        total_weight_tons REAL NOT NULL,
        distance_km REAL NOT NULL,
        fuel_saved_liters REAL NOT NULL,
        co2_avoided_kg REAL NOT NULL,
        status TEXT NOT NULL -- 'Completed', 'In Progress'
    );
    """)

    # 6. Notifications table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS notifications (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        message TEXT NOT NULL,
        level TEXT NOT NULL, -- 'critical', 'warning', 'info', 'success'
        timestamp TEXT NOT NULL,
        is_read INTEGER NOT NULL DEFAULT 0,
        bin_id TEXT,
        vehicle_id TEXT
    );
    """)

    conn.commit()

    # --- SEED INITIAL DATA IF EMPTY ---
    # Check users
    cursor.execute("SELECT COUNT(*) FROM users;")
    if cursor.fetchone()[0] == 0:
        seed_users = [
            ("usr-admin-01", "admin@ecoroute.city", hash_password("admin123"), "Chethan (CS)", "admin", "CS", "+91 98450 11223", datetime.utcnow().isoformat()),
            ("usr-oper-02", "operator@ecoroute.city", hash_password("operator123"), "Ramesh Kumar", "operator", "RK", "+91 98450 44556", datetime.utcnow().isoformat()),
        ]
        cursor.executemany("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?);", seed_users)

    # Check bins
    cursor.execute("SELECT COUNT(*) FROM bins;")
    if cursor.fetchone()[0] == 0:
        seed_bins = [
            ("bin-101", "BIN-101", "Indiranagar Metro Gate 1", "Indiranagar Core", "100 Feet Rd & CMH Rd", 12.9784, 77.6408, 88.0, "recyclable", 120.0, 94, "Critical", "4 mins ago", 1),
            ("bin-102", "BIN-102", "Cubbon Park Bamboo Grove", "Central Green Belt", "Kasturba Road Promenade", 12.9763, 77.5929, 25.0, "organic", 80.0, 88, "Normal", "12 mins ago", 0),
            ("bin-103", "BIN-103", "Koramangala 5th Block Plaza", "Koramangala Commercial", "Jyoti Nivas College Rd", 12.9345, 77.6190, 94.0, "organic", 150.0, 79, "Critical", "2 mins ago", 1),
            ("bin-104", "BIN-104", "Manyata Tech Park Gate 4", "North IT Corridor", "Outer Ring Road, Hebbal", 13.0489, 77.6200, 45.0, "recyclable", 120.0, 92, "Normal", "18 mins ago", 0),
            ("bin-105", "BIN-105", "Victoria Hospital Trauma Wing", "Medical Sector", "Fort Rd, Kalasipalya", 12.9628, 77.5752, 82.0, "hazardous", 100.0, 85, "Critical", "7 mins ago", 1),
            ("bin-106", "BIN-106", "IISc Main Campus Library", "Education Corridor", "CV Raman Ave, Malleshwaram", 13.0219, 77.5671, 18.0, "recyclable", 100.0, 96, "Normal", "25 mins ago", 0),
            ("bin-107", "BIN-107", "Commercial Street Arcade", "Central Retail", "Commercial St, Tasker Town", 12.9822, 77.6083, 96.0, "recyclable", 160.0, 73, "Critical", "1 min ago", 1),
            ("bin-108", "BIN-108", "Jayanagar 4th Block Complex", "South Residential", "11th Main Rd, 4th Block", 12.9299, 77.5824, 62.0, "general", 110.0, 81, "Normal", "15 mins ago", 0),
            ("bin-109", "BIN-109", "Lalbagh Botanical Lake Gate", "Lalbagh Green Zone", "Double Road Gate Promenade", 12.9507, 77.5848, 79.0, "organic", 140.0, 68, "Critical", "8 mins ago", 1),
            ("bin-110", "BIN-110", "KSR Bengaluru Majestic Terminal", "Transit Core", "Majestic Railway Station Plaza", 12.9781, 77.5696, 85.0, "recyclable", 150.0, 89, "Critical", "6 mins ago", 1),
            ("bin-111", "BIN-111", "Electronic City Phase 1 Gate", "Tech Corridor South", "Hosur Rd, Electronic City", 12.8452, 77.6602, 32.0, "recyclable", 90.0, 95, "Normal", "30 mins ago", 0),
            ("bin-112", "BIN-112", "Whitefield ITPL Main Plaza", "East IT Cluster", "ITPB Main Rd, Whitefield", 12.9863, 77.7315, 38.0, "organic", 85.0, 90, "Normal", "22 mins ago", 0),
        ]
        cursor.executemany("INSERT INTO bins VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", seed_bins)

    # Check drivers
    cursor.execute("SELECT COUNT(*) FROM drivers;")
    if cursor.fetchone()[0] == 0:
        seed_drivers = [
            ("drv-01", "DRV-101", "Suresh Gowda", "+91 98451 22334", "KA-01-2019-004812", "On Duty", 4.9, "veh-01", 168),
            ("drv-02", "DRV-102", "Anand Murthy", "+91 98452 33445", "KA-02-2020-008914", "On Duty", 4.8, "veh-02", 142),
            ("drv-03", "DRV-103", "Mohammed Rafiq", "+91 98453 44556", "KA-03-2018-001235", "On Break", 4.95, "veh-03", 210),
            ("drv-04", "DRV-104", "Manjunath K.", "+91 98454 55667", "KA-04-2021-006721", "Off Duty", 4.7, "veh-04", 98),
        ]
        cursor.executemany("INSERT INTO drivers VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);", seed_drivers)

    # Check vehicles
    cursor.execute("SELECT COUNT(*) FROM vehicles;")
    if cursor.fetchone()[0] == 0:
        seed_vehicles = [
            ("veh-01", "TRK-01", "Electric Compactor Alpha", "Tata Ultra T.7 Electric", "KA-01-GA-1024", "En Route", "drv-01", 84, 5.5, 12.9784, 77.6408, "Indiranagar Core", "2026-11-10"),
            ("veh-02", "TRK-02", "Zero-Emission Hauler Beta", "Ashok Leyland CleanCity EV", "KA-02-GB-2048", "En Route", "drv-02", 91, 6.0, 12.9756, 77.6097, "Central Core", "2026-11-14"),
            ("veh-03", "TRK-03", "Eco-Compactor Gamma", "Mahindra Treo Bio-Hauler", "KA-03-GC-3072", "Available", "drv-03", 72, 4.0, 12.9345, 77.6190, "Koramangala Commercial", "2026-11-05"),
            ("veh-04", "TRK-04", "Heavy Waste Interceptor Delta", "Eicher Pro 2049 CleanAir", "KA-04-GD-4096", "Charging", "drv-04", 38, 7.5, 12.9756, 77.6097, "MG Road Fleet Depot", "2026-11-01"),
        ]
        cursor.executemany("INSERT INTO vehicles VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", seed_vehicles)

    # Check collection logs
    cursor.execute("SELECT COUNT(*) FROM collection_logs;")
    if cursor.fetchone()[0] == 0:
        seed_logs = [
            ("log-01", "RUN-20261122-01", "2026-11-22 17:30", "TRK-01", "Suresh Gowda", 6, 4.8, 23.8, 7.6, 20.1, "Completed"),
            ("log-02", "RUN-20261122-02", "2026-11-22 14:15", "TRK-02", "Anand Murthy", 5, 4.1, 21.4, 6.9, 18.3, "Completed"),
            ("log-03", "RUN-20261121-01", "2026-11-21 16:45", "TRK-01", "Suresh Gowda", 7, 5.2, 25.1, 7.5, 19.9, "Completed"),
            ("log-04", "RUN-20261120-01", "2026-11-20 18:00", "TRK-03", "Mohammed Rafiq", 6, 4.6, 22.4, 8.4, 22.3, "Completed"),
            ("log-05", "RUN-20261119-01", "2026-11-19 15:20", "TRK-02", "Anand Murthy", 5, 3.9, 24.0, 7.2, 19.1, "Completed"),
        ]
        cursor.executemany("INSERT INTO collection_logs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", seed_logs)

    # Check notifications
    cursor.execute("SELECT COUNT(*) FROM notifications;")
    if cursor.fetchone()[0] == 0:
        seed_notifications = [
            ("notif-01", "Critical Bin Level Alert", "Commercial Street Arcade (BIN-107) reached 96% capacity. Immediate collection required.", "critical", "Just now", 0, "bin-107", None),
            ("notif-02", "Critical Bin Level Alert", "Koramangala 5th Block (BIN-103) reached 94% capacity. Hazardous/organic overflow risk.", "critical", "3 mins ago", 0, "bin-103", None),
            ("notif-03", "Route Dispatched", "Electric Compactor Alpha (TRK-01) en route to Indiranagar & Central Hub.", "info", "12 mins ago", 0, None, "veh-01"),
            ("notif-04", "Vehicle Charging Notice", "Heavy Waste Interceptor (TRK-04) battery at 38%. Connected to fast charger at MG Road Depot.", "warning", "45 mins ago", 1, None, "veh-04"),
        ]
        cursor.executemany("INSERT INTO notifications VALUES (?, ?, ?, ?, ?, ?, ?, ?);", seed_notifications)

    conn.commit()
    conn.close()
    print("[EcoRoute AI] Database initialized & verified at:", DB_PATH)


# ============================================================================
# AUTH & USER REPOSITORY
# ============================================================================
def authenticate_user(email: str, password_plain: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE email = ?;", (email.strip().lower(),)).fetchone()
    conn.close()
    if not user:
        return None
    hashed = hash_password(password_plain)
    if user["password_hash"] == hashed:
        u_dict = dict(user)
        del u_dict["password_hash"]
        return u_dict
    return None


def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE id = ?;", (user_id,)).fetchone()
    conn.close()
    if user:
        d = dict(user)
        del d["password_hash"]
        return d
    return None


def list_users() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    rows = conn.execute("SELECT id, email, full_name, role, avatar_initials, phone, created_at FROM users;").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def create_user(email: str, password_plain: str, full_name: str, role: str = "operator", phone: str = "") -> Dict[str, Any]:
    """Registers a new user (operator or admin) in SQLite."""
    conn = get_db_connection()
    clean_email = email.strip().lower()
    existing = conn.execute("SELECT id FROM users WHERE email = ?;", (clean_email,)).fetchone()
    if existing:
        conn.close()
        raise ValueError(f"User with email '{clean_email}' already exists.")

    role_clean = role.strip().lower()
    if role_clean not in ["admin", "operator"]:
        role_clean = "operator"

    uid = f"usr-{role_clean}-{uuid.uuid4().hex[:6]}"
    parts = full_name.strip().split()
    initials = "".join([p[0].upper() for p in parts[:2]]) if parts else "US"
    hashed = hash_password(password_plain)
    now_iso = datetime.now().isoformat()

    conn.execute(
        "INSERT INTO users (id, email, password_hash, full_name, role, avatar_initials, phone, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?);",
        (uid, clean_email, hashed, full_name.strip(), role_clean, initials, phone.strip(), now_iso)
    )
    conn.commit()
    user = conn.execute("SELECT id, email, full_name, role, avatar_initials, phone, created_at FROM users WHERE id = ?;", (uid,)).fetchone()
    conn.close()
    return dict(user)


# ============================================================================
# SMART BINS REPOSITORY
# ============================================================================
def list_bins() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM bins ORDER BY fill_level DESC;").fetchall()
    conn.close()
    result = []
    for r in rows:
        d = dict(r)
        d["fill"] = d["fill_level"]
        d["fillLevel"] = d["fill_level"]
        d["battery"] = d["battery_level"]
        d["batteryLevel"] = d["battery_level"]
        d["capacityKg"] = d["capacity_kg"]
        d["lastUpdated"] = d["last_updated"]
        d["needsPickup"] = bool(d["needs_pickup"])
        result.append(d)
    return result


def get_bin(bin_id: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    r = conn.execute("SELECT * FROM bins WHERE id = ? OR code = ?;", (bin_id, bin_id)).fetchone()
    conn.close()
    if r:
        d = dict(r)
        d["fill"] = d["fill_level"]
        d["fillLevel"] = d["fill_level"]
        d["battery"] = d["battery_level"]
        d["batteryLevel"] = d["battery_level"]
        d["needsPickup"] = bool(d["needs_pickup"])
        return d
    return None


def create_bin(bin_data: Dict[str, Any]) -> Dict[str, Any]:
    conn = get_db_connection()
    bid = bin_data.get("id") or f"bin-{uuid.uuid4().hex[:6]}"
    code = bin_data.get("code") or f"BIN-{random.randint(113, 999)}"
    fill = float(bin_data.get("fillLevel", bin_data.get("fill", 15.0)))
    needs_pickup = 1 if fill >= 75.0 else 0
    priority = "Critical" if fill >= 75.0 else ("High" if fill >= 50.0 else "Normal")

    conn.execute("""
    INSERT INTO bins (id, code, name, zone, address, lat, lng, fill_level, category, capacity_kg, battery_level, priority, last_updated, needs_pickup)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, (
        bid,
        code,
        bin_data.get("name", "New Municipal Bin"),
        bin_data.get("zone", "Central Core"),
        bin_data.get("address", "Bengaluru Urban Sector"),
        float(bin_data.get("lat", 12.9716)),
        float(bin_data.get("lng", 77.5946)),
        fill,
        bin_data.get("category", "recyclable").lower(),
        float(bin_data.get("capacityKg", 100.0)),
        int(bin_data.get("batteryLevel", 95)),
        bin_data.get("priority", priority),
        "Just now",
        needs_pickup
    ))
    conn.commit()
    conn.close()
    return get_bin(bid)


def update_bin(bin_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    existing = get_bin(bin_id)
    if not existing:
        conn.close()
        return None

    fill = float(updates["fillLevel"]) if "fillLevel" in updates else float(updates.get("fill", existing["fill_level"]))
    needs_pickup = 1 if fill >= 75.0 else 0
    priority = updates.get("priority", "Critical" if fill >= 75.0 else ("High" if fill >= 50.0 else existing.get("priority", "Normal")))

    conn.execute("""
    UPDATE bins
    SET fill_level = ?,
        priority = ?,
        needs_pickup = ?,
        category = COALESCE(?, category),
        name = COALESCE(?, name),
        zone = COALESCE(?, zone),
        address = COALESCE(?, address),
        last_updated = ?
    WHERE id = ? OR code = ?;
    """, (
        fill,
        priority,
        needs_pickup,
        updates.get("category"),
        updates.get("name"),
        updates.get("zone"),
        updates.get("address"),
        "Just now",
        bin_id,
        bin_id
    ))
    conn.commit()
    conn.close()

    # If critical, add notification if none exists recently
    if fill >= 75.0:
        create_notification(
            title="Critical Bin Fill Alert",
            message=f"{existing['name']} ({existing['code']}) reached {fill:.1f}% capacity. Immediate collection needed.",
            level="critical",
            bin_id=existing["id"]
        )

    return get_bin(bin_id)


def delete_bin(bin_id: str) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM bins WHERE id = ? OR code = ?;", (bin_id, bin_id))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return affected > 0


def simulate_sensor_fluctuations() -> List[Dict[str, Any]]:
    """Simulates dynamic bin fill level fluctuations for route optimization testing."""
    conn = get_db_connection()
    rows = conn.execute("SELECT id, fill_level, battery_level, name, code FROM bins;").fetchall()
    for r in rows:
        delta = random.randint(-15, 25)
        new_fill = round(max(8.0, min(99.0, r["fill_level"] + delta)), 1)
        needs_pickup = 1 if new_fill >= 75.0 else 0
        new_battery = max(18, r["battery_level"] - random.choice([0, 1]))
        priority = "Critical" if new_fill >= 75.0 else ("High" if new_fill >= 50.0 else "Normal")

        conn.execute("""
        UPDATE bins
        SET fill_level = ?, battery_level = ?, needs_pickup = ?, priority = ?, last_updated = ?
        WHERE id = ?;
        """, (new_fill, new_battery, needs_pickup, priority, "Just now (Fill Level Update)", r["id"]))

        if new_fill >= 75.0 and r["fill_level"] < 75.0:
            create_notification(
                title="Critical Bin Threshold Exceeded",
                message=f"{r['name']} ({r['code']}) jumped to {new_fill}% (Requires collection pickup).",
                level="critical",
                bin_id=r["id"]
            )

    conn.commit()
    conn.close()
    return list_bins()


# ============================================================================
# VEHICLES & DRIVERS REPOSITORY
# ============================================================================
def list_vehicles() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    rows = conn.execute("""
    SELECT v.*, d.name as driver_name, d.phone as driver_phone, d.employee_code as driver_code
    FROM vehicles v
    LEFT JOIN drivers d ON v.driver_id = d.id
    ORDER BY v.code ASC;
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_vehicle(veh_id: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    r = conn.execute("""
    SELECT v.*, d.name as driver_name, d.phone as driver_phone, d.employee_code as driver_code
    FROM vehicles v
    LEFT JOIN drivers d ON v.driver_id = d.id
    WHERE v.id = ? OR v.code = ?;
    """, (veh_id, veh_id)).fetchone()
    conn.close()
    return dict(r) if r else None


def update_vehicle(veh_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    conn.execute("""
    UPDATE vehicles
    SET status = COALESCE(?, status),
        driver_id = COALESCE(?, driver_id),
        fuel_battery_pct = COALESCE(?, fuel_battery_pct),
        current_lat = COALESCE(?, current_lat),
        current_lng = COALESCE(?, current_lng),
        assigned_zone = COALESCE(?, assigned_zone)
    WHERE id = ? OR code = ?;
    """, (
        updates.get("status"),
        updates.get("driver_id"),
        updates.get("fuel_battery_pct"),
        updates.get("current_lat"),
        updates.get("current_lng"),
        updates.get("assigned_zone"),
        veh_id,
        veh_id
    ))
    conn.commit()
    conn.close()
    return get_vehicle(veh_id)


def create_vehicle(data: Dict[str, Any]) -> Dict[str, Any]:
    conn = get_db_connection()
    vid = data.get("id") or f"veh-{uuid.uuid4().hex[:6]}"
    code = data.get("code") or f"TRK-{random.randint(10, 99)}"
    conn.execute("""
    INSERT INTO vehicles (id, code, name, model, plate_number, status, driver_id, fuel_battery_pct, capacity_tons, current_lat, current_lng, assigned_zone, last_maintenance)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, (
        vid,
        code,
        data.get("name", "Electric Compactor"),
        data.get("model", "Tata Ultra EV CleanCity"),
        data.get("plate_number", f"KA-01-GC-{random.randint(1000, 9999)}"),
        data.get("status", "Available"),
        data.get("driver_id"),
        int(data.get("fuel_battery_pct", 100)),
        float(data.get("capacity_tons", 5.0)),
        float(data.get("current_lat", 12.9756)),
        float(data.get("current_lng", 77.6097)),
        data.get("assigned_zone", "Central Core"),
        datetime.utcnow().strftime("%Y-%m-%d")
    ))
    conn.commit()
    conn.close()
    return get_vehicle(vid)


def list_drivers() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    rows = conn.execute("""
    SELECT d.*, v.code as vehicle_code, v.name as vehicle_name
    FROM drivers d
    LEFT JOIN vehicles v ON d.assigned_vehicle_id = v.id
    ORDER BY d.employee_code ASC;
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def create_driver(data: Dict[str, Any]) -> Dict[str, Any]:
    conn = get_db_connection()
    did = data.get("id") or f"drv-{uuid.uuid4().hex[:6]}"
    code = data.get("employee_code") or f"DRV-{random.randint(105, 999)}"
    conn.execute("""
    INSERT INTO drivers (id, employee_code, name, phone, license_no, status, rating, assigned_vehicle_id, shifts_completed)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, (
        did,
        code,
        data.get("name", "New Driver"),
        data.get("phone", "+91 98000 00000"),
        data.get("license_no", f"KA-01-{random.randint(2018, 2024)}-{random.randint(100000, 999999)}"),
        data.get("status", "On Duty"),
        float(data.get("rating", 4.8)),
        data.get("assigned_vehicle_id"),
        int(data.get("shifts_completed", 0))
    ))
    conn.commit()
    conn.close()
    return {"id": did, "employee_code": code, **data}


def update_driver(driver_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    conn.execute("""
    UPDATE drivers
    SET status = COALESCE(?, status),
        phone = COALESCE(?, phone),
        assigned_vehicle_id = COALESCE(?, assigned_vehicle_id),
        rating = COALESCE(?, rating)
    WHERE id = ? OR employee_code = ?;
    """, (
        updates.get("status"),
        updates.get("phone"),
        updates.get("assigned_vehicle_id"),
        updates.get("rating"),
        driver_id,
        driver_id
    ))
    conn.commit()
    conn.close()
    return {"id": driver_id, **updates}


# ============================================================================
# COLLECTION LOGS REPOSITORY
# ============================================================================
def list_collection_logs() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM collection_logs ORDER BY timestamp DESC;").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def create_collection_log(data: Dict[str, Any]) -> Dict[str, Any]:
    conn = get_db_connection()
    lid = data.get("id") or f"log-{uuid.uuid4().hex[:6]}"
    run_id = data.get("run_id") or f"RUN-{datetime.utcnow().strftime('%Y%m%d')}-{random.randint(10, 99)}"
    ts = data.get("timestamp") or datetime.utcnow().strftime("%Y-%m-%d %H:%M")
    conn.execute("""
    INSERT INTO collection_logs (id, run_id, timestamp, vehicle_code, driver_name, bins_serviced_count, total_weight_tons, distance_km, fuel_saved_liters, co2_avoided_kg, status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, (
        lid,
        run_id,
        ts,
        data.get("vehicle_code", "TRK-01"),
        data.get("driver_name", "Fleet Operator"),
        int(data.get("bins_serviced_count", 5)),
        float(data.get("total_weight_tons", 4.2)),
        float(data.get("distance_km", 22.0)),
        float(data.get("fuel_saved_liters", 7.5)),
        float(data.get("co2_avoided_kg", 19.8)),
        data.get("status", "Completed")
    ))
    conn.commit()
    conn.close()

    create_notification(
        title="Collection Run Completed",
        message=f"{data.get('vehicle_code', 'TRK-01')} completed collection run {run_id}. Serviced {data.get('bins_serviced_count', 5)} smart bins.",
        level="success",
        vehicle_id=data.get("vehicle_id")
    )
    return {"id": lid, "run_id": run_id, "timestamp": ts, **data}


# ============================================================================
# NOTIFICATIONS REPOSITORY
# ============================================================================
def list_notifications() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM notifications ORDER BY timestamp DESC, id DESC LIMIT 50;").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def mark_notification_read(notif_id: str) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE notifications SET is_read = 1 WHERE id = ?;", (notif_id,))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return affected > 0


def clear_all_notifications() -> bool:
    conn = get_db_connection()
    conn.execute("UPDATE notifications SET is_read = 1;")
    conn.commit()
    conn.close()
    return True


def create_notification(title: str, message: str, level: str = "info", bin_id: Optional[str] = None, vehicle_id: Optional[str] = None) -> Dict[str, Any]:
    conn = get_db_connection()
    nid = f"notif-{uuid.uuid4().hex[:8]}"
    ts = datetime.utcnow().strftime("%H:%M UTC")
    conn.execute("""
    INSERT INTO notifications (id, title, message, level, timestamp, is_read, bin_id, vehicle_id)
    VALUES (?, ?, ?, ?, ?, 0, ?, ?);
    """, (nid, title, message, level, ts, bin_id, vehicle_id))
    conn.commit()
    conn.close()
    return {"id": nid, "title": title, "message": message, "level": level, "timestamp": ts, "is_read": 0}


# ============================================================================
# MUNICIPAL ANALYTICS CALCULATION
# ============================================================================
def get_municipal_analytics() -> Dict[str, Any]:
    conn = get_db_connection()
    bins = conn.execute("SELECT * FROM bins;").fetchall()
    vehicles = conn.execute("SELECT * FROM vehicles;").fetchall()
    logs = conn.execute("SELECT * FROM collection_logs;").fetchall()
    conn.close()

    total_bins = len(bins)
    critical_bins = len([b for b in bins if b["fill_level"] >= 75.0])
    avg_fill = round(sum(b["fill_level"] for b in bins) / total_bins, 1) if total_bins > 0 else 0.0

    total_fuel_saved = round(sum(l["fuel_saved_liters"] for l in logs) + 115.0, 1)
    total_co2_avoided = round(sum(l["co2_avoided_kg"] for l in logs) + 1280.0, 1)
    trees_equiv = int(round(total_co2_avoided / 21.0))

    return {
        "summary": {
            "totalItemsSorted": 14820,
            "overallAccuracyPercent": 96.4,
            "segregationRatePercent": 96.4,
            "fuelSavedLiters": total_fuel_saved,
            "treesEquivalent": trees_equiv,
            "co2SavedTotalKg": total_co2_avoided,
            "activeVehiclesCount": len([v for v in vehicles if v["status"] in ["En Route", "Available"]]),
            "binsMonitoredCount": total_bins,
            "criticalBinsCount": critical_bins,
            "averageFillPercent": avg_fill
        },
        "wasteTrends7D": [
            {"day": "Mon", "collectedTons": 14.2, "standardKm": 47.2, "aiKm": 23.8, "fuelSavedL": 7.6, "co2SavedKg": 20.1},
            {"day": "Tue", "collectedTons": 15.6, "standardKm": 48.5, "aiKm": 25.1, "fuelSavedL": 7.5, "co2SavedKg": 19.9},
            {"day": "Wed", "collectedTons": 13.9, "standardKm": 49.0, "aiKm": 22.4, "fuelSavedL": 8.4, "co2SavedKg": 22.3},
            {"day": "Thu", "collectedTons": 16.1, "standardKm": 46.8, "aiKm": 24.0, "fuelSavedL": 7.2, "co2SavedKg": 19.1},
            {"day": "Fri", "collectedTons": 18.4, "standardKm": 51.2, "aiKm": 26.5, "fuelSavedL": 7.9, "co2SavedKg": 20.9},
            {"day": "Sat", "collectedTons": 12.0, "standardKm": 44.5, "aiKm": 21.0, "fuelSavedL": 7.5, "co2SavedKg": 19.8},
            {"day": "Sun", "collectedTons": 10.8, "standardKm": 42.0, "aiKm": 19.5, "fuelSavedL": 7.2, "co2SavedKg": 19.1},
        ],
        "zoneFillRates": [
            {"zone": "Indiranagar Core", "avgFill": 88.0, "status": "Critical", "bins": 2},
            {"zone": "Central Retail & MG Rd", "avgFill": 96.0, "status": "Critical", "bins": 2},
            {"zone": "Koramangala Commercial", "avgFill": 94.0, "status": "Critical", "bins": 2},
            {"zone": "Transit Core & Majestic", "avgFill": 85.0, "status": "Critical", "bins": 2},
            {"zone": "Green Belt & Lalbagh", "avgFill": 52.0, "status": "Normal", "bins": 4},
        ],
        "materialBreakdown": [
            {"stream": "Recyclable / Plastic", "purity": 97.4, "tons": 38.6, "colorHex": "#2563EB"},
            {"stream": "Organic / Food", "purity": 96.8, "tons": 45.2, "colorHex": "#059669"},
            {"stream": "Cardboard & Paper", "purity": 95.2, "tons": 24.8, "colorHex": "#3B82F6"},
            {"stream": "Hazardous & E-Waste", "purity": 98.9, "tons": 8.4, "colorHex": "#DC2626"},
            {"stream": "Residual / Mixed", "purity": 91.5, "tons": 16.2, "colorHex": "#D97706"},
        ]
    }


# Initialize DB upon module load
init_db()
