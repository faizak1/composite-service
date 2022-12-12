import json
from datetime import datetime
from flask import Flask, Response, request, redirect, url_for, session
from flask_cors import CORS
import os
import random
import requests

#create trip and create itinerary--> to be called from composite service

# TODO change apis to AWS deployed
USER_PROPS = {
    'microservice': 'User microservice',
    'api': 'http://localhost:5011/api/users_service',
    'fields': ('name', 'email', 'userId', 'tripId', 'fromLocation', 'toLocation', 'fromDate', 'toDate')
}
ITINERARY_PROPS = {
    'microservice': 'Itinerary microservice',
    'api': 'http://localhost:5001/itenerary_service/get_trip',
    'fields': ('itinerary_id')
}
REVIEW_PROPS = {
    'microservice': 'Review microservice',
    'api': 'http://localhost:5012/api/review',
    'fields': ('city', 'user_id')
}

# Create the Flask application object.
# Ned to change this and update the local command
app = Flask(__name__,
            static_url_path='/',
            static_folder='static/class-ui/',
            template_folder='web/templates')

CORS(app)
# cors = CORS(app, resources={r'/users_service/*': {'origins': '*'}})

itenerary_url = str(os.environ.get("ITENERARY_URL"))
users_service_url = str(os.environ.get("USER_URL"))

@app.get("/")
def get_service():
    t = str(datetime.now())
    msg = {
        "Service": "Composite Service",
        "Description ": "A service to manage other microservices for CRUD on user accounts/trips/itineraries",
        "at time": t

    }
    result = Response(json.dumps(msg), status=200, content_type="application/json")
    return result

# create user
@app.route("/composite_service/new_itenerary", methods=["POST"])
def signup():
    if request.method == 'POST':
        fromLocation = request.get_json()['fromLocation']
        toLocation = request.get_json()['toLocation']
        fromDate = request.get_json()['fromDate']
        toDate = request.get_json()['toDate']

        # get src airport code
        getAirportCodeUrl = itenerary_url + '/api/flight/' \
                            + fromLocation
        response = requests.request('GET', getAirportCodeUrl)
        response = response.json()
        fromAirport = response[0]['code']

        # get dest airport code
        getAirportCodeUrl = itenerary_url + '/api/flight/' + toLocation
        response = requests.request('GET', getAirportCodeUrl)
        response = response.json()
        toAirport = response[0]['code']

        # call to get flight details from origin to destination
        toFlightDetails = str(
            itenerary_url + '/api/flight?origin=' + fromAirport + '&destination=' + toAirport + '&date=' + fromDate)
        response = requests.request('GET', toFlightDetails)
        toFlightDetails = response.json()
        to_flight_list = []
        for f in toFlightDetails:
            toFlight = {
                "flight_id": f['id'],
                "price": f['price']['amount'],
                "origin_airport": f['legs'][0]['origin']['name'],
                "destination_airport": f['legs'][0]['destination']['name'],
                "departure": f['legs'][0]['departure'],
                "arrival": f['legs'][0]['arrival'],
                "duration": f['legs'][0]['duration'],
                "carrier": f['legs'][0]['carriers'][0]['name'],
            }
            to_flight_list.append(toFlight)

        fromFlightDetails = str(
            itenerary_url + '/api/flight?origin=' + toAirport + '&destination=' + fromAirport + '&date=' + toDate)
        response = requests.request('GET', fromFlightDetails)
        fromFlightDetails = response.json()
        from_flight_list = []
        for f in fromFlightDetails:
            fromFlight = {
                "flight_id": f['id'],
                "price": f['price']['amount'],
                "origin_airport": f['legs'][0]['origin']['name'],
                "destination_airport": f['legs'][0]['destination']['name'],
                "departure": f['legs'][0]['departure'],
                "arrival": f['legs'][0]['arrival'],
                "duration": f['legs'][0]['duration'],
                "carrier": f['legs'][0]['carriers'][0]['name'],
            }
            from_flight_list.append(fromFlight)

        resp = {"org": fromLocation, "dest": toLocation, "dest_flights": to_flight_list,
                "return_flights": from_flight_list}
        return resp
    else:
        resp = Response('NOT FOUND', status=404,
                       content_type='text/plain')
    return resp



@app.route('/composite_service/get_saved_trips', methods=['POST'])
def get_saved_trips():
    if request.method == 'POST':
        # call the trips table to query the list of trip_id for this user
        req = str(users_service_url+ '/users_service/get_trips?user_id=' + str(request.get_json()['user_id']))
        response = requests.request('GET', req)
        trips = response.json()
        # iterate over trips and call itenerary service by each trip id
        saved_trips = []
        for t in trips:
            req = str(itenerary_url + '/itenerary_service/get_trip?itenerary_id=' + str(t['trip_id']))
            response = requests.request('GET', req)
            saved_trips.append(response.json())
    else:
        saved_trips = Response("NOT FOUND", status=404, content_type="text/plain")
    return saved_trips


if __name__ == "__main__":
    app.debug = True
    app.run(host="0.0.0.0", port=5005)
