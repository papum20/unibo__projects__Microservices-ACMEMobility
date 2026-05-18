def get_route_from_graphhopper(start_latlon, end_latlon):
    # Ask Graphhopper for the route. 'points_encoded=false' gives us raw GPS arrays!
    url = f"http://graphhopper:8989/route?point={start_latlon}&point={end_latlon}&vehicle=car&points_encoded=false"
    
    response = requests.get(url)
    data = response.json()
    
    # Graphhopper returns coordinates as [longitude, latitude]
    coordinates = data["paths"][0]["points"]["coordinates"]
    
    # We return the list of points so the simulator can iterate over them
    return coordinates
