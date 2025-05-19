from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.users.users import router as users_router
from api.roles.roles import router as roles_router
from api.stations.stations import router as stations_router
from api.transfers.transfers import router as transfers_router
from api.dispatchers.dispatchers import router as dispatchers_router
from api.companies.companies import router as companies_router
from api.vehicles.vehicles import router as vehicles_router
from api.station_summaries.station_summaries import router as station_summaries_router
from api.supply_regions.supply_regions import router as supply_regions_router
from api.account_regions.account_regions import router as account_regions_router
from api.notifications.notifications import router as notifications_router
from routes.auth import router as auth_router
from  db.model import user, profile, role, station, transfer, dispatcher, company, vehicle, station_summary, supply_region, account_region, notification
from  db.db_setup import engine, Base

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8000",
    # Add your frontend URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api")
app.include_router(users_router, prefix="/api")
app.include_router(roles_router, prefix="/api")
app.include_router(stations_router, prefix="/api")
app.include_router(transfers_router, prefix="/api")
app.include_router(dispatchers_router, prefix="/api")
app.include_router(companies_router, prefix="/api")
app.include_router(vehicles_router, prefix="/api")
app.include_router(station_summaries_router, prefix="/api")
app.include_router(supply_regions_router, prefix="/api")
app.include_router(account_regions_router, prefix="/api")
app.include_router(notifications_router, prefix="/api")

# Create tables
Base.metadata.create_all(bind=engine)