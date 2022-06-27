from sqlalchemy import BOOLEAN, Column, ForeignKey, VARCHAR, Integer, DECIMAL
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class GeoAPIUsers(Base):
    __tablename__ = "GeoAPIUsers"
    UserId = Column(Integer, primary_key=True, autoincrement=True)
    Username = Column(
        VARCHAR(10, collation="utf8_bin"),
        unique=True,
        nullable=False,
    )
    Email = Column(VARCHAR(50), unique=True)
    Password = Column(VARCHAR(250), nullable=False)
    Disabled = Column(BOOLEAN, default=0)


class Continent(Base):
    __tablename__ = "Continent"
    ContinentId = Column(Integer, primary_key=True, autoincrement=True)
    ContinentCode = Column(VARCHAR(5))
    ContinentName = Column(VARCHAR(50))


class Country(Base):
    __tablename__ = "Country"
    CountryId = Column(Integer, primary_key=True, autoincrement=True)
    CountryCode = Column(VARCHAR(5))
    CountryName = Column(VARCHAR(100))


class Region(Base):
    __tablename__ = "Region"
    RegionId = Column(Integer, primary_key=True, autoincrement=True)
    RegionCode = Column(VARCHAR(5))
    RegionName = Column(VARCHAR(100))


class Location(Base):
    __tablename__ = "Location"
    LocationId = Column(Integer, primary_key=True, autoincrement=True)
    CityName = Column(VARCHAR(50), nullable=False)
    ZipCode = Column(VARCHAR(50), nullable=False)
    RegionId = Column(ForeignKey("Region.RegionId"), nullable=False)
    CountryId = Column(ForeignKey("Country.CountryId"), nullable=False)
    ContinentId = Column(ForeignKey("Continent.ContinentId"), nullable=False)

    rel_region = relationship("Region")
    rel_country = relationship("Country")
    rel_continent = relationship("Continent")


class IPLocations(Base):
    __tablename__ = "IPLocations"
    IPLocationId = Column(Integer, primary_key=True, autoincrement=True)
    LocationId = Column(ForeignKey("Location.LocationId"), nullable=False)
    IPAddress = Column(VARCHAR(20), unique=True)
    Latitude = Column(DECIMAL)
    Longitude = Column(DECIMAL)

    rel_location = relationship("Location")
