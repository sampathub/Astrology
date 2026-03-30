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

def get_julian_date(y, m, d, h, mi):
    if m <= 2:
        y -= 1
        m += 12
    a = math.floor(y / 100)
    b = 2 - a + math.floor(a / 4)
    jd = math.floor(365.25 * (y + 4716)) + math.floor(30.6001 * (m + 1)) + d + b - 1524.5
    # UTC වේලාව Julian Day එකට එකතු කිරීම
    jd += (h + mi / 60.0) / 24.0
    return jd

def calculate_astrology_logic(jd, lon, lat):
    # J2000.0 සිට සියවස් ගණන
    t = (jd - 2451545.0) / 36525.0
    
    # 1. Ayanamsa (Lahiri) - Approx 24 degrees for modern dates
    ayanamsa = 23.0 + (51.0 / 60.0) + (t * 50.3 / 3600.0)
    
    # 2. Local Sidereal Time (LST) - ලග්නය සඳහා මෙය තීරණාත්මකයි
    # Greenwich Mean Sidereal Time (GMST)
    gmst = 280.46061837 + 360.98564736629 * (jd - 2451545.0) + 0.000387933 * t**2
    lst = (gmst + lon) % 360
    
    # 3. Ascendant (ලග්නය) - සරල කළ නිවැරදි සූත්‍රය
    # ලංකාව වැනි සමකයට ආසන්න රටවලට මෙය ඉතා සමීපයි
    sid_asc = (lst - ayanamsa) % 360
    
    # 4. Moon's Longitude (නැකත සඳහා)
    l_prime = 218.316 + 481267.881 * t
    m_prime = 134.963 + 477198.867 * t
    d_moon = 297.850 + 445267.111 * t
    moon_long = l_prime + 6.289 * math.sin(math.radians(m_prime)) - 1.274 * math.sin(math.radians(m_prime - 2*d_moon))
    sid_moon = (moon_long - ayanamsa) % 360
    
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

        # ශ්‍රී ලංකා වේලාව (GMT+5.5) UTC වලට හැරවීම
        utc_total_mins = (h * 60 + mi) - 330
        utc_h = utc_total_mins // 60
        utc_m = utc_total_mins % 60
        
        # UTC වේලාව අනුව දින නිවැරදි කිරීම
        target_y, target_m, target_d = y, m, d
        if utc_h < 0:
            # පෙර දිනයට යාම අවශ්‍යයි (සරලව Julian Day එකම මෙය පාලනය කරයි)
            pass

        jd = get_julian_date(target_y, target_m, target_d, utc_h, utc_m)
        asc_deg, moon_deg = calculate_astrology_logic(jd, lon, lat)
        
        # ලග්නය තීරණය කිරීම (අංශක 30 බැගින්)
        lagnaya = ZODIAC_SIGNS[int(asc_deg / 30)]
        # නැකත තීරණය කිරීම (අංශක 13.33 බැගින්)
        nak_idx = int(moon_deg / (360/27))
        nakshata = NAKSHATRAS[nak_idx % 27]

        return jsonify({
            "lagnaya": lagnaya,
            "nakshata": nakshata,
            "debug": {"utc_date": f"{target_y}-{target_m}-{target_d}", "asc_deg": round(asc_deg, 2)},
            "status": "success"
        })
    except Exception as e:
        return jsonify({"error": str(e), "status": "failed"})

app = app
