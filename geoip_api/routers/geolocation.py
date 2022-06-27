from ipaddress import ip_address
import requests, os, json
from urllib import response
from fastapi import APIRouter
from fastapi import Depends, HTTPException, status
from sqlalchemy import true
from geoip_api.model.database.database_model import (
    Continent,
    IPLocations,
    Country,
    Region,
    Location,
)
from geoip_api.model.location.location_model import LocationInfo
from geoip_api.model.ipstackapi.ipstack_model import IPStackModel
from sqlalchemy.orm import Session
from geoip_api.lib.dependecies import get_geoip_db, get_current_active_user

router = APIRouter(
    prefix="/location",
    tags=["LOCATION"],
    dependencies=[Depends(get_current_active_user)],
)


def get_or_create(session, model, defaults=None, **kwargs):
    """Method to get or create a given model to the database."""
    instance = session.query(model).filter_by(**kwargs).one_or_none()
    if instance:
        return instance
    else:
        kwargs |= defaults or {}
        instance = model(**kwargs)
        try:
            session.add(instance)
            session.commit()
            session.refresh()
        except Exception:
            session.rollback()
            instance = session.query(model).filter_by(**kwargs).one()
            return instance


def parse_ipstack_model_to_location_model(ip_stack_model: IPStackModel):
    """Method to parse IPStack model to a simpler model: LocationInfo"""

    location_info = LocationInfo(
        ip_address=ip_stack_model.ip,
        city_name=ip_stack_model.city,
        zip_code=ip_stack_model.continent_code,
        latitude=ip_stack_model.latitude,
        longitude=ip_stack_model.longitude,
        continent_code=ip_stack_model.country_code,
        continent_name=ip_stack_model.continent_code,
        country_code=ip_stack_model.country_code,
        country_name=ip_stack_model.continent_name,
        region_code=ip_stack_model.region_code,
        region_name=ip_stack_model.region_name,
    )
    return location_info


def parse_iplocation_query_to_location_model(ip_url, geoip_dp):
    """Method to parse ip_location query to a simpler model: LocationInfo"""
    parse_to_location_model = (
        geoip_dp.query()
        .with_entities(
            IPLocations.IPAddress,
            IPLocations.Latitude,
            IPLocations.Longitude,
            Location.CityName,
            Location.ZipCode,
            Country.CountryCode,
            Country.CountryName,
            Region.RegionCode,
            Region.RegionName,
            Continent.ContinentCode,
            Continent.ContinentName,
        )
        .join(IPLocations.rel_location)
        .join(Location.rel_region)
        .join(Location.rel_country)
        .join(Location.rel_continent)
        .filter(
            IPLocations.IPAddress == ip_url,
        )
        .first()
    )
    location_info = LocationInfo(
        ip_address=parse_to_location_model.IPAddress,
        city_name=parse_to_location_model.CityName,
        zip_code=parse_to_location_model.ZipCode,
        latitude=parse_to_location_model.Latitude,
        longitude=parse_to_location_model.Longitude,
        continent_code=parse_to_location_model.ContinentCode,
        continent_name=parse_to_location_model.ContinentName,
        country_code=parse_to_location_model.CountryCode,
        country_name=parse_to_location_model.CountryName,
        region_code=parse_to_location_model.RegionCode,
        region_name=parse_to_location_model.RegionName,
    )

    return location_info


def request_ip_stack_api(ip_url: str):
    """Request information to the IP Stack with a given IP or url"""
    req_session = requests.Session()
    api_key = os.getenv("API_IPSTACK_KEY")
    response = req_session.get(f"http://api.ipstack.com/{ip_url}?access_key={api_key}")
    ip_stack_json = json.loads(response.content.decode("utf-8"))

    return ip_stack_json


@router.get("/ip_url/{ip_url}", response_model=LocationInfo)
async def provide_ip_url_location(
    ip_url: str, geoip_db: Session = Depends(get_geoip_db)
):
    """With a given IP it will provide the location from IP Stack API or database.
    It will prioritize database over the IP Stack API since there is a limit of requests that can be done."""

    ## Valites if the ip exists in database
    ip_location_value = (
        geoip_db.query(IPLocations)
        .filter(
            IPLocations.IPAddress == ip_url,
        )
        .one_or_none()
    )

    if ip_location_value:
        ## Parse to Location Info
        location_info = parse_iplocation_query_to_location_model(ip_url, geoip_db)
    else:
        ## Request to the IP Stack API
        ip_stack_json = request_ip_stack_api(ip_url)

        ## Parse IPStack model to Location Info
        location_info = parse_ipstack_model_to_location_model(
            IPStackModel.parse_obj(ip_stack_json)
        )

    return location_info


@router.put(
    "/ip_url/{ip_url}", status_code=status.HTTP_201_CREATED, response_model=LocationInfo
)
async def add_ip_url_location(ip_url: str, geoip_db: Session = Depends(get_geoip_db)):
    """Adds a location with a given IP to the database. If the ip exists it will fail."""

    ## Checks if IP exists in the database
    ip_location_exists = geoip_db.query(IPLocations).filter(
        IPLocations.IPAddress == ip_url,
    )
    if geoip_db.query(ip_location_exists.exists()).scalar():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="IP Address already exist!",
        )

    ## Request to the IP Stack API
    ip_stack_json = request_ip_stack_api(ip_url)

    ## Parse IPStack model to Location Info
    location_info = parse_ipstack_model_to_location_model(
        IPStackModel.parse_obj(ip_stack_json)
    )

    ## Get or create continent model
    continent_model = get_or_create(
        geoip_db,
        Continent,
        ContinentCode=location_info.continent_code,
        ContinentName=location_info.continent_name,
    )

    ## Get or create country model
    country_model = get_or_create(
        geoip_db,
        Country,
        CountryCode=location_info.country_code,
        CountryName=location_info.country_name,
    )

    ## Get or create region model
    region_model = get_or_create(
        geoip_db,
        Region,
        RegionCode=location_info.region_code,
        RegionName=location_info.region_name,
    )

    ## Get or create location model
    location_model = get_or_create(
        geoip_db,
        Location,
        CityName=location_info.city_name,
        ZipCode=location_info.zip_code,
        RegionId=region_model.RegionId,
        CountryId=country_model.CountryId,
        ContinentId=continent_model.ContinentId,
    )

    ## Create IPLocations model
    ip_address_info = IPLocations(
        LocationId=location_model.LocationId,
        IPAddress=location_info.ip_address,
        Latitude=location_info.latitude,
        Longitude=location_info.longitude,
    )

    ## Add the IP location to the database
    geoip_db.add(ip_address_info)
    geoip_db.commit()
    geoip_db.refresh(ip_address_info)

    ## Parse to Location Info
    location_info = parse_iplocation_query_to_location_model(
        ip_address_info.IPAddress, geoip_db
    )
    return location_info


@router.delete("/ip_url/{ip_url}")
async def delete_ip_url_location(
    ip_url: str, geoip_db: Session = Depends(get_geoip_db)
):
    """Method to delete the location information in the database from a given IP."""
    ip_location_value = (
        geoip_db.query(IPLocations)
        .filter(
            IPLocations.IPAddress == ip_url,
        )
        .one_or_none()
    )
    if ip_location_value:
        geoip_db.delete(ip_location_value)
        geoip_db.commit()
    else:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="IP Address does not exist!",
        )

    return {"Success": ip_url + " has been deleted!"}
