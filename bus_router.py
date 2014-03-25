import json

def main():
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