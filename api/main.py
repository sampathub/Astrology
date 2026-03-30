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
        min = int(request.args.get('min'))
        lat = float(request.args.get('lat'))
        lon = float(request.args.get('lon'))

        # UTC Time calculation
        utc_time = h + (min / 60.0) - 5.5
        jd = swe.julday(y, m, d, utc_time)
        
        swe.set_sid_mode(swe.SIDM_LAHIRI)
        
        # 'flag' ඉවත් කර සෘජුවම FLG_SIDEREAL ලබා දීම
        res, ascmc = swe.houses_ex(jd, lat, lon, b'P', swe.FLG_SIDEREAL)
        
        zodiac_signs = ["Mesha", "Vrushaba", "Mithuna", "Kataka", "Sinha", "Kanya", 
                        "Thula", "Vrushchika", "Dhanu", "Makara", "Kumbha", "Meena"]
        
        lagnaya = zodiac_signs[int(ascmc[0] / 30)]
        
        return jsonify({"lagnaya": lagnaya, "status": "success"})
    except Exception as e:
        return jsonify({"error": str(e), "status": "failed"})

# Vercel සඳහා අත්‍යවශ්‍යයි
app = app
