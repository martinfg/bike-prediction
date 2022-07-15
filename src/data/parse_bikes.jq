[
.countries[].cities[].places[] as $places | (if $places.bike_list then $places.bike_list[] else null end) |
{
    latitude: $places.lat,
    longitude: $places.lng,
    number: .number,
	bike_type: .bike_type,
}
]