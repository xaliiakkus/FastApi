# crud.py
from sqlalchemy.orm import Session
from db.model.user import User as UserModel
from db.model.profile import Profile
from db.model.role import RoleList
from db.model.menuitem import MenuItem
from db.model.station import StationItem
from db.model.transfer import TransfersDispatcher
from db.model.dispatcher import Dispatcher
from db.model.company import Company
from db.model.vehicle import Vehicle
from db.model.station_summary import StationSummary
from db.model.supply_region import SupplyRegion
from db.model.account_region import AccountRegion
from db.model.notification import Notification
import bcrypt
from datetime import datetime
from typing import Optional, List, Any

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# User CRUD
def get_user(db: Session, user_id: str) -> Optional[UserModel]:
    return db.query(UserModel).filter(UserModel.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[UserModel]:
    return db.query(UserModel).filter(UserModel.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[UserModel]:
    return db.query(UserModel).offset(skip).limit(limit).all()

def create_user(db: Session, user_data: dict) -> UserModel:
    hashed_password = hash_password(user_data["password"])
    db_user = UserModel(
        id=user_data["id"],
        email=user_data["email"],
        password=hashed_password,
        role=user_data["role"],
        roleID=user_data["roleID"],
        displayName=user_data["displayName"],
        photoURL=user_data.get("photoURL"),
        pmpRestriction=user_data.get("pmpRestriction"),
        settings=user_data.get("settings"),
        shortcuts=user_data.get("shortcuts"),
        is_active=user_data.get("is_active", True)
    )
    db.add(db_user)
    
    # Create profile
    first_name, last_name = user_data["displayName"].split(" ", 1) if " " in user_data["displayName"] else (user_data["displayName"], "")
    db_profile = Profile(first_name=first_name, last_name=last_name, user_id=db_user.id)
    db.add(db_profile)
    
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: str, user_data: dict) -> Optional[UserModel]:
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    for key, value in user_data.items():
        if key == "password" and value:
            value = hash_password(value)
        setattr(db_user, key, value)
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: str) -> bool:
    db_user = get_user(db, user_id)
    if not db_user:
        return False
    db.delete(db_user)
    db.commit()
    return True

# RoleList CRUD
def get_role(db: Session, role_id: str) -> Optional[RoleList]:
    return db.query(RoleList).filter(RoleList.id == role_id).first()

def get_roles(db: Session, skip: int = 0, limit: int = 100) -> List[RoleList]:
    return db.query(RoleList).offset(skip).limit(limit).all()

def create_role(db: Session, role_data: dict) -> RoleList:
    db_role = RoleList(
        id=role_data["id"],
        RoleName=role_data["RoleName"],
        menuitems=role_data.get("menuitems")
    )
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role

def update_role(db: Session, role_id: str, role_data: dict) -> Optional[RoleList]:
    db_role = get_role(db, role_id)
    if not db_role:
        return None
    for key, value in role_data.items():
        setattr(db_role, key, value)
    db.commit()
    db.refresh(db_role)
    return db_role

def delete_role(db: Session, role_id: str) -> bool:
    db_role = get_role(db, role_id)
    if not db_role:
        return False
    db.delete(db_role)
    db.commit()
    return True

# MenuItem CRUD
def get_menuitem(db: Session, menu_id: str) -> Optional[MenuItem]:
    return db.query(MenuItem).filter(MenuItem.menuID == menu_id).first()

def get_menuitems(db: Session, skip: int = 0, limit: int = 100) -> List[MenuItem]:
    return db.query(MenuItem).offset(skip).limit(limit).all()

def create_menuitem(db: Session, menuitem_data: dict) -> MenuItem:
    db_menuitem = MenuItem(**menuitem_data)
    db.add(db_menuitem)
    db.commit()
    db.refresh(db_menuitem)
    return db_menuitem

def update_menuitem(db: Session, menu_id: str, menuitem_data: dict) -> Optional[MenuItem]:
    db_menuitem = get_menuitem(db, menu_id)
    if not db_menuitem:
        return None
    for key, value in menuitem_data.items():
        setattr(db_menuitem, key, value)
    db.commit()
    db.refresh(db_menuitem)
    return db_menuitem

def delete_menuitem(db: Session, menu_id: str) -> bool:
    db_menuitem = get_menuitem(db, menu_id)
    if not db_menuitem:
        return False
    db.delete(db_menuitem)
    db.commit()
    return True

# StationItem CRUD
def get_station(db: Session, station_id: str) -> Optional[StationItem]:
    return db.query(StationItem).filter(StationItem.id == station_id).first()

def get_stations(db: Session, skip: int = 0, limit: int = 100) -> List[StationItem]:
    return db.query(StationItem).offset(skip).limit(limit).all()

def create_station(db: Session, station_data: dict) -> StationItem:
    db_station = StationItem(**station_data)
    db.add(db_station)
    db.commit()
    db.refresh(db_station)
    return db_station

def update_station(db: Session, station_id: str, station_data: dict) -> Optional[StationItem]:
    db_station = get_station(db, station_id)
    if not db_station:
        return None
    for key, value in station_data.items():
        setattr(db_station, key, value)
    db.commit()
    db.refresh(db_station)
    return db_station

def delete_station(db: Session, station_id: str) -> bool:
    db_station = get_station(db, station_id)
    if not db_station:
        return False
    db.delete(db_station)
    db.commit()
    return True

# TransfersDispatcher CRUD
def get_transfer(db: Session, transfer_id: str) -> Optional[TransfersDispatcher]:
    return db.query(TransfersDispatcher).filter(TransfersDispatcher.id == transfer_id).first()

def get_transfers(db: Session, skip: int = 0, limit: int = 100) -> List[TransfersDispatcher]:
    return db.query(TransfersDispatcher).offset(skip).limit(limit).all()

def create_transfer(db: Session, transfer_data: dict) -> TransfersDispatcher:
    db_transfer = TransfersDispatcher(**transfer_data)
    db.add(db_transfer)
    db.commit()
    db.refresh(db_transfer)
    return db_transfer

def update_transfer(db: Session, transfer_id: str, transfer_data: dict) -> Optional[TransfersDispatcher]:
    db_transfer = get_transfer(db, transfer_id)
    if not db_transfer:
        return None
    for key, value in transfer_data.items():
        setattr(db_transfer, key, value)
    db.commit()
    db.refresh(db_transfer)
    return db_transfer

def delete_transfer(db: Session, transfer_id: str) -> bool:
    db_transfer = get_transfer(db, transfer_id)
    if not db_transfer:
        return False
    db.delete(db_transfer)
    db.commit()
    return True

# Dispatcher CRUD
def get_dispatcher(db: Session, dispatcher_id: int) -> Optional[Dispatcher]:
    return db.query(Dispatcher).filter(Dispatcher.id == dispatcher_id).first()

def get_dispatchers(db: Session, skip: int = 0, limit: int = 100) -> List[Dispatcher]:
    return db.query(Dispatcher).offset(skip).limit(limit).all()

def create_dispatcher(db: Session, dispatcher_data: dict) -> Dispatcher:
    db_dispatcher = Dispatcher(**dispatcher_data)
    db.add(db_dispatcher)
    db.commit()
    db.refresh(db_dispatcher)
    return db_dispatcher

def update_dispatcher(db: Session, dispatcher_id: int, dispatcher_data: dict) -> Optional[Dispatcher]:
    db_dispatcher = get_dispatcher(db, dispatcher_id)
    if not db_dispatcher:
        return None
    for key, value in dispatcher_data.items():
        setattr(db_dispatcher, key, value)
    db.commit()
    db.refresh(db_dispatcher)
    return db_dispatcher

def delete_dispatcher(db: Session, dispatcher_id: int) -> bool:
    db_dispatcher = get_dispatcher(db, dispatcher_id)
    if not db_dispatcher:
        return False
    db.delete(db_dispatcher)
    db.commit()
    return True

# Company CRUD
def get_company(db: Session, company_id: str) -> Optional[Company]:
    return db.query(Company).filter(Company.CompanyId == company_id).first()

def get_companies(db: Session, skip: int = 0, limit: int = 100) -> List[Company]:
    return db.query(Company).offset(skip).limit(limit).all()

def create_company(db: Session, company_data: dict) -> Company:
    db_company = Company(**company_data)
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return db_company

def update_company(db: Session, company_id: str, company_data: dict) -> Optional[Company]:
    db_company = get_company(db, company_id)
    if not db_company:
        return None
    for key, value in company_data.items():
        setattr(db_company, key, value)
    db.commit()
    db.refresh(db_company)
    return db_company

def delete_company(db: Session, company_id: str) -> bool:
    db_company = get_company(db, company_id)
    if not db_company:
        return False
    db.delete(db_company)
    db.commit()
    return True

# Vehicle CRUD
def get_vehicle(db: Session, vehicle_id: str) -> Optional[Vehicle]:
    return db.query(Vehicle).filter(Vehicle.VehicleId == vehicle_id).first()

def get_vehicles(db: Session, skip: int = 0, limit: int = 100) -> List[Vehicle]:
    return db.query(Vehicle).offset(skip).limit(limit).all()

def create_vehicle(db: Session, vehicle_data: dict) -> Vehicle:
    db_vehicle = Vehicle(**vehicle_data)
    db.add(db_vehicle)
    db.commit()
    db.refresh(db_vehicle)
    return db_vehicle

def update_vehicle(db: Session, vehicle_id: str, vehicle_data: dict) -> Optional[Vehicle]:
    db_vehicle = get_vehicle(db, vehicle_id)
    if not db_vehicle:
        return None
    for key, value in vehicle_data.items():
        setattr(db_vehicle, key, value)
    db.commit()
    db.refresh(db_vehicle)
    return db_vehicle

def delete_vehicle(db: Session, vehicle_id: str) -> bool:
    db_vehicle = get_vehicle(db, vehicle_id)
    if not db_vehicle:
        return False
    db.delete(db_vehicle)
    db.commit()
    return True

# StationSummary CRUD
def get_station_summary(db: Session, summary_id: str) -> Optional[StationSummary]:
    return db.query(StationSummary).filter(StationSummary.id == summary_id).first()

def get_station_summaries(db: Session, skip: int = 0, limit: int = 100) -> List[StationSummary]:
    return db.query(StationSummary).offset(skip).limit(limit).all()

def create_station_summary(db: Session, summary_data: dict) -> StationSummary:
    db_summary = StationSummary(**summary_data)
    db.add(db_summary)
    db.commit()
    db.refresh(db_summary)
    return db_summary

def update_station_summary(db: Session, summary_id: str, summary_data: dict) -> Optional[StationSummary]:
    db_summary = get_station_summary(db, summary_id)
    if not db_summary:
        return None
    for key, value in summary_data.items():
        setattr(db_summary, key, value)
    db.commit()
    db.refresh(db_summary)
    return db_summary

def delete_station_summary(db: Session, summary_id: str) -> bool:
    db_summary = get_station_summary(db, summary_id)
    if not db_summary:
        return False
    db.delete(db_summary)
    db.commit()
    return True

# SupplyRegion CRUD
def get_supply_region(db: Session, region_id: int) -> Optional[SupplyRegion]:
    return db.query(SupplyRegion).filter(SupplyRegion.Id == region_id).first()

def get_supply_regions(db: Session, skip: int = 0, limit: int = 100) -> List[SupplyRegion]:
    return db.query(SupplyRegion).offset(skip).limit(limit).all()

def create_supply_region(db: Session, region_data: dict) -> SupplyRegion:
    db_region = SupplyRegion(**region_data)
    db.add(db_region)
    db.commit()
    db.refresh(db_region)
    return db_region

def update_supply_region(db: Session, region_id: int, region_data: dict) -> Optional[SupplyRegion]:
    db_region = get_supply_region(db, region_id)
    if not db_region:
        return None
    for key, value in region_data.items():
        setattr(db_region, key, value)
    db.commit()
    db.refresh(db_region)
    return db_region

def delete_supply_region(db: Session, region_id: int) -> bool:
    db_region = get_supply_region(db, region_id)
    if not db_region:
        return False
    db.delete(db_region)
    db.commit()
    return True

# AccountRegion CRUD
def get_account_region(db: Session, region_id: int) -> Optional[AccountRegion]:
    return db.query(AccountRegion).filter(AccountRegion.Id == region_id).first()

def get_account_regions(db: Session, skip: int = 0, limit: int = 100) -> List[AccountRegion]:
    return db.query(AccountRegion).offset(skip).limit(limit).all()

def create_account_region(db: Session, region_data: dict) -> AccountRegion:
    db_region = AccountRegion(**region_data)
    db.add(db_region)
    db.commit()
    db.refresh(db_region)
    return db_region

def update_account_region(db: Session, region_id: int, region_data: dict) -> Optional[AccountRegion]:
    db_region = get_account_region(db, region_id)
    if not db_region:
        return None
    for key, value in region_data.items():
        setattr(db_region, key, value)
    db.commit()
    db.refresh(db_region)
    return db_region

def delete_account_region(db: Session, region_id: int) -> bool:
    db_region = get_account_region(db, region_id)
    if not db_region:
        return False
    db.delete(db_region)
    db.commit()
    return True

# Notification CRUD
def get_notification(db: Session, notification_id: str) -> Optional[Notification]:
    return db.query(Notification).filter(Notification.id == notification_id).first()

def get_notifications(db: Session, skip: int = 0, limit: int = 100) -> List[Notification]:
    return db.query(Notification).offset(skip).limit(limit).all()

def create_notification(db: Session, notification_data: dict) -> Notification:
    db_notification = Notification(**notification_data)
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    return db_notification

def update_notification(db: Session, notification_id: str, notification_data: dict) -> Optional[Notification]:
    db_notification = get_notification(db, notification_id)
    if not db_notification:
        return None
    for key, value in notification_data.items():
        setattr(db_notification, key, value)
    db.commit()
    db.refresh(db_notification)
    return db_notification

def delete_notification(db: Session, notification_id: str) -> bool:
    db_notification = get_notification(db, notification_id)
    if not db_notification:
        return False
    db.delete(db_notification)
    db.commit()
    return True