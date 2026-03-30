from flask import Flask, request, jsonify
from flask_cors import CORS  # මේ පේළිය අලුතින් එකතු කරන්න
import swisseph as swe

app = Flask(__name__)
CORS(app)  # මේ පේළියත් අලුතින් එකතු කරන්න. එවිට CORS Error එක නැති වේ.

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

        utc_time = h + (min / 60.0) - 5.5
        jd = swe.julday(y, m, d, utc_time)
        swe.set_sid_mode(swe.SIDM_LAHIRI)
        res, ascmc = swe.houses_ex(jd, lat, lon, b'P', flag=swe.FLG_SIDEREAL)
        
        zodiac_signs = ["Mesha", "Vrushaba", "Mithuna", "Kataka", "Sinha", "Kanya", 
                        "Thula", "Vrushchika", "Dhanu", "Makara", "Kumbha", "Meena"]
        
        lagnaya = zodiac_signs[int(ascmc[0] / 30)]
        
        return jsonify({"lagnaya": lagnaya, "status": "success"})
    except Exception as e:
        return jsonify({"error": str(e), "status": "failed"})

if __name__ == '__main__':
    app.run()
