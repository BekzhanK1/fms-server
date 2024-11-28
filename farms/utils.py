from geopy.distance import geodesic


def calculate_distance(user_location, farm_location):
    """
    Calculate the distance between two points.
    :param user_location: Tuple (latitude, longitude) of the user.
    :param farm_location: Tuple (latitude, longitude) of the farm.
    :return: Distance in kilometers.
    """
    return geodesic(user_location, farm_location).km
