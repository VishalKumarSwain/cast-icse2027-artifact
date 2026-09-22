def create_feature(message, liked):
    feature = {
        "properties": {
            "id": message["id"],
            "text": message["text"],
            "liked": liked,
            "country": message["country"],
            "city": message["city"],
            "state": message["state"],
        },
        "geometry": {
            "type": "Point",
            "coordinates": [message["longitude"], message["latitude"]],
        },
    }
    return feature
