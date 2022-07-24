# Version 1
[
.countries[].cities[].places[] | select(.spot == true) |
{
    station_id: .number,
    name: .name,
    latitude: .lat,
    longitude: .lng,
    bikes: .bikes,
    available_bikes: .bikes_available_to_rent,
    booked_bikes: .booked_bikes,
}
]