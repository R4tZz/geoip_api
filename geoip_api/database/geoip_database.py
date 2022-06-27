import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class GeopIPDatabase:
    def __init__(self) -> None:
        self.engine = None

    def get_connection_string(self) -> str:
        try:
            username = os.getenv("MYSQL_USER")
            password = os.getenv("MYSQL_PASSWORD")
            hostname = os.getenv("MYSQL_HOST")
            port = os.getenv("MYSQL_PORT")
            database_name = os.getenv("MYSQL_DATABASE_NAME")
        except:
            raise KeyError(
                "Environment variables for the database are not configured correctly!"
            )

        return (
            f"mysql+pymysql://{username}:{password}@{hostname}:{port}/{database_name}"
        )

    def get_connection_engine(self):
        self.engine = create_engine(self.get_connection_string())
        return self.engine

    def close_connection_engine(self):
        self.engine.dispose()

    def get_session_maker(self):
        return sessionmaker(autocommit=False, autoflush=False, bind=self.engine)()


def get_active_engine():
    if db_engine.engine:
        return db_engine
    else:
        raise ConnectionError("Error getting active engine!")


db_engine = GeopIPDatabase()
