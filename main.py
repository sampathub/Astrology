from flask import Flask, request, jsonify
import swisseph as swe

app = Flask(__name__)

@app.route('/calculate', methods=['GET'])
def calculate():
    # URL එකෙන් දත්ත ලබා ගැනීම
    try:
        y = int(request.args.get('year'))
        m = int(request.args.get('month'))
        d = int(request.args.get('day'))
        h = int(request.args.get('hour'))
        min = int(request.args.get('min'))
        lat = float(request.args.get('lat'))
        lon = float(request.args.get('lon'))

        # UTC වලට හැරවීම (ලංකාව නිසා 5.5 ක් අඩු කරනවා)
        utc_time = h + (min / 60.0) - 5.5
        jd = swe.julday(y, m, d, utc_time)
        
        swe.set_sid_mode(swe.SIDM_LAHIRI)
        
        # ලග්නය ගණනය කිරීම
        res, ascmc = swe.houses_ex(jd, lat, lon, b'P', flag=swe.FLG_SIDEREAL)
        asc_deg = ascmc[0]
        
        zodiac_signs = ["Mesha", "Vrushaba", "Mithuna", "Kataka", "Sinha", "Kanya", 
                        "Thula", "Vrushchika", "Dhanu", "Makara", "Kumbha", "Meena"]
        
        lagnaya = zodiac_signs[int(asc_deg / 30)]
        
        return jsonify({"lagnaya": lagnaya, "status": "success"})
    except Exception as e:
        return jsonify({"error": str(e), "status": "failed"})

if __name__ == '__main__':
    app.run()