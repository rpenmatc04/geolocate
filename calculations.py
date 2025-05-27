from shapely import distance
from shapely.ops import nearest_points 
from shapely import Polygon
from shapely import Point
from geopy.distance import geodesic
from config import LOW_LEVEL, MID_LEVEL

# Construct a Polygon for each boundary for this client
# Create a Point object for the current coordinate
def generate_structures(pointVals, polygonVals):
    polygon = [Polygon(coordinates) for coordinates in polygonVals] 
    point = Point(pointVals[0], pointVals[1]) 
    return polygon, point

# Calculate the closest distance between a point and a polygon
def calculate_distance(point, polygon): 
    return distance(polygon, point)

# Calculate minimum distance between a point and polygon(s) 
def calculate_min_distance(point, polygon):
    if type(polygon) == list: 
        closest_distance = calculate_distance(point, polygon[0])
        closest_index = 0
        for itr in range(1, len(polygon)):
            dist = calculate_distance(point, polygon[itr])
            if closest_distance > dist:
                closest_index = itr 
                closest_distance = dist
        return closest_distance, nearest_points(polygon[closest_index], point)[0]
    else: 
        return nearest_points(polygon, point)

# Checks if any polygon covers point
def covers(point, polygon):
    if any(polygon_options.covers(point) for polygon_options in polygon): 
        return "IN"
    else: 
        return "OUT"

# Returns whether the point is in the polygon or not, their distance, and the closest point
def cover_information(point, polygon): 
    distance, closest_point = calculate_min_distance(point, polygon)
    if distance == 0.0: 
        decision = "IN"
    else: 
        decision = "OUT"
        distance = geodesic((point.y, point.x),(closest_point.y, closest_point.x)).miles # Miles

    return decision, distance, closest_point

# Alert-Level based on distance
def calculate_level(distance): 
    level = ""
    if distance < LOW_LEVEL: 
        level = "Low"
    elif distance < MID_LEVEL: 
        level = "Mid"
    else: 
        level = "High"
    return level