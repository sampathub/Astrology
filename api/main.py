from flask import Flask, request, jsonify
from flask_cors import CORS
import math

app = Flask(__name__)
CORS(app)

# ලග්න සහ නැකත් ලැයිස්තු
ZODIAC_SIGNS = ["Mesha", "Vrushaba", "Mithuna", "Kataka", "Sinha", "Kanya", 
                "Thula", "Vrushchika", "Dhanu", "Makara", "Kumbha", "Meena"]

NAKSHATRAS = [
    "Ashwini", "Bharani", "Krithika", "Rohini", "Mrigashira", "Arudra", 
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni", 
    "Hastha", "Chitra", "Swathi", "Vishaka", "Anuradha", "Jyeshtha", 
    "Moola", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha", 
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

def calculate_jd(y, m, d, h, mi):
    if m <= 2:
        y -= 1
        m += 12
    A = math.floor(y / 100)
    B = 2 - A + math.floor(A / 4)
    jd = math.floor(365.25 * (y + 4716)) + math.floor(30.6001 * (m + 1)) + d + B - 1524.5
    jd += (h + mi / 60.0) / 24.0
    return jd

def get_moon_long(jd):
    # චන්ද්‍රයාගේ දළ පිහිටීම ගණනය කිරීම (Simplified lunar theory)
    T = (jd - 2451545.0) / 36525.0
    L0 = 218.316 + 481267.881 * T
    # Lahiri Ayanamsa (දළ වශයෙන්)
    ayanamsa = 23.0 + (51.0 / 60.0) + (T * 50.3 / 3600.0)
    moon_long = (L0 - ayanamsa) % 360
    return moon_long

def get_ascendant(jd, lat, lon):
    # ලග්නය ගණනය කිරීම (Sidereal Time based)
    T = (jd - 2451545.0) / 36525.0
    # Greenwich Mean Sidereal Time
    gmst = 280.46061837 + 360.98564736629 * (jd - 2451545.0) + 0.000387933 * T**2
    lst = (gmst + lon) % 360
    
    # Sidereal to Tropical adjustment (Ayanamsa)
    ayanamsa = 23.0 + (51.0 / 60.0) + (T * 50.3 / 3600.0)
    # සරල කළ ලග්න ගණනය කිරීම
    asc = (lst - ayanamsa) % 360
    return asc

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

        # 1. UTC Offset Correction (GMT +5.5)
        utc_h = h - 5
        utc_m = mi - 30
        if utc_m < 0:
            utc_m += 60
            utc_h -= 1
        
        jd = calculate_jd(y, m, d, utc_h, utc_m)
        
        # 2. ලග්නය (Ascendant)
        asc_deg = get_ascendant(jd, lat, lon)
        lagnaya = ZODIAC_SIGNS[int(asc_deg / 30)]
        
        # 3. නැකත (Moon Position)
        moon_deg = get_moon_long(jd)
        nak_idx = int(moon_deg / (360/27))
        nakshata = NAKSHATRAS[nak_idx % 27]

        return jsonify({
            "lagnaya": lagnaya,
            "nakshata": nakshata,
            "debug": {"utc_date": f"{y}-{m}-{d}", "jd": jd},
            "status": "success"
        })
    except Exception as e:
        return jsonify({"error": str(e), "status": "failed"})

app = app
