from geopy.distance import geodesic
from datetime import datetime

def calculate_distance(user_location,row):
    lat = row["lat"]
    lng = row["lng"]
    spot_location =(lat,lng)
    dis= geodesic(user_location,spot_location).km
    return round(dis,2)



def is_open_spot(row):
    current_time= datetime.now().strftime("%H:%M")
    open_time=row["opening_time"]
    close_time=row["closing_time"]
    if open_time <= current_time <= close_time:
        return "open"
    else:
        return "closed"
    
def get_spot_icon(spot_type):
    icons=["🏠","🛒","🚚"]
    if spot_type == "cafe":
       return icons[0]
    elif spot_type == "cart":
        return icons[1]
    else:
       return icons[2]

