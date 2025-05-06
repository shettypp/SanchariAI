import pandas as pd
import math
import re

# Helper to clean coordinates like "13.1663° N" or with invisible characters
def clean_coordinate(coord):
    if isinstance(coord, str):
        coord = re.sub(r'[^\d.\-]', '', coord)  # Remove all non-digit, non-dot, non-negative characters
    return float(coord)

# Haversine formula to calculate distance between two lat/lon points (in km)
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

# Load dataset
df = pd.read_csv('places.csv')

# Clean coordinates
df['Latitude'] = df['Latitude'].apply(clean_coordinate)
df['Longitude'] = df['Longitude'].apply(clean_coordinate)

# Simple name-to-location map (you can expand this or make it smarter)
location_coords = {str(name).strip().lower(): (lat, lon) for name, lat, lon in zip(df['Name'], df['Latitude'], df['Longitude']) if pd.notnull(name)}

# Get user input
start_place = input("Enter your starting location (e.g., Bengaluru): ").strip().lower()
end_place = input("Enter your destination (e.g., Mysuru): ").strip().lower()

# Lookup coordinates
def find_place_coords(place_name):
    for name, lat, lon, address in zip(df['Name'], df['Latitude'], df['Longitude'], df['Address']):
        # Match place name in Name column
        if place_name in str(name).lower():
            return lat, lon
        # Match place name in Address column (if Name doesn't match)
        if place_name in str(address).lower():
            return lat, lon
    return None


start_coords = find_place_coords(start_place)
end_coords = find_place_coords(end_place)

if not start_coords or not end_coords:
    print("❌ Start or destination not found in dataset.")
    exit()

start_lat, start_lon = start_coords
end_lat, end_lon = end_coords

start_lat, start_lon = location_coords[start_place]
end_lat, end_lon = location_coords[end_place]

# Define nearby range (km)
RANGE_NEARBY = 10  # You can change this
places_on_route = []
places_nearby_dest = []

# Check all places
for _, row in df.iterrows():
    place_name = row['Name']
    plat = row['Latitude']
    plon = row['Longitude']

    dist_to_start = haversine(start_lat, start_lon, plat, plon)
    dist_to_end = haversine(end_lat, end_lon, plat, plon)

    # Near destination
    if dist_to_end <= RANGE_NEARBY:
        places_nearby_dest.append((place_name, round(dist_to_end, 2)))

    # Along route (within 20 km buffer from midpoint)
    total_trip = haversine(start_lat, start_lon, end_lat, end_lon)
    dist_from_mid = haversine((start_lat + end_lat)/2, (start_lon + end_lon)/2, plat, plon)
    if dist_from_mid < total_trip / 2:
        places_on_route.append((place_name, round(dist_from_mid, 2)))

# Output
print("\n📍 Places near your destination:")
for name, dist in places_nearby_dest:
    print(f"  - {name} ({dist} km from destination)")

print("\n🚗 Places along the route:")
for name, dist in places_on_route:
    print(f"  - {name} ({dist} km from midpoint of route)")
