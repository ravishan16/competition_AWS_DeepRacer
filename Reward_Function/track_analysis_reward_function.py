import math


# Racing line using Waypoints
def reward_function(params):
    left = [
        53,72,73,74,75
    ]
    centerleft = [1,2,3,4,5,6,7,8,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,43,44,45,46,47,48,49,50,51,52,54,55,56,57,58,59,60,61,62,68,69,70,71,76,92,93,94,101,102,103,104,105,106,121,123,124,125,126,127]
    centerright = [9,10,11,12,13,14,38,39,40,41,42,63,64,65,66,67,77,78,83,84,85,86,87,88,89,90,91,95,96,97,98,99,100,107,111,112,113,114,115,116,117,118,119,120,122]
    right = [79,80,81,82,108,109,110]

    fast = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,45,46,47,48,49,50,56,57,58,59,60,61,62,63,64,65,66,67,68,69,74,75,76,77,78,79,80,81,82,83,84,85,86,95,96,97,98,99,100,106,107,108,109,110,111,112,113,114,115,116,117,118,124,125,126,127,0]
    medium = [33,34,35,36,37,38,41,42,43,44,51,52,54,55,70,72,73,87,88,90,93,94,101,102,103,119,120,121,122,123]
    slow = [39,40, 53,71,91,92,104,105]

    closest = params["closest_waypoints"]
    nextwaypoint = max(closest[0], closest[1])

    if params["all_wheels_on_track"] == True:
        if nextwaypoint in centerleft:
            if (params["distance_from_center"] / params["track_width"]) <= 0.25 and (
                params["is_left_of_center"]
            ):
                reward = 14
            elif (params["distance_from_center"] / params["track_width"]) <= 0.25 and (
                not params["is_left_of_center"]
            ):
                reward = 0
            else:
                reward = -7

        elif nextwaypoint in centerright:
            if (params["distance_from_center"] / params["track_width"]) <= 0.25 and (
                not params["is_left_of_center"]
            ):
                reward = 14
            elif (params["distance_from_center"] / params["track_width"]) <= 0.25 and (
                params["is_left_of_center"]
            ):
                reward = 0
            else:
                reward = -7

        elif nextwaypoint in left:
            if (
                (params["is_left_of_center"])
                and (params["distance_from_center"] / params["track_width"]) > 0.25
                and (params["distance_from_center"] / params["track_width"]) < 0.48
            ):
                reward = 14
            else:
                reward = -7
        elif nextwaypoint in right:
            if (
                (not params["is_left_of_center"])
                and (params["distance_from_center"] / params["track_width"]) > 0.25
                and (params["distance_from_center"] / params["track_width"]) < 0.48
            ):
                reward = 14
            else:
                reward = -7

        if nextwaypoint in fast:
            if params["speed"] == 3:
                reward += 14
            else:
                reward -= (5 - params["speed"]) ** 2
        elif nextwaypoint in medium:
            if params["speed"] == 2:
                reward += 14
            else:
                reward -= 7
        elif nextwaypoint in slow:
            if params["speed"] == 1:
                reward += 14
            else:
                reward -= (2 + params["speed"]) ** 2

    else:
        reward = 0.001

    return float(reward)
