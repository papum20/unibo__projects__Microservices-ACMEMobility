import math

# Earth radius in km
EARTH_R_KM = 6371.0

# Haversine formula works for a sphere, so this is an approximation, but good enough
def coord_distance_km(lat1, lon1, lat2, lon2):

    # Convert degrees to radians
    phi1, phi2	= math.radians(lat1), math.radians(lat2)
    dphi		= math.radians(lat2 - lat1)
    dlambda		= math.radians(lon2 - lon1)

    # Haversine formula
    a = math.sin(dphi / 2)**2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2)**2
    
    c = 2 * math.asin(math.sqrt(a))
    return EARTH_R_KM * c