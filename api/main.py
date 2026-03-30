from flask import Flask, request, jsonify
from flask_cors import CORS
import swisseph as swe

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

        # --- Manual UTC Correction ---
        # ලංකාවේ වේලාවෙන් 5:30 ක් අඩු කිරීම
        decimal_hour = h + (mi / 60.0)
        utc_hour = decimal_hour - 5.5
        
        target_year, target_month, target_day = y, m, d
        
        # වේලාව සෘණ වුවහොත් පෙර දිනයට යාම
        if utc_hour < 0:
            utc_hour += 24
            d -= 1
            if d < 1: # මාසය මාරු වන අවස්ථාවකදී (උදා: අප්‍රේල් 1 සිට මාර්තු 31 ට)
                m -= 1
                if m < 1:
                    y -= 1
                    m = 12
                # මාසයේ දින ගණන තීරණය කිරීම (සරලව)
                if m in [4, 6, 9, 11]: d = 30
                elif m == 2: d = 29 if (y % 4 == 0) else 28
                else: d = 31
            target_year, target_month, target_day = y, m, d

        # Julian Day ගණනය කිරීම
        jd_ut = swe.julday(target_year, target_month, target_day, utc_hour)
        
        # ලාහිරි අයනංශය (Lahiri Ayanamsa)
        swe.set_sid_mode(swe.SIDM_LAHIRI)
        
        # 1. ලග්නය (Ascendant) - 64 = FLG_SIDEREAL
        # 'O' = Porphyrius, ලංකාවේ ජ්‍යොතිෂයට වඩාත් ගැලපේ
        res, ascmc = swe.houses_ex(jd_ut, lat, lon, b'O', 64)
        zodiac_signs = ["Mesha", "Vrushaba", "Mithuna", "Kataka", "Sinha", "Kanya", 
                        "Thula", "Vrushchika", "Dhanu", "Makara", "Kumbha", "Meena"]
        
        ascendant_deg = ascmc[0]
        lagnaya = zodiac_signs[int(ascendant_deg / 30)]

        # 2. නැකත (Moon)
        moon_pos, retire = swe.calc_ut(jd_ut, 1, 64)
        moon_deg = moon_pos[0]
        nakshatra_idx = int(moon_deg / (360 / 27))
        nakshata = NAKSHATRAS[nakshatra_idx % 27]
        
        return jsonify({
            "lagnaya": lagnaya,
            "nakshata": nakshata,
            "debug": {"utc_date": f"{target_year}-{target_month}-{target_day}", "utc_hour": utc_hour},
            "status": "success"
        })
    except Exception as e:
        return jsonify({"error": str(e), "status": "failed"})

app = app
