from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import requests
from dotenv import load_dotenv

# Load environment variables (for local dev)
load_dotenv()

app = Flask(__name__)
CORS(app)  # ✅ Enable CORS for all routes (can be limited to specific origins if needed)

# Load your OpenWeather API key from environment
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

# ---------- ROUTE 1: GET FLIGHT DATA FROM OPENSKY ----------
@app.route('/api/flights', methods=['GET'])
def get_flights():
    import requests
    try:
        url = "https://opensky-network.org/api/states/all"
        response = requests.get(url)
        return response.json()
    except Exception as e:
        return {"error": str(e)}, 500


# ---------- ROUTE 2: GET WEATHER DATA FROM OPENWEATHER ----------
@app.route('/api/weather', methods=['GET'])
def get_weather():
    """
    Fetch weather data for a given city or coordinates.
    Example frontend call: /api/weather?city=Kuching
    or /api/weather?lat=1.5&lon=110.3
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
            return jsonify({"error": "Please provide city or coordinates"}), 400

        response = requests.get(url)
        data = response.json()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------- ROOT ROUTE ----------
@app.route('/')
def home():
    return jsonify({
        "message": "AirSifu Backend API is running",
        "routes": ["/api/flights", "/api/weather"]
    })


# ---------- START SERVER ----------
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
