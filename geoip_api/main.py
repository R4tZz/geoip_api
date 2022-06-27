from fastapi import FastAPI
from geoip_api.routers import authentication, geolocation
from dotenv import load_dotenv
from geoip_api.database.geoip_database import (
    db_engine,
    get_active_engine,
)
from geoip_api.model.database import database_model
from fastapi.routing import Request, Response

app = FastAPI(
    title="Geolocation Api",
    description="This API adds, deletes and provides the geolocation of a given ip or url. It will use a JWT authentication system to manage those locations to database.",
    version="0.1.0",
)


@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    """Middle ware to handle database sessions."""
    response = Response("Internal server error", status_code=500)
    try:
        request.state.db = get_active_engine().get_session_maker()
        response = await call_next(request)
    finally:
        request.state.db.close()
    return response


## Loading routers
app.include_router(authentication.router)
app.include_router(geolocation.router)


@app.get("/")
async def root():
    """Root of the page"""
    return {
        "Geolocation Api": "This API adds, deletes and provides the geolocation of a given ip or url. It will use a JWT authentication system to manage those locations to database."
    }


@app.on_event("startup")
async def startup_event():
    """Loads environment variables and creates all the tables if they are not created."""
    load_dotenv()
    db_engine.get_connection_engine()
    database_model.Base.metadata.create_all(bind=get_active_engine().engine)


@app.on_event("shutdown")
async def shutdown_event():
    """Closes the engine connection on exit."""
    db_engine.close_connection_engine()
