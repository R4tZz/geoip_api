from typing import Any, List, Optional

from pydantic import Field
from geoip_api.model.geoip_model_base import InternalBaseModel


class Language(InternalBaseModel):
    code: str
    name: str
    native: str


class Location(InternalBaseModel):
    geoname_id: int
    capital: str
    languages: List[Language]
    country_flag: str
    country_flag_emoji: str
    country_flag_emoji_unicode: str
    calling_code: str
    is_eu: bool


class TimeZone(InternalBaseModel):
    id: str
    current_time: str
    gmt_offset: int
    code: str
    is_daylight_saving: bool


class Currency(InternalBaseModel):
    code: str
    name: str
    plural: str
    symbol: str
    symbol_native: str


class Connection(InternalBaseModel):
    asn: int
    isp: str


class Security(InternalBaseModel):
    is_proxy: bool
    proxy_type: Any
    is_crawler: bool
    crawler_name: Any
    crawler_type: Any
    is_tor: bool
    threat_level: str
    threat_types: Any


class IPStackModel(InternalBaseModel):
    ip: str
    hostname: Optional[str] = None
    type: str
    continent_code: str
    continent_name: str
    country_code: str
    country_name: str
    region_code: str
    region_name: str
    city: str
    zip: str
    latitude: float
    longitude: float
    location: Location
    time_zone: Optional[TimeZone] = Field(None)
    currency: Optional[Currency] = Field(None)
    connection: Optional[Connection] = Field(None)
    security: Optional[Security] = Field(None)
