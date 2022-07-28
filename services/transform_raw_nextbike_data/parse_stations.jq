# Version 1
[
.countries[].cities[].places[] | select(.spot == true) |
{
    station_id: .number,
    name: .name,
    latitude: .lat,
    longitude: .lng,
}
]