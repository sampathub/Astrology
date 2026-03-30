from flask import Flask, request, jsonify
from flask_cors import CORS
import swisseph as swe

app = Flask(__name__)
CORS(app)

@app.route('/calculate', methods=['GET'])
def calculate():
    try:
        y = int(request.args.get('year'))
        m = int(request.args.get('month'))
        d = int(request.args.get('day'))
        h = int(request.args.get('hour'))
        min_val = int(request.args.get('min'))
        lat = float(request.args.get('lat'))
        lon = float(request.args.get('lon'))

        # 1. නිවැරදි UTC Offset එක (GMT +5.5)
        decimal_hour = h + (min_val / 60.0) - 5.5
        jd_ut = swe.julday(y, m, d, decimal_hour)

        # 2. Topocentric (උපන් ස්ථානයට අනුව) සැකසුම් - වඩාත් නිවැරදි වීමට
        swe.set_topo(lon, lat, 0) 

        # 3. Sidereal Mode එක Lahiri (True) ලෙස සැකසීම
        swe.set_sid_mode(swe.SIDM_LAHIRI)

        # 4. ලග්නය ගණනය කිරීම (Ascendant)
        # 64 = FLG_SIDEREAL, 256 = FLG_JPLEPH (NASA Data precision)
        flags = swe.FLG_SIDEREAL
        res, ascmc = swe.houses_ex(jd_ut, lat, lon, b'P', flags)

        zodiac_signs = ["Mesha", "Vrushaba", "Mithuna", "Kataka", "Sinha", "Kanya", 
                        "Thula", "Vrushchika", "Dhanu", "Makara", "Kumbha", "Meena"]

        ascendant = ascmc[0]
        lagnaya_index = int(ascendant / 30)
        lagnaya = zodiac_signs[lagnaya_index]

        return jsonify({
            "lagnaya": lagnaya,
            "ascendant_degree": ascendant,
            "status": "success"
        })
    except Exception as e:
        return jsonify({"error": str(e), "status": "failed"})

app = app
