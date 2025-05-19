# scripts/seed_db.py
import psycopg2
from psycopg2.extras import Json
import bcrypt
from datetime import datetime

# Your JSON data (abridged for brevity)
json_data = {
    "users": [
        {
            "id": "651655",
            "password": "1234",
            "role": "admin",
            "roleID": "1",
            "displayName": "Ali Akkuş",
            "photoURL": "/assets/images/avatars/sbilsel.jpg",
            "email": "admin@fusetheme.com",
            "pmpRestriction": {"CompanyID": "1", "StationIDList": "", "DispatcherIDList": ""},
            "settings": {"layout": {}, "theme": {}},
            "shortcuts": ["apps.calendar", "apps.mailbox", "apps.contacts"]
        },
        # ... other users ...
    ],
    "rolelist": [
        {"id": "1", "RoleName": "admin", "menuitems": ["1", "2", "3", "4"]},
        # ... other roles ...
    ],
    # ... other sections ...
}

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def get_db_connection():
    return psycopg2.connect(
        host="POSTGRES_db",
        port="5432",
        dbname="postgres",
        user="postgres",
        password="1453"
    )

def seed_database():
    conn = get_db_connection()
    cur = conn.cursor()

    # Seed users
    for user in json_data["users"]:
        hashed_password = hash_password(user["password"]) if not user["password"].startswith('$2b$') else user["password"]
        cur.execute(
            """
            INSERT INTO users (id, email, password, role, roleID, displayName, photoURL, pmpRestriction, settings, shortcuts, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
            """,
            (
                user["id"],
                user["email"],
                hashed_password,
                user["role"],
                user["roleID"],
                user["displayName"],
                user["photoURL"],
                Json(user["pmpRestriction"]),
                Json(user["settings"]),
                Json(user["shortcuts"]),
                True
            )
        )
        # Seed profiles
        first_name, last_name = user["displayName"].split(" ", 1) if " " in user["displayName"] else (user["displayName"], "")
        cur.execute(
            """
            INSERT INTO profiles (first_name, last_name, user_id)
            VALUES (%s, %s, %s)
            ON CONFLICT (user_id) DO NOTHING
            """,
            (first_name, last_name, user["id"])
        )

    # Seed rolelist
    for role in json_data["rolelist"]:
        cur.execute(
            """
            INSERT INTO rolelist (id, RoleName, menuitems)
            VALUES (%s, %s, %s)
            ON CONFLICT (id) DO NOTHING
            """,
            (role["id"], role["RoleName"], Json(role["menuitems"]))
        )

    # Seed menuitems
    for item in json_data["menuitems"]:
        cur.execute(
            """
            INSERT INTO menuitems (menuID, menuDisplayname, menuurl, title, subtitle, type, icon, translate, translateKey, children)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (menuID) DO NOTHING
            """,
            (
                item["menuID"],
                item["menuDisplayname"],
                item["menuurl"],
                item.get("title"),
                item.get("subtitle"),
                item.get("type"),
                item.get("icon"),
                item.get("translate"),
                item.get("translateKey"),
                Json(item["children"])
            )
        )

    # Seed stations
    for station in json_data["stationsItems"]:
        cur.execute(
            """
            INSERT INTO stations (id, name, address, taxOffice, taxNumber, lat, lng, phone, "order", status, PumperId, city, CompanyId)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
            """,
            (
                station["id"],
                station["name"],
                station["address"],
                station["taxOffice"],
                station["taxNumber"],
                station["lat"],
                station["lng"],
                station["phone"],
                station["order"],
                station["status"],
                station["PumperId"],
                station["city"],
                station["CompanyId"]
            )
        )

    # Seed transfers
    for transfer in json_data["TransfersDispatcher"]:
        cur.execute(
            """
            INSERT INTO transfers (id, OID, CompanyId, DispatcherId, VehicleId, Status, DateRealized, CreateDate, GrandTotalStart, BatchTotal, Type, BatchPrice)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
            """,
            (
                transfer["id"],
                transfer["OID"],
                transfer["CompanyId"],
                transfer["DispatcherId"],
                transfer["VehicleId"],
                transfer["Status"],
                datetime.fromisoformat(transfer["DateRealized"].replace("Z", "+00:00")),
                transfer["CreateDate"],
                float(transfer["GrandTotalStart"]),
                float(transfer["BatchTotal"]),
                transfer["Type"],
                float(transfer["BatchPrice"])
            )
        )

    # Seed dispatchers
    for dispatcher in json_data["dispatchers"]:
        cur.execute(
            """
            INSERT INTO dispatchers (id, IMEI, StationId, DispatcherName, LastUpdateDate, GrandTotal, K, isActive, DaviceId, Version, Tell, City, PName, District, PumpModel, isNotificationMailActive, CompanyId)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
            """,
            (
                dispatcher["id"],
                dispatcher["IMEI"],
                dispatcher["StationId"],
                dispatcher["DispatcherName"],
                datetime.fromisoformat(dispatcher["LastUpdateDate"].replace("Z", "+00:00")),
                float(dispatcher["GrandTotal"]),
                dispatcher["K"],
                dispatcher["isActive"],
                dispatcher["DaviceId"],
                datetime.fromisoformat(dispatcher["Version"].replace("Z", "+00:00")),
                dispatcher["Tell"],
                dispatcher["City"],
                dispatcher["PName"],
                dispatcher["District"],
                dispatcher["PumpModel"],
                dispatcher["isNotificationMailActive"],
                dispatcher["CompanyId"]
            )
        )

    # Seed companies
    for company in json_data["Company"]:
        cur.execute(
            """
            INSERT INTO companies (CompanyId, CompanyName, OwnerId)
            VALUES (%s, %s, %s)
            ON CONFLICT (CompanyId) DO NOTHING
            """,
            (company["CompanyId"], company["CompanyName"], company["OwnerId"])
        )

    # Seed vehicles
    for vehicle in json_data["vehicles"]:
        cur.execute(
            """
            INSERT INTO vehicles (VehicleId, OID, Company, CardName, MonthLimit, MontTransfer, Totaltransfer, CardTypeID, RfId, IsActive)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (VehicleId) DO NOTHING
            """,
            (
                vehicle["VehicleId"],
                vehicle["OID"],
                vehicle["Company"],
                vehicle["CardName"],
                float(vehicle["MonthLimit"]),
                float(vehicle["MontTransfer"]),
                float(vehicle["Totaltransfer"]),
                vehicle["CardTypeID"],
                vehicle["RfId"],
                vehicle["IsActive"]
            )
        )

    # Seed station summaries
    for summary in json_data["StationSummary"]:
        cur.execute(
            """
            INSERT INTO station_summaries (id, supplyId, accountId, name, address, taxOffice, taxNumber, lat, lng, phone, "order", city, PumperId, CompanyId, status, Dispatchers)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
            """,
            (
                summary["id"],
                summary["supplyId"],
                summary["accountId"],
                summary["name"],
                summary["address"],
                summary["taxOffice"],
                summary["taxNumber"],
                summary["lat"],
                summary["lng"],
                summary["phone"],
                summary["order"],
                summary["city"],
                summary["PumperId"],
                summary["CompanyId"],
                summary["status"],
                Json(summary["Dispatchers"])
            )
        )

    # Seed supply regions
    for region in json_data["SupplyRegion"]:
        cur.execute(
            """
            INSERT INTO supply_regions (Id, name)
            VALUES (%s, %s)
            ON CONFLICT (Id) DO NOTHING
            """,
            (region["Id"], region["name"])
        )

    # Seed account regions
    for region in json_data["AccountRegion"]:
        cur.execute(
            """
            INSERT INTO account_regions (Id, name)
            VALUES (%s, %s)
            ON CONFLICT (Id) DO NOTHING
            """,
            (region["Id"], region["name"])
        )

    # Seed notifications
    for notification in json_data["notifications"]:
        cur.execute(
            """
            INSERT INTO notifications (id, company_id, station_id, dispatcher_id, transfer_batch_total, transfer_grand_total_start, transfer_create_date, company_name, station_name, dispatcher_name)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
            """,
            (
                notification["id"],
                notification["company_id"],
                notification["station_id"],
                notification["dispatcher_id"],
                notification["transfer_batch_total"],
                notification["transfer_grand_total_start"],
                datetime.fromisoformat(notification["transfer_create_date"].replace("Z", "+00:00")),
                notification["company_name"],
                notification["station_name"],
                notification["dispatcher_name"]
            )
        )

    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    seed_database()