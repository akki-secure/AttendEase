from pydantic import BaseModel, Field


class LocationCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    radius_meters: int = Field(ge=10, le=5000, default=200)
    is_active: bool = True


class LocationUpdateRequest(LocationCreateRequest):
    pass


class LocationResponse(BaseModel):
    id: int
    name: str
    latitude: float
    longitude: float
    radius_meters: int
    is_active: bool

    model_config = {"from_attributes": True}


class GeofenceSettingResponse(BaseModel):
    enabled: bool


class GeofenceSettingUpdateRequest(BaseModel):
    enabled: bool
