[
.countries[].cities[].places[] | select(.spot == true) |
{
    name: .name,
    number: .number,
    latitude: .lat,
    longitude: .lng,
    bikes: .bikes,
    available_bikes: .bikes_available_to_rent,
    booked_bikes: .booked_bikes,
}
]