''' Goal is to have a bot that can search for all businesses of as
specific type (eg restaurant, cafe, bar) within a radius of ___ miles
from an input address. Want to return business name, type, address,
phone #, email, review rating, etc.'''

from flask import Flask, render_template, jsonify, request, make_response
import requests
import io
import csv

key = 'AIzaSyD5CCUlbq7cUYc3fOTBb6NNCPr2Lr_18NE'
app = Flask(__name__)

# search_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
# base gooogle places 'nearby search' URL https://maps.googleapis.com/maps/api/place/nearbysearch/output?parameters
search_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
#will need to find details of the places returned by the search_url request
details_url = "https://maps.googleapis.com/maps/api/place/details/json"
geocode_url = "https://maps.googleapis.com/maps/api/geocode/json"


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/", methods=['POST'])
def address():
        address = request.form['address']
        radius = request.form['radius']
        output = results(address, radius)
        to_csv = io.StringIO()
        to_dwnld = csv.writer(to_csv)
        to_dwnld.writerows(output)
        out = make_response(to_csv.getvalue())
        out.headers["Content-Disposition"] = "attachment; filename=EW-LocatorList.csv"
        out.headers["Content-type"] = "text/csv"
        return out


''' for nearby searches the following input is required:
key, location (in the form of 'latitude, longitude'), radius '''

def geocode(address):
    geocode_payload = {"key":key, "address":address}
    geocode_req = requests.get(geocode_url, params=geocode_payload)
    geocode_json=geocode_req.json()
    loc = [geocode_json["results"][0]["geometry"]["location"]["lat"], geocode_json["results"][0]["geometry"]["location"]["lng"]]
    return loc

def results(address, radius):
    geocode_payload = {"key":key, "address":address}
    geocode_req = requests.get(geocode_url, params=geocode_payload)
    geocode_json=geocode_req.json()
    location = str(geocode_json["results"][0]["geometry"]["location"]["lat"]) + ',' + str(geocode_json["results"][0]["geometry"]["location"]["lng"])

    m_radius = float(radius) * 1609.34
    details_list = []
    options = []
    types = ['bar', 'cafe', 'restaurant', 'meal_takeaway', 'meal_delivery', 'bakery', 'lodging', 'pharmacy', 'night_club']

    for item in types:
        search_payload = {"key":key, "location":location, "radius":m_radius, "type":item}
        search_req = requests.get(search_url, params=search_payload)
        search_json = search_req.json()
        pid = [search_json["results"][i]["place_id"] for i in range(len(search_json["results"]))]
        options = options + pid

    for i in options:
        details_payload = {"key":key, "place_id":i}
        details_req = requests.get(details_url, params=details_payload)
        details_json = details_req.json()
        d_info = []
        headers = ['Name', 'Rating', 'Phone Number', 'Wesbite', 'Address']
        try:
            d_info.append(details_json["result"]["name"])
        except:
            d_info.append('null')
        try:
            d_info.append(details_json["result"]["rating"])
        except:
            d_info.append('null')
        try:
            d_info.append(details_json["result"]["formatted_phone_number"])
        except:
            d_info.append('null')
        try:
            d_info.append(details_json["result"]["website"])
        except:
            d_info.append('null')
        try:
            d_info.append(details_json["result"]["formatted_address"])
        except:
            d_info.append('null')
        try:
            d_info.append(details_json["result"]["types"])
        except:
            d_info.append('null')
        details_list.append(d_info)

    return details_list


if __name__ == '__main__':
    app.run(debug=True)
