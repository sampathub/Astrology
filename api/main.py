from flask import Flask, request, jsonify
from flask_cors import CORS
import math

app = Flask(__name__)
CORS(app)

ZODIAC_SIGNS = ["Mesha", "Vrushaba", "Mithuna", "Kataka", "Sinha", "Kanya", 
                "Thula", "Vrushchika", "Dhanu", "Makara", "Kumbha", "Meena"]

NAKSHATRAS = [
    "Ashwini", "Bharani", "Krithika", "Rohini", "Mrigashira", "Arudra", 
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni", 
    "Hastha", "Chitra", "Swathi", "Vishaka", "Anuradha", "Jyeshtha", 
    "Moola", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha", 
    "Purva Bhadrapada", "Uttara Ashadha", "Revati"
]

def get_julian_date(y, m, d, h, mi):
    if m <= 2:
        y -= 1
        m += 12
    a = math.floor(y / 100)
    b = 2 - a + math.floor(a / 4)
    jd = math.floor(365.25 * (y + 4716)) + math.floor(30.6001 * (m + 1)) + d + b - 1524.5
    jd += (h + mi / 60.0) / 24.0
    return jd

def calculate_astrology_logic(jd, lon):
    # Time T in Julian centuries from J2000.0
    t = (jd - 2451545.0) / 36525.0
    
    # 1. Ayanamsa (Lahiri) - Approx
    ayanamsa = 23.0 + (51.0 / 60.0) + (t * 50.3 / 3600.0)
    
    # 2. Moon's Longitude (Simplified Theory of Moon)
    # Mean longitude of Moon
    l_prime = 218.3164477 + 481267.8812307 * t
    # Mean elongation of Moon
    d_moon = 297.8501921 + 445267.1114034 * t
    # Mean anomaly of Sun
    m_sun = 357.5291092 + 35999.0502909 * t
    # Mean anomaly of Moon
    m_prime = 134.9633964 + 477198.8675055 * t
    
    # Major corrections
    moon_long = l_prime + 6.289 * math.sin(math.radians(m_prime)) \
                - 1.274 * math.sin(math.radians(m_prime - 2 * d_moon)) \
                + 0.658 * math.sin(math.radians(2 * d_moon)) \
                + 0.214 * math.sin(math.radians(2 * m_prime))
    
    # Sidereal Moon Position
    sid_moon = (moon_long - ayanamsa) % 360
    
    # 3. Ascendant (Lagnaya)
    # Local Sidereal Time
    gmst = 280.46061837 + 360.98564736629 * (jd - 2451545.0)
    lst = (gmst + lon) % 360
    sid_asc = (lst - ayanamsa) % 360
    
    return sid_asc, sid_moon

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

        # UTC Correction (GMT+5.5)
        utc_h = h - 5
        utc_m = mi - 30
        if utc_m < 0:
            utc_m += 60
            utc_h -= 1
        
        jd = get_julian_date(y, m, d, utc_h, utc_m)
        asc_deg, moon_deg = calculate_astrology_logic(jd, lon)
        
        lagnaya = ZODIAC_SIGNS[int(asc_deg / 30)]
        nak_idx = int(moon_deg / (360/27))
        nakshata = NAKSHATRAS[nak_idx % 27]

        return jsonify({
            "lagnaya": lagnaya,
            "nakshata": nakshata,
            "debug": {"utc_date": f"{y}-{m}-{d}", "asc": round(asc_deg, 2)},
            "status": "success"
        })
    except Exception as e:
        return jsonify({"error": str(e), "status": "failed"})

app = app
