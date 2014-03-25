import csv, os, subprocess, json, urllib, re, gpolyencode
from pprint import pprint

class AutoVivification(dict):
	"""Implementation of perl's autovivification feature."""
	def __getitem__(self, item):
		try:
			return dict.__getitem__(self, item)
		except KeyError:
			value = self[item] = type(self)()
			return value
def decode(point_str):
	'''Decodes a polyline that has been encoded using Google's algorithm
	http://code.google.com/apis/maps/documentation/polylinealgorithm.html
	
	This is a generic method that returns a list of (latitude, longitude) 
	tuples.
	
	:param point_str: Encoded polyline string.
	:type point_str: string
	:returns: List of 2-tuples where each tuple is (latitude, longitude)
	:rtype: list
	
	'''
			
	# sone coordinate offset is represented by 4 to 5 binary chunks
	coord_chunks = [[]]
	for char in point_str:
		
		# convert each character to decimal from ascii
		value = ord(char) - 63
		
		# values that have a chunk following have an extra 1 on the left
		split_after = not (value & 0x20)		 
		value &= 0x1F
		
		coord_chunks[-1].append(value)
		
		if split_after:
				coord_chunks.append([])
		
	del coord_chunks[-1]
	
	coords = []
	
	for coord_chunk in coord_chunks:
		coord = 0
		
		for i, chunk in enumerate(coord_chunk):					
			coord |= chunk << (i * 5) 
		
		#there is a 1 on the right if the coord is negative
		if coord & 0x1:
			coord = ~coord #invert
		coord >>= 1
		coord /= 100000.0
					
		coords.append(coord)
	
	# convert the 1 dimensional list to a 2 dimensional list and offsets to 
	# actual values
	points = []
	prev_x = 0
	prev_y = 0
	for i in xrange(0, len(coords) - 1, 2):
		if coords[i] == 0 and coords[i + 1] == 0:
			continue
		
		prev_x += coords[i + 1]
		prev_y += coords[i]
		# a round to 6 digits ensures that the floats are the same as when 
		# they were encoded
		points.append((round(prev_x, 6), round(prev_y, 6)))
	
	return points

def processPolylines():
	encoder = gpolyencode.GPolyEncoder()
	json_data=open('data.txt')
	datadir = os.path.join(os.getcwd(), 'data')
	gtfsdir = os.path.join(datadir, 'gtfs')
	data = json.load(json_data, object_hook=_decode_dict)
	# pprint(data)
	json_data.close()
	with open(gtfsdir + "/shapes.txt", 'wb') as shapesfile:
		shapeswriter = csv.writer(shapesfile)
		shapeswriter.writerow(["shape_id","shape_pt_sequence","shape_dist_traveled","shape_pt_lon","shape_pt_lat"])
		for trip, stops in data.items():
			count = 0
			for i in range(20):
				filepath = os.path.join(datadir, trip + "_" + str(i) + ".json")
				if(os.path.exists(filepath)):
					gmaps=open(filepath)
					
					data = json.load(gmaps)
					for leg in data['routes'][0]['legs']:
						for step in leg['steps']:
							points = decode(step['polyline']['points'])
							for point in points:
								point = list(point)
								point.insert(0, trip)
								point.insert(1, count)
								point.insert(2, "")
								shapeswriter.writerow(point)
								count += 1

					json_data.close()

def modifyTrips():
	datadir = os.path.join(os.getcwd(), 'data')
	gtfsdir = os.path.join(datadir, 'gtfs')
	with open(gtfsdir + "/trips.txt", 'r+') as tripsfile:
		tripsreader = csv.reader(tripsfile)
		with open(gtfsdir + "/trips_new.txt", 'wb') as tripsnew:
			tripswriter = csv.writer(tripsnew)
			count = 0
			for row in tripsreader:
				if count == 0:
					tripswriter.writerow(row)
				else:
					# print row[3].replace(" ","") + "_" + row[0]
					row.append(row[3].replace(" ","") + "_" + row[0])
					tripswriter.writerow(row)
				count += 1

def _decode_list(data):
	rv = []
	for item in data:
		if isinstance(item, unicode):
			item = item.encode('utf-8')
		elif isinstance(item, list):
			item = _decode_list(item)
		elif isinstance(item, dict):
			item = _decode_dict(item)
		rv.append(item)
	return rv

def _decode_dict(data):
	rv = {}
	for key, value in data.iteritems():
		if isinstance(key, unicode):
			key = key.encode('utf-8')
		if isinstance(value, unicode):
			value = value.encode('utf-8')
		elif isinstance(value, list):
			value = _decode_list(value)
		elif isinstance(value, dict):
			value = _decode_dict(value)
		rv[key] = value
	return rv

def getDirections():
	json_data=open('data.txt')
	datadir = os.path.join(os.getcwd(), 'data')
	data = json.load(json_data, object_hook=_decode_dict)
	# pprint(data)
	json_data.close()
	base = 'https://maps.googleapis.com/maps/api/directions/json?'
	for trip, stops in data.items():
		# if trip == "MidtownAtlanta_14" or trip == "IndianTrP-R_3" or trip == "SugarloafMills_14" or trip == "DoravilleMarta_10" or trip == "LiveOakPkwy_9" or trip == "I-985P-R_2":
		# 	continue
		# print trip
		# print stops
		stopcount = 1
		segmentcount = 0
		origin = ""
		dest = ""
		points = ""
		previous = ""
		waypoints = ""
		last = stops['stops'][-1]

		for stop  in stops['stops']:
			lastCheck = cmp(stop, last)
			print stop
			# print diff
			# print trip
			if stopcount == 1:
				origin = stop['lat'] + "," + stop['lon']
			elif stopcount == 9:
				waypoints += stop['lat'] + "," + stop['lon']
			elif stopcount == 10 or lastCheck == 0:
				dest = stop['lat'] + "," + stop['lon']
				params = urllib.urlencode({'origin': origin, 'destination': dest, 'waypoints': waypoints, 'sensor': 'false','key': 'AIzaSyD2KTHZHT8Bl-JzgF3yI1t7Ln05udSu318'})
				print params
				response = urllib.urlopen(base + params)
				data = json.load(response)
				with open(datadir + "/" + trip + "_" + str(segmentcount) + '.json', 'w') as outfile:
					json.dump(data, outfile)
				stopcount = 0
				waypoints = ""
				segmentcount += 1
			else:
				waypoints += stop['lat'] + "," + stop['lon'] + "|"

			stopcount += 1



def processGtfs():
	

	datadir = os.path.join(os.getcwd(), 'data/gtfs')
	stopspath = os.path.join(datadir, 'stops.txt')
	timespath = os.path.join(datadir, 'stop_times.txt')
	tripspath = os.path.join(datadir, 'trips.txt')
	trips = AutoVivification()
	names = {}
	with open(tripspath, 'rb') as tripsfile:
		tripsreader = csv.DictReader(tripsfile)
		for trip in tripsreader:
			
			tripname = trip['trip_headsign'].replace(" ","") + "_" + trip['route_id']
			if tripname in names:
				continue
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
				trips[tripname]['stops'] = []
				nextStop = {'id': time["stop_id"]}
				trips[tripname]['stops'].append(nextStop)
				stopscount += 1
				curr_trip = tripname
				tripscount += 1

			elif tripname == curr_trip:
				nextStop = {'id': time["stop_id"]}
				trips[tripname]['stops'].append(nextStop)
				stopscount += 1
				curr_trip = tripname

			else:
				stopscount = 0
	# print trips
	# read stops into dict
	with open(stopspath, 'rb') as stopsfile:
		stopsreader = csv.DictReader(stopsfile)
		for stop in stopsreader:
			# print stop['stop_id']
			for trip in trips:
				print trip
				for i in trips[trip]['stops']:
					# print i
					# print trips[trip]['stops']
					if stop['stop_id'] == i['id']:
						i['lat'] = stop['stop_lat']
						i['lon'] = stop['stop_lon']
	with open('data.txt', 'w') as outfile:
		json.dump(trips, outfile)

	# read latlng for stop_ids from stops.txt
	
	# urlib for https://maps.googleapis.com/maps/api/directions/json?origin=33.983518,-84.084661&destination=33.762069,-84.384326&waypoints=33.765978,-84.387597&sensor=false&key=AIzaSyD2KTHZHT8Bl-JzgF3yI1t7Ln05udSu318

	# get json back

	# decode routes[0].legs[0].steps.0.polyline
	# iterate on legs and steps...
	# add points to array (each with their own number)
	# 
if __name__ == '__main__':
	modifyTrips()