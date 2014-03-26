bus-router
==========

Ever come across a GTFS feed without the optional shapes.txt file?  bus-router creates a shapes.txt file for stop_times.txt using the Google Maps Directions API.  The routing is not perfect, but it gets the dirty parts out of the way.

## Usage

1. Clone the repo.

    `git clone git@github.com:atlregional/bus-router.git`

2. Get yo' python packages
	
	`pip install Django # for geoDjango geojson libraries`

2. Grab your GTFS data.

    Copy `stop_times.txt`, `trips.txt`, and `stops.txt` into `bus-router/data/gtfs`.
    
3. Run the script

    `cd bus-router`

    `python bus-router.py`
    
## Known Limitations

There are a few finicky things about this script at the moment.

### stop_times.txt
`shape_dist_traveled` column must be empty (or not exist).  bus-router does not create shapes with the corresponding column, so sometimes validators yell at you if these two don't match up.

### Shapes limited to unique `route_id` + `trip_headsign` combinations
For example, if we take `route_id` **MARTA_110**, bus-router only creates new route shapes for each of the `trip_headsign` values associated with this route.  So if there are two trip headsigns but actually 4 different trip patterns, bus-router will only generate 2 shapes.  

This is to cut down on the number of Google Maps API requests and because I didn't implement a database here...

