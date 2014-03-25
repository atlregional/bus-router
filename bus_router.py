import csv, os, subprocess, json

class AutoVivification(dict):
    """Implementation of perl's autovivification feature."""
    def __getitem__(self, item):
        try:
            return dict.__getitem__(self, item)
        except KeyError:
            value = self[item] = type(self)()
            return value

def main():
	

	datadir = os.path.join(os.getcwd(), 'data')
	stopspath = os.path.join(datadir, 'stops.txt')
	timespath = os.path.join(datadir, 'stop_times.txt')
	tripspath = os.path.join(datadir, 'trips.txt')
	trips = AutoVivification()
	names = {}
	with open(tripspath, 'rb') as tripsfile:
		tripsreader = csv.DictReader(tripsfile)
		for trip in tripsreader:
			
			tripname = trip['route_id'] + trip['trip_headsign']
			if tripname in names:
				break
			else:
				names[trip['trip_id']] = tripname
				print tripname
			
	# read times into dict
	with open(timespath, 'rb') as timesfile:
		timesreader = csv.DictReader(timesfile)
		tripscount = 0
		stopscount = 0
		for time in timesreader:
			tripname = names[time['trip_id']]
			if stopscount == 0 and not (tripname in trips):
				trips[tripname]['stops'][stopscount]['id'] = time["stop_id"]
				stopscount += 1
				curr_trip = tripname
				tripscount += 1

			elif tripname == curr_trip:
				trips[tripname]['stops'][stopscount]['id'] = time["stop_id"]
				stopscount += 1
				curr_trip = tripname

			else:
				stopscount = 0
	print trips
	# read stops into dict
	with open(stopspath, 'rb') as stopsfile:
		stopsreader = csv.DictReader(stopsfile)
		for stop in stopsreader:
			print stop['stop_id']
			for trip in trips:
				print trip
				for stoptime in trips[trip]['stops']:
					print trips[trip]['stops'][stoptime]['id']
					if stop['stop_id'] == trips[trip]['stops'][stoptime]['id']:
						trips[trip]['stops'][stoptime]['lat'] = stop['stop_lat']
						trips[trip]['stops'][stoptime]['lon'] = stop['stop_lon']
	with open('data.txt', 'w') as outfile:
		json.dump(trips, outfile)
		
				

# for trip in trips:
# 			print trip
# 			for stop in trips[trip]['stops']:
# 				print 'id: ' + trips[trip]['stops'][stop]['id']
# 				for row in stopsreader:
# 					print row['stop_id'] + ' & ' + trips[trip]['stops'][stop]['id']
# 					if row['stop_id'] == trips[trip]['stops'][stop]['id']:
# 						trips[trip]['stops'][stop]['lat'] = row['stop_lat']
# 						trips[trip]['stops'][stop]['lon'] = row['stop_lon']
# 						print trips[trip]['stops'][stop]

	# read stop_ids from stop_times.txt
	# while trip_id is the same, add stops to array inside "tripid" object
	#[ 
	# {
	# 	trip_id: "yadda",
	#	stops: [
	#	{
	#		id: "1234",
	#		lat: "33",
	# 		lng: "-87"
	#	},
	#	{
	#		id: "1234",
	#		lat: "33",
	# 		lng: "-87"
	#	},
	#	{
	#		id: "1234",
	#		lat: "33",
	# 		lng: "-87"
	#	}
	# 	]
	# },
	# {
	# 	trip_id: "yadda",
	#	stops: [
	#	{
	#		id: "1234",
	#		lat: "33",
	# 		lng: "-87"
	#	},
	#	{
	#		id: "1234",
	#		lat: "33",
	# 		lng: "-87"
	#	},
	#	{
	#		id: "1234",
	#		lat: "33",
	# 		lng: "-87"
	#	}
	# 	]
	# }
	#]
	#
	#
	# read latlng for stop_ids from stops.txt
	
	# urlib for https://maps.googleapis.com/maps/api/directions/json?origin=33.983518,-84.084661&destination=33.762069,-84.384326&waypoints=33.765978,-84.387597&sensor=false&key=AIzaSyD2KTHZHT8Bl-JzgF3yI1t7Ln05udSu318

	# get json back

	# decode routes[0].legs[0].steps.0.polyline
	# iterate on legs and steps...
	# add points to array (each with their own number)
	# 
if __name__ == '__main__':
	main()