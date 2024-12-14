"""
This module will contain the required endpoints.
Note that if the project was bigger, we would be using a router, and dispatching the routes in different files.
"""
import fastapi
import http
from typing import *
import pydantic

app = fastapi.FastAPI()

# region: Types
SensorTypeId = int
RoomId = int
Temperature = float
# endregion: Types



@app.post("/temperature")
def add_temperature(room_id: RoomId, sensor_type_id: SensorTypeId, value: Temperature) -> fastapi.Response:
  # Here is an example of preprocessing of the temperature. Example: if we can break
  # all physical laws and go below (as said in assumptions, we will pretend they are all in kelvin)
  if value <0:
    return fastapi.Response(
      content="Invalid temperature. Kelvins cannot be negative.",
      status_code=http.HTTPStatus.BAD_REQUEST,
    )

  # Add here the authorization and authentication. for instance we could check if the

  return fastapi.Response(
    status_code=http.HTTPStatus.CREATED,
  )


class GetTemperatureResponse(pydantic.BaseModel):
  value: float
  # We might have more data in the future.


@app.get("/temperature")
def get_temperature(room: RoomId, sensor: SensorTypeId, value: Temperature, interval: str) -> GetTemperatureResponse:
  """
  Aggregates the temperature on the specified interval.
  """

  return fastapi.Response(
    status_code=http.HTTPStatus.OK,
    content=GetTemperatureResponse(
      value=0, #TODO
    )
  )

