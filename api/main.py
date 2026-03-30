from flask import Flask, request, jsonify
from flask_cors import CORS
import swisseph as swe

app = Flask(__name__)
CORS(app) # වෙනත් origin එකක සිට එන requests වලට ඉඩ ලබා දීම

@app.route('/calculate', methods=['GET'])
def calculate():
    try:
        # URL එකෙන් දත්ත ලබා ගැනීම
        y = int(request.args.get('year'))
        m = int(request.args.get('month'))
        d = int(request.args.get('day'))
        h = int(request.args.get('hour'))
        min = int(request.args.get('min'))
        lat = float(request.args.get('lat'))
        lon = float(request.args.get('lon'))

        # UTC වලට හැරවීම (ලංකාවේ වේලාවෙන් 5.5 ක් අඩු කරයි)
        utc_time = h + (min / 60.0) - 5.5
        jd = swe.julday(y, m, d, utc_time)
        
        # ලාහිරි අයනංශය භාවිතයෙන් නිවැරදි ගණනය කිරීම
        swe.set_sid_mode(swe.SIDM_LAHIRI)
        
        # ලග්නය ගණනය කිරීම
        res, ascmc = swe.houses_ex(jd, lat, lon, b'P', flag=swe.FLG_SIDEREAL)
        
        zodiac_signs = ["Mesha", "Vrushaba", "Mithuna", "Kataka", "Sinha", "Kanya", 
                        "Thula", "Vrushchika", "Dhanu", "Makara", "Kumbha", "Meena"]
        
        lagnaya = zodiac_signs[int(ascmc[0] / 30)]
        
        return jsonify({"lagnaya": lagnaya, "status": "success"})
    except Exception as e:
        return jsonify({"error": str(e), "status": "failed"})

# Vercel සඳහා අවශ්‍ය වන කොටස
if __name__ == "__main__":
    app.run()
