from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import requests
from dotenv import load_dotenv

# Load .env variables (local dev)
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# OpenWeather API key from environment
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

# ------------------ ROUTES ------------------

@app.route('/')
def home():
    return jsonify({
        "status": "AirSifu backend is live!",
        "routes": [
            "/api/flights  →  Live aircraft data from OpenSky",
            "/api/weather?city=Kuching  →  Current weather data from OpenWeather"
        ]
    })


@app.route('/api/flights', methods=['GET'])
def get_flights():
    """
    Fetch live aircraft states from OpenSky Network.
    No authentication required.
    """
    try:
        url = "https://opensky-network.org/api/states/all"
        response = requests.get(url)
        data = response.json()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/weather', methods=['GET'])
def get_weather():
    """
    Fetch weather data for a given city or coordinates.
    Example call: /api/weather?city=Kuching
    """
    city = request.args.get('city')
    lat = request.args.get('lat')
    lon = request.args.get('lon')

    if not OPENWEATHER_API_KEY:
        return jsonify({"error": "Missing OpenWeather API key"}), 500

    try:
        if city:
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
        elif lat and lon:
            url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric"
        else:
            return jsonify({"error": "Provide city or coordinates"}), 400

        response = requests.get(url)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ------------------ RUN SERVER ------------------
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
