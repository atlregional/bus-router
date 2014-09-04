import csv, os, subprocess, json, urllib, re, gpolyencode
from pprint import pprint
from geojson import LineString, Point, FeatureCollection, Feature
import geojson
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
	geojsondir = os.path.join(datadir, 'geojson')
	polydir = os.path.join(datadir, 'polylines')
	data = json.load(json_data, object_hook=_decode_dict)
	# pprint(data)
	json_data.close()
	with open(gtfsdir + "/shapes.txt", 'wb') as shapesfile:
		shapeswriter = csv.writer(shapesfile)
		shapeswriter.writerow(["shape_id","shape_pt_sequence","shape_dist_traveled","shape_pt_lon","shape_pt_lat"])
		for trip, stops in data.items():
			print trip
			
			legpoints = []
			jsonpoints = []

			for i in range(20):
				filepath = os.path.join(polydir, trip + "_" + str(i) + ".json")
				if(os.path.exists(filepath)):
					gmaps=open(filepath)
					
					linedata = json.load(gmaps)
					print trip + "_" + str(i)
					if linedata['status'] != "OK":
						continue
					print linedata['routes'][0]['overview_polyline']['points']
					points = decode(linedata['routes'][0]['overview_polyline']['points'])
					# print points
					for point in points:
						dictpoint = {'x': point[0], 'y': point[1]}
						
						legpoints.append(dictpoint)
					# try:		
						# for leg in linedata['routes'][0]['legs']:
						# 	for step in leg['steps']:
						# 		points = decode(step['polyline']['points'])
						# 		# print points
						# 		for point in points:
						# 			dictpoint = {'x': point[0], 'y': point[1]}
									
						# 			legpoints.append(dictpoint)
									
									
					# except:
					# 	print "leg don't exist"
					gmaps.close()
			# print legpoints
			
			# print ls.geojson
			if not legpoints:
				continue
			else:
				simplified = simplify(legpoints, .0002, True)
				# print "new:" + str(simplified)
				count = 0
				for point in simplified:
					pnt = Point(point['x'], point['y'])
					jsonpoints.append(pnt)
					shppoint = [point['x'], point['y']]
					shppoint.insert(0, trip)
					shppoint.insert(1, count)
					shppoint.insert(2, "")
					shapeswriter.writerow(shppoint)
					count += 1
				ls = LineString(jsonpoints)
				gc = GeometryCollection(ls)

				geoj = gc.geojson
				gtfsfile = os.path.join(geojsondir, trip + '.geojson')

				with open(gtfsfile, 'wb') as tripgeo:
					# json.dump(geoj, tripgeo)
					tripgeo.write(geoj)

def modifyTrips():
	datadir = os.path.join(os.getcwd(), 'data')
	gtfsdir = os.path.join(datadir, 'gtfs')
	
	with open(gtfsdir + "/trips.txt", 'r+') as tripsfile:
		tripsreader = csv.DictReader(tripsfile)
		keys = tripsreader.fieldnames
		with open(gtfsdir + "/trips_new.txt", 'wb') as tripsnew:
			tripswriter = csv.DictWriter(tripsnew, keys)
			tripswriter.writeheader()
			for row in tripsreader:
				
				# print row
				newtrip = row['trip_headsign'].replace(" ","").replace("/","") + "_" + row['route_id']
				row['shape_id'] = newtrip
				# print row
				#  remove that pesky last comma
				# print row[0]
				tripswriter.writerow(row)
				# tripsnew.write(string)
				

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
	polydir = os.path.join(datadir, 'polylines')
	data = json.load(json_data, object_hook=_decode_dict)
	# pprint(data)
	json_data.close()
	
	for trip, stops in data.items():
		# if trip == "MidtownAtlanta_14" or trip == "IndianTrP-R_3" or trip == "SugarloafMills_14" or trip == "DoravilleMarta_10" or trip == "LiveOakPkwy_9" or trip == "I-985P-R_2":
		# 	continue
		with open("log.txt", 'a') as log:
			log.write(trip + '\n')
		print trip
		# print stops
		stopcount = 1
		segmentcount = 0
		origin = ""
		dest = ""
		points = ""
		previous = {}
		waypoints = ""
		last = stops['stops'][-1]
		
		for index, stop  in enumerate(stops['stops']):
			fname = polydir + "/" + trip + "_" + str(segmentcount) + '.json'
			lastCheck = cmp(stop, last)
			# print lastCheck
			if stopcount == 1:
				# print "first stop"
				origin = stop['lat'] + "," + stop['lon']

				if segmentcount > 0:
					origin = stops['stops'][index - 1]['lat'] + "," + stops['stops'][index - 1]['lon']
					waypoints += stop['lat'] + "," + stop['lon'] + "|"

				if lastCheck == 0:
					dest = stop['lat'] + "," + stop['lon']
					directionscall(stop, origin, dest, waypoints, fname)
					waypoints = ""
					segmentcount += 1
					continue

				stopcount += 1

			elif stopcount == 9 or lastCheck == 0:
				dest = stop['lat'] + "," + stop['lon'] 
				directionscall(stop, origin, dest, waypoints, fname)
				stopcount = 1
				waypoints = ""
				segmentcount += 1
				continue
			else:
				waypoints += stop['lat'] + "," + stop['lon'] + "|"
				stopcount += 1


def directionscall(stop, origin, dest, waypoints, fname):
	print "getting dirs..."
	base = 'https://maps.googleapis.com/maps/api/directions/json?'
	params = urllib.urlencode({'origin': origin, 'destination': dest, 'waypoints': waypoints, 'sensor': 'false','key': 'AIzaSyBxCIum1F7gg1y_OcKBU5R1-_pMXIA--Ho'})
	# print params
	# if waypoints == "":
	with open("log.txt", 'a') as log:
		log.write(base + params + '\n')
	response = urllib.urlopen(base + params)
	data = json.load(response)
	with open(fname, 'w') as outfile:
		json.dump(data, outfile)
	
def shapesToGeojson():
	json_data=open('data.txt')
	datadir = os.path.join(os.getcwd(), 'data')
	gtfsdir = os.path.join(datadir, 'gtfs')
	geojsondir = os.path.join(datadir, 'geojson')
	data = json.load(json_data, object_hook=_decode_dict)
	json_data.close()
	with open(gtfsdir + "/shapes.txt", 'rb') as shapesfile:
		shapesreader = csv.DictReader(shapesfile)
		keys = shapesreader.fieldnames

		jsonpoints = []
		features = []
		currentTrip = ''
		for i, point in enumerate(shapesreader):
			if point['shape_pt_sequence'] == '0' and i > 0:
				currentTrip = point['shape_id']
				ls = LineString(jsonpoints)
				feature = Feature(geometry=ls, properties={"shape_id": currentTrip})
				features.append(feature)
				jsonpoints = []
			else:
				pnt = (float(point['shape_pt_lon']), float(point['shape_pt_lat']))
				jsonpoints.append(pnt)
				
		fc = FeatureCollection(features)
		print fc

		geojsonfile = os.path.join(geojsondir, 'shapes.geojson')

		with open(geojsonfile, 'wb') as tripgeo:
			geojson.dump(fc, tripgeo)



	# 		else:
	# 			simplified = simplify(legpoints, .0002, True)
	# 			# print "new:" + str(simplified)
	# 			count = 0
	# 			for point in simplified:
	# 				pnt = Point(point['x'], point['y'])
	# 				jsonpoints.append(pnt)
	# 				shppoint = [point['x'], point['y']]
	# 				shppoint.insert(0, trip)
	# 				shppoint.insert(1, count)
	# 				shppoint.insert(2, "")
	# 				shapeswriter.writerow(shppoint)
	# 				count += 1
	# 			ls = LineString(jsonpoints)
	# 			gc = GeometryCollection(ls)

	# 			geoj = gc.geojson
	# 			gtfsfile = os.path.join(geojsondir, trip + '.geojson')

	# 			with open(gtfsfile, 'wb') as tripgeo:
	# 				# json.dump(geoj, tripgeo)
	# 				tripgeo.write(geoj)

def geojsonToShapes():
	datadir = os.path.join(os.getcwd(), 'data')
	gtfsdir = os.path.join(datadir, 'gtfs')
	geojsondir = os.path.join(datadir, 'geojson')

	with open(gtfsdir + "/shapes_new.txt", 'wb') as shapesfile:
		shapeswriter = csv.writer(shapesfile)
		shapeswriter.writerow(["shape_id","shape_pt_sequence","shape_dist_traveled","shape_pt_lon","shape_pt_lat"])

		geojsonfile = os.path.join(geojsondir, 'shapes_new.geojson')

		with open(geojsonfile, 'rb') as fc:
			geo_fc = geojson.load(fc)
			# print geo_fc
			for feature in geo_fc['features']:
				for i, coord in enumerate(feature['geometry']['coordinates']):
					shapeswriter.writerow([feature['properties']['shape_id'],i,'',coord[0],coord[1]])


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
			
			tripname = trip['trip_headsign'].replace(" ","").replace("/","") + "_" + trip['route_id']
			if tripname in names.values():
				continue
			else:
				names[trip['trip_id']] = tripname
				# print tripname
	with open('names.json', 'wb') as namesfile:
		json.dump(names, namesfile)

	# read times into dict
	with open(timespath, 'rb') as timesfile:
		timesreader = csv.DictReader(timesfile)
		tripscount = 0
		stopscount = 0
		curr_trip = ""
		for time in timesreader:
			# print time['trip_id']
			# print names[time['trip_id']]
			
			tripname = ""
			if time['trip_id'] in names.keys():
				tripname = names[time['trip_id']]
			else:
				continue

			if not (tripname in trips):
				trips[tripname]['stops'] = []
				nextStop = {'id': time["stop_id"]}
				trips[tripname]['stops'].append(nextStop)
				curr_trip = tripname
				tripscount += 1

			elif tripname == curr_trip:
				nextStop = {'id': time["stop_id"]}
				trips[tripname]['stops'].append(nextStop)
				stopscount += 1
				curr_trip = tripname
			else:
				continue
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




def getSquareDistance(p1, p2):
	"""
	Square distance between two points
	"""
	dx = p1['x'] - p2['x']
	dy = p1['y'] - p2['y']

	return dx * dx + dy * dy


def getSquareSegmentDistance(p, p1, p2):
	"""
	Square distance between point and a segment
	"""
	x = p1['x']
	y = p1['y']

	dx = p2['x'] - x
	dy = p2['y'] - y

	if dx != 0 or dy != 0:
		t = ((p['x'] - x) * dx + (p['y'] - y) * dy) / (dx * dx + dy * dy)

		if t > 1:
			x = p2['x']
			y = p2['y']
		elif t > 0:
			x += dx * t
			y += dy * t

	dx = p['x'] - x
	dy = p['y'] - y

	return dx * dx + dy * dy


def simplifyRadialDistance(points, tolerance):
	length = len(points)
	prev_point = points[0]
	new_points = [prev_point]

	for i in range(length):
		point = points[i]

		if getSquareDistance(point, prev_point) > tolerance:
			new_points.append(point)
			prev_point = point

	if prev_point != point:
		new_points.append(point)

	return new_points


def simplifyDouglasPeucker(points, tolerance):
	length = len(points)
	markers = [0] * length  # Maybe not the most efficent way?

	first = 0
	last = length - 1

	first_stack = []
	last_stack = []

	new_points = []

	markers[first] = 1
	markers[last] = 1

	while last:
		max_sqdist = 0

		for i in range(first, last):
			sqdist = getSquareSegmentDistance(points[i], points[first], points[last])

			if sqdist > max_sqdist:
				index = i
				max_sqdist = sqdist

		if max_sqdist > tolerance:
			markers[index] = 1

			first_stack.append(first)
			last_stack.append(index)

			first_stack.append(index)
			last_stack.append(last)

		# Can pop an empty array in Javascript, but not Python, so check
		# the length of the list first
		if len(first_stack) == 0:
			first = None
		else:
			first = first_stack.pop()

		if len(last_stack) == 0:
			last = None
		else:
			last = last_stack.pop()

	for i in range(length):
		if markers[i]:
			new_points.append(points[i])

	return new_points


def simplify(points, tolerance=0.1, highestQuality=True):
	sqtolerance = tolerance * tolerance

	if not highestQuality:
		points = simplifyRadialDistance(points, sqtolerance)

	points = simplifyDouglasPeucker(points, sqtolerance)

	return points
if __name__ == '__main__':
	# processGtfs()
	# shapesToGeojson()
	geojsonToShapes()
	# getDirections()
	# processPolylines()
	# modifyTrips()