from geoip_api.model.geoip_model_base import InternalBaseModel


class LocationInfo(InternalBaseModel):
    ip_address: str
    city_name: str
    zip_code: str
    latitude: int
    longitude: int
    continent_code: str
    continent_name: str
    country_code: str
    country_name: str
    region_code: str
    region_name: str
