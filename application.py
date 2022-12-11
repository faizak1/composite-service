import json
from datetime import datetime
from flask import Flask, Response, request, redirect, url_for, session
from flask_cors import CORS
import os
import random
import boto3


import requests
from oauthlib.oauth2 import WebApplicationClient
from user_service_resource import UserResource
from user import User

from flask import Flask, redirect, request, url_for
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)

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
    'api': 'http://localhost:5003/api/review',
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
frontend_url = str(os.environ.get("FRONTEND_URL"))
review_url = str(os.environ.get("REVIEW_URL"))
user_service_url = str(os.environ.get("USER_SERVICE_URL"))

app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)
login_manager = LoginManager()
login_manager.init_app(app)

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

#Get auth from user service
@app.get("/home")
def get_user_auth():
    response = str(user_service_url + '/login?userId=')
    return response

@app.route("/users_service/recommend", methods=["GET"])
def recommend():
    if request.method == 'GET':
        random_from_location = ["prague", "delhi", "miami"]
        random_to_location = ["california", "dhaka", "milan"]
        random_index_from = random.randint(0,len(random_from_location)-1)
        random_index_to = random.randint(0,len(random_to_location)-1)


        fromLocation = random_from_location[random_index_from]
        toLocation = random_to_location[random_index_to]
        fromDate = "2023-01-08"
        toDate = "2023-01-14"

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

        # call to get flight details from destination to origin
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

        resp = {"org": fromLocation, "dest": toLocation, "dest_flights": to_flight_list[0],
                "return_flights": from_flight_list[0]}
        return resp
    else:
        resp = Response('NOT FOUND', status=404,
                       content_type='text/plain')
    return resp


# create user
@app.route("/users_service/signup", methods=["POST"])
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

        # call to get flight details from destination to origin
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



@app.route('/users_service/get_saved_trips', methods=['POST'])
def get_saved_trips():
    if request.method == 'POST':
        # call the trips table to query the list of trip_id for this user
        trips = UserResource.get_saved_trips(request.get_json()['user_id'])

        # iterate over trips and call itenerary service by each trip id
        saved_trips = []
        for t in trips:
            print("trip_id", t['trip_id'])
            req = str(itenerary_url + '/itenerary_service/get_trip?itenerary_id=' + str(t['trip_id']))
            response = requests.request('GET', req)
            saved_trips.append(response.json())

        # rsp = Response(json.dumps(result), status=200, content_type="application.json")
    else:
        saved_trips = Response("NOT FOUND", status=404, content_type="text/plain")
    return saved_trips


if __name__ == "__main__":
    app.debug = True
    app.run(host="0.0.0.0", port=5005)
