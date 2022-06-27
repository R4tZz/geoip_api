from pydantic import BaseModel


class InternalBaseModel(BaseModel):
    class Config:
        allow_population_by_field_name = True
