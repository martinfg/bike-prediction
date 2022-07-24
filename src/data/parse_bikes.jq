[
.countries[].cities[].places[] as $places | (if $places.bike_list then $places.bike_list[] else null end) |
{
    bike_id: .number,
    latitude: $places.lat,
    longitude: $places.lng,
	bike_type: .bike_type,
}
]