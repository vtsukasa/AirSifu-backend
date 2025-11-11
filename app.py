from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import json
import os
import requests

app = Flask(__name__)
CORS(app)  # Enable CORS so your GoDaddy frontend can access this API

# --- CONFIGURATION ---
OPENWEATHER_API_KEY = "34fa89d91d947206c79c465555c4b954"

# Make sure Render finds the right paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROUTE_FILE = os.path.join(BASE_DIR, 'data', 'routes.json')
AIRPORTS_FILE = os.path.join(BASE_DIR, 'data', 'airports.json')


# --- HELPER FUNCTIONS ---
def load_json(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return json.load(file)
    return {}


def get_weather(lat, lon):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        return {
            "temperature": data["main"]["temp"],
            "weather": data["weather"][0]["description"],
            "wind_speed": data["wind"]["speed"],
            "humidity": data["main"]["humidity"]
        }
    else:
        return {"error": "Weather data not available"}


# --- ROUTES ---
@app.route('/')
def home():
    return jsonify({"status": "AirSifu backend is live!"})


@app.route('/get_route', methods=['GET'])
def get_route():
    departure = request.args.get('departure')
    destination = request.args.get('destination')

    if not departure or not destination:
        return jsonify({"error": "Missing departure or destination"}), 400

    airports = load_json(AIRPORTS_FILE)
    routes = load_json(ROUTE_FILE)

    if departure not in airports or destination not in airports:
        return jsonify({"error": "Invalid airport code"}), 400

    route_key = f"{departure}-{destination}"
    if route_key not in routes:
        return jsonify({"error": "Route not found"}), 404

    dep_coords = airports[departure]
    dest_coords = airports[destination]

    dep_weather = get_weather(dep_coords["lat"], dep_coords["lon"])
    dest_weather = get_weather(dest_coords["lat"], dest_coords["lon"])

    return jsonify({
        "departure": {"lat": dep_coords["lat"], "lon": dep_coords["lon"], "name": departure},
        "destination": {"lat": dest_coords["lat"], "lon": dest_coords["lon"], "name": destination},
        "departure_weather": dep_weather,
        "destination_weather": dest_weather,
        "distance_km": routes[route_key]["distance_km"],
        "flight_time_hours": routes[route_key]["flight_time_hours"]
    })


# --- MAIN ENTRY POINT ---
if __name__ == '__main__':
    # Run on all interfaces for Render
    app.run(host='0.0.0.0', port=5000)
