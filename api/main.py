from flask import Flask, request, jsonify
from flask_cors import CORS
import swisseph as swe

app = Flask(__name__)
CORS(app)

# නැකත් 27 ක ලැයිස්තුව
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

        # UTC Offset (GMT +5.5)
        utc_hour = h + (mi / 60.0) - 5.5
        jd_ut = swe.julday(y, m, d, utc_hour)
        
        swe.set_sid_mode(swe.SIDM_LAHIRI)
        
        # 1. ලග්නය ගණනය කිරීම (Ascendant)
        res, ascmc = swe.houses_ex(jd_ut, lat, lon, b'O', 64)
        zodiac_signs = ["Mesha", "Vrushaba", "Mithuna", "Kataka", "Sinha", "Kanya", 
                        "Thula", "Vrushchika", "Dhanu", "Makara", "Kumbha", "Meena"]
        lagnaya = zodiac_signs[int(ascmc[0] / 30)]

        # 2. නැකත ගණනය කිරීම (Moon's position)
        # 1 යනු චන්ද්‍රයා (Moon) සඳහා වන අංකයයි
        moon_pos, retire = swe.calc_ut(jd_ut, 1, 64)
        moon_degree = moon_pos[0] # චන්ද්‍රයා සිටින අංශකය
        
        # නැකතක් අංශක 13.3333 කින් සමන්විත වේ (360 / 27)
        nakshatra_index = int(moon_degree / (360 / 27))
        nakshata = NAKSHATRAS[nakshatra_index]
        
        return jsonify({
            "lagnaya": lagnaya,
            "nakshata": nakshata,
            "status": "success"
        })
    except Exception as e:
        return jsonify({"error": str(e), "status": "failed"})

app = app
