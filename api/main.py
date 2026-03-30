from flask import Flask, request, jsonify
from flask_cors import CORS
import swisseph as swe
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

NAKSHATRAS = [
    "Ashwini", "Bharani", "Krithika", "Rohini", "Mrigashira", "Arudra", 
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni", 
    "Hastha", "Chitra", "Swathi", "Vishaka", "Anuradha", "Jyeshtha", 
    "Moola", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha", 
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

@app.route('/calculate', methods=['GET'])
def calculate():
    try:
        y = int(request.args.get('year'))
        m = int(request.args.get('month'))
        d = int(request.args.get('day'))
        h = int(request.args.get('hour'))
        mi = int(request.args.get('min'))
        lat = float(request.args.get('lat'))
        lon = float(request.args.get('lon'))

        # --- නිවැරදි UTC ගණනය කිරීම ---
        # ලංකාවේ වේලාවෙන් පැය 5 මිනිත්තු 30 ක් අඩු කිරීම
        local_dt = datetime(y, m, d, h, mi)
        utc_dt = local_dt - timedelta(hours=5, minutes=30)
        
        # UTC දිනය සහ වේලාව ලබා ගැනීම
        jd_ut = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, 
                           utc_dt.hour + utc_dt.minute/60.0 + utc_dt.second/3600.0)
        
        swe.set_sid_mode(swe.SIDM_LAHIRI)
        
        # 1. ලග්නය ගණනය කිරීම
        # 64 = FLG_SIDEREAL
        res, ascmc = swe.houses_ex(jd_ut, lat, lon, b'O', 64)
        zodiac_signs = ["Mesha", "Vrushaba", "Mithuna", "Kataka", "Sinha", "Kanya", 
                        "Thula", "Vrushchika", "Dhanu", "Makara", "Kumbha", "Meena"]
        
        # ධනු රාශිය (Dhanu) අංශක 240 සිට 270 දක්වා වේ.
        lagnaya = zodiac_signs[int(ascmc[0] / 30)]

        # 2. නැකත ගණනය කිරීම
        moon_pos, retire = swe.calc_ut(jd_ut, 1, 64)
        moon_degree = moon_pos[0]
        
        nakshatra_index = int(moon_degree / (360 / 27))
        nakshata = NAKSHATRAS[nakshatra_index % 27]
        
        return jsonify({
            "lagnaya": lagnaya,
            "nakshata": nakshata,
            "status": "success"
        })
    except Exception as e:
        return jsonify({"error": str(e), "status": "failed"})

app = app
