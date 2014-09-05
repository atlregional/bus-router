bus-router
==========

Ever come across a GTFS feed without the optional shapes.txt file?  bus-router creates a shapes.txt file for stop_times.txt using [OSRM](http://project-osrm.org/).  The routing isn't always perfect, but it gets the dirty parts out of the way.

:balloon::birthday:**NEW!!**:balloon::birthday: bus-router now creates valid GeoJSON from your shapes.txt file so that you can play with/view the routes in [geojson.io](http://geojson.io), [gist](https://gist.github.com), [GitHub](https://help.github.com/articles/mapping-geojson-files-on-github), etc.

## Requirements

Need Python 2.7 and pip to install geojson package.

## Usage

This script is probably most relevant for those routes that have wide stop spacing (for example, express bus routes), where you have stretches of uncharted territory between stops.  It still works for local bus routes, but the value added is less.

Final word: you can adjust the "smoothness" of the final shapes, by changing the second argument for the `simplify()` call.  Right now it's at `.0002`, make it larger for more jagged-y shapes, smaller for smoother.

1. Clone the repo.

    `git clone git@github.com:atlregional/bus-router.git`

2. Get packages for geojson libraries (use `sudo` if you experience permissions errors)
	
	`pip install geojson`

	`pip install gpolyencode`

2. Grab your GTFS data.

    Copy `stop_times.txt`, `trips.txt`, and `stops.txt` into `bus-router/data/gtfs`.
    
3. Change file name `env.json.tmp` to `env.json` and replace `"INSERT KEY HERE"` your Google API key.

4. Run the script

    `cd bus-router`

    `python bus-router.py`
  	
## Optional command-line arguments

```bash
optional arguments:
  -h, --help           show this help message and exit
  -d osrm, --dir osrm  specify the directions provider, either "goog" or
                       "osrm"
  -s, --shapes         create shapes.txt from GeoJSON
  -l, --lines          process polylines if directions calls have already been
                       made
  -t, --trips          modify trips file with new shape_ids (creates new file)
  -g, --geojson        create GeoJSON from shapes.txt
```

## Notes on Data Licensing

### Google Directions API
It should be noted that using the [Google Directions API](https://developers.google.com/maps/documentation/directions/) to create these routes is [questionable at best from a licensing perspective](https://groups.google.com/d/msg/transit-developers/EIe2dRsRWyY/IlGSd2oPG0gJ) ([Google ToS](https://developers.google.com/maps/terms)).  Ironically enough, this tool could very well be used by public transport agencies to feed data to Google Transit...

### OSRM API/OpenStreetMap
The default option for creating bus routes here is the [Open Source Routing Machine (OSRM)](http://project-osrm.org/).  As such, any routes derived from this tool is subject to the [ODbL](http://opendatacommons.org/licenses/odbl/).  

Be sure that any use of this tool is respectful of OSRM's [API Usage Policy](https://github.com/Project-OSRM/osrm-backend/wiki/Api-usage-policy).

Big thanks to OSRM for creating a routing engine for the entire globe!

## Known Limitations

There are a few finicky things about this script at the moment.

### stop_times.txt
`shape_dist_traveled` column must be empty (or not exist).  bus-router does not create shapes with the corresponding column, so sometimes validators yell at you if these two don't match up.

### Shapes limited to unique `route_id` + `trip_headsign` combinations
For example, if we take `route_id` **MARTA_110**, bus-router only creates new route shapes for each of the `trip_headsign` values associated with this route.  So if there are two trip headsigns but actually 4 different trip patterns, bus-router will only generate 2 shapes.  

This is to cut down on the number of Google Maps API requests and because I didn't implement a database here...

