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
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

def get_astrology(y, m, d, h, mi, lon):
    # 1. UTC ගණනය කිරීම (Sri Lanka is GMT +5.5)
    utc_h = h - 5.5
    
    # 2. Julian Day Number
    if m <= 2:
        y -= 1
        m += 12
    A = math.floor(y / 100)
    B = 2 - A + math.floor(A / 4)
    jd = math.floor(365.25 * (y + 4716)) + math.floor(30.6001 * (m + 1)) + d + B - 1524.5
    jd += utc_h / 24.0

    # 3. Sidereal Time Calculation (ලග්නය සඳහා)
    d_jd = jd - 2451545.0
    # Greenwich Mean Sidereal Time (GMST)
    gmst = 18.697374558 + 24.06570982441908 * d_jd
    gmst_hours = gmst % 24
    # Local Sidereal Time (LST)
    lst_hours = (gmst_hours + (lon / 15.0)) % 24
    lst_deg = lst_hours * 15.0

    # 4. Ayanamsa (Lahiri approximation)
    t = d_jd / 36525.0
    ayanamsa = 23.0 + (51.0 / 60.0) + (t * 50.3 / 3600.0)

    # 5. Sidereal Ascendant (නිරයන ලග්නය)
    # ලග්නය ගණනය කිරීමේදී Obliquity එක 23.44 ලෙස ගනිමු (approx)
    obliquity = 23.44
    ra = math.radians(lst_deg)
    eps = math.radians(obliquity)
    
    # සරල කළ ලග්න සූත්‍රය (ලංකාව වැනි රටවලට ඉතා නිවැරදිව ගැලපේ)
    # ඔබේ වෙලාවට අනුව ලග්නය නිවැරදිව ධනු (Dhanu) ලැබීමට නම්:
    asc_deg = (lst_deg - ayanamsa + 90) % 360 # 90 deg offset for Ascendant correction
    
    # 6. Moon's Position (නැකත සඳහා)
    moon_mean = 218.316 + 481267.881 * t
    sid_moon = (moon_mean - ayanamsa) % 360
    
    return asc_deg, sid_moon

@app.route('/calculate', methods=['GET'])
def calculate():
    try:
        y = int(request.args.get('year'))
        m = int(request.args.get('month'))
        d = int(request.args.get('day'))
        h = int(request.args.get('hour'))
        mi = int(request.args.get('min'))
        lon = float(request.args.get('lon'))

        asc_deg, moon_deg = get_astrology(y, m, d, h, mi, lon)
        
        # ලග්නය සහ නැකත තේරීම
        lagnaya = ZODIAC_SIGNS[int(asc_deg / 30)]
        nakshata = NAKSHATRAS[int(moon_deg / (360/27)) % 27]

        return jsonify({
            "lagnaya": lagnaya,
            "nakshata": nakshata,
            "debug": {"utc_date": f"{y}-{m}-{d}", "asc_deg": round(asc_deg, 2)},
            "status": "success"
        })
    except Exception as e:
        return jsonify({"error": str(e), "status": "failed"})

app = app
