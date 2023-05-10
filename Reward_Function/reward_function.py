import math


class Reward:
    def __init__(self, verbose=False):
        self.first_racingpoint_index = None
        self.verbose = verbose

    def reward_function(self, params):
        # Import package (needed for heading)
        import math

        ################## HELPER FUNCTIONS ###################

        def dist_2_points(x1, x2, y1, y2):
            return abs(abs(x1 - x2) ** 2 + abs(y1 - y2) ** 2) ** 0.5

        def closest_2_racing_points_index(racing_coords, car_coords):
            # Calculate all distances to racing points
            distances = []
            for i in range(len(racing_coords)):
                distance = dist_2_points(
                    x1=racing_coords[i][0],
                    x2=car_coords[0],
                    y1=racing_coords[i][1],
                    y2=car_coords[1],
                )
                distances.append(distance)

            # Get index of the closest racing point
            closest_index = distances.index(min(distances))

            # Get index of the second closest racing point
            distances_no_closest = distances.copy()
            distances_no_closest[closest_index] = 999
            second_closest_index = distances_no_closest.index(min(distances_no_closest))

            return [closest_index, second_closest_index]

        def dist_to_racing_line(closest_coords, second_closest_coords, car_coords):
            # Calculate the distances between 2 closest racing points
            a = abs(
                dist_2_points(
                    x1=closest_coords[0],
                    x2=second_closest_coords[0],
                    y1=closest_coords[1],
                    y2=second_closest_coords[1],
                )
            )

            # Distances between car and closest and second closest racing point
            b = abs(
                dist_2_points(
                    x1=car_coords[0],
                    x2=closest_coords[0],
                    y1=car_coords[1],
                    y2=closest_coords[1],
                )
            )
            c = abs(
                dist_2_points(
                    x1=car_coords[0],
                    x2=second_closest_coords[0],
                    y1=car_coords[1],
                    y2=second_closest_coords[1],
                )
            )

            # Calculate distance between car and racing line (goes through 2 closest racing points)
            # try-except in case a=0 (rare bug in DeepRacer)
            try:
                distance = abs(
                    -(a**4)
                    + 2 * (a**2) * (b**2)
                    + 2 * (a**2) * (c**2)
                    - (b**4)
                    + 2 * (b**2) * (c**2)
                    - (c**4)
                ) ** 0.5 / (2 * a)
            except:
                distance = b

            return distance

        # Calculate which one of the closest racing points is the next one and which one the previous one
        def next_prev_racing_point(
            closest_coords, second_closest_coords, car_coords, heading
        ):
            # Virtually set the car more into the heading direction
            heading_vector = [
                math.cos(math.radians(heading)),
                math.sin(math.radians(heading)),
            ]
            new_car_coords = [
                car_coords[0] + heading_vector[0],
                car_coords[1] + heading_vector[1],
            ]

            # Calculate distance from new car coords to 2 closest racing points
            distance_closest_coords_new = dist_2_points(
                x1=new_car_coords[0],
                x2=closest_coords[0],
                y1=new_car_coords[1],
                y2=closest_coords[1],
            )
            distance_second_closest_coords_new = dist_2_points(
                x1=new_car_coords[0],
                x2=second_closest_coords[0],
                y1=new_car_coords[1],
                y2=second_closest_coords[1],
            )

            if distance_closest_coords_new <= distance_second_closest_coords_new:
                next_point_coords = closest_coords
                prev_point_coords = second_closest_coords
            else:
                next_point_coords = second_closest_coords
                prev_point_coords = closest_coords

            return [next_point_coords, prev_point_coords]

        def racing_direction_diff(
            closest_coords, second_closest_coords, car_coords, heading
        ):
            # Calculate the direction of the center line based on the closest waypoints
            next_point, prev_point = next_prev_racing_point(
                closest_coords, second_closest_coords, car_coords, heading
            )

            # Calculate the direction in radius, arctan2(dy, dx), the result is (-pi, pi) in radians
            track_direction = math.atan2(
                next_point[1] - prev_point[1], next_point[0] - prev_point[0]
            )

            # Convert to degree
            track_direction = math.degrees(track_direction)

            # Calculate the difference between the track direction and the heading direction of the car
            direction_diff = abs(track_direction - heading)
            if direction_diff > 180:
                direction_diff = 360 - direction_diff

            return direction_diff

        # Gives back indexes that lie between start and end index of a cyclical list
        # (start index is included, end index is not)
        def indexes_cyclical(start, end, array_len):
            if end < start:
                end += array_len

            return [index % array_len for index in range(start, end)]

        # Calculate how long car would take for entire lap, if it continued like it did until now
        def projected_time(first_index, closest_index, step_count, times_list):
            # Calculate how much time has passed since start
            current_actual_time = (step_count - 1) / 15

            # Calculate which indexes were already passed
            indexes_traveled = indexes_cyclical(
                first_index, closest_index, len(times_list)
            )

            # Calculate how much time should have passed if car would have followed optimals
            current_expected_time = sum([times_list[i] for i in indexes_traveled])

            # Calculate how long one entire lap takes if car follows optimals
            total_expected_time = sum(times_list)

            # Calculate how long car would take for entire lap, if it continued like it did until now
            try:
                projected_time = (
                    current_actual_time / current_expected_time
                ) * total_expected_time
            except:
                projected_time = 9999

            return projected_time

        #################### RACING LINE ######################

        # Optimal racing line for the Spain track
        # Each row: [x,y,speed,timeFromPreviousPoint]
        racing_track = [
            [8.54861, 3.17367, 4.0, 0.05036],
            [8.34696, 3.17288, 3.97255, 0.05076],
            [8.14533, 3.17223, 3.51675, 0.05733],
            [7.9437, 3.17199, 3.27282, 0.06161],
            [7.74207, 3.17269, 2.62127, 0.07692],
            [7.54109, 3.17783, 2.51994, 0.07978],
            [7.34089, 3.18917, 2.51994, 0.07957],
            [7.14154, 3.20726, 2.51994, 0.07944],
            [6.94331, 3.23395, 2.51994, 0.07937],
            [6.74689, 3.27045, 2.51994, 0.07928],
            [6.55319, 3.29124, 2.51994, 0.07731],
            [6.3596, 3.2961, 2.61531, 0.07405],
            [6.16594, 3.28627, 2.89363, 0.06701],
            [5.97192, 3.26428, 3.36446, 0.05804],
            [5.77717, 3.23299, 3.84935, 0.05124],
            [5.57868, 3.20773, 3.84935, 0.05198],
            [5.37919, 3.18964, 4.0, 0.05008],
            [5.17891, 3.17814, 4.0, 0.05015],
            [4.97806, 3.17181, 4.0, 0.05024],
            [4.77683, 3.16899, 4.0, 0.05031],
            [4.57536, 3.16817, 4.0, 0.05037],
            [4.37371, 3.16823, 4.0, 0.05041],
            [4.17206, 3.16857, 4.0, 0.05041],
            [3.97041, 3.1691, 4.0, 0.05041],
            [3.76876, 3.16984, 4.0, 0.05041],
            [3.56711, 3.17069, 4.0, 0.05041],
            [3.36546, 3.17165, 4.0, 0.05041],
            [3.16381, 3.17273, 3.4943, 0.05771],
            [2.96216, 3.1739, 2.87161, 0.07022],
            [2.76053, 3.17493, 2.50151, 0.08061],
            [2.55891, 3.17449, 2.24419, 0.08984],
            [2.35732, 3.17121, 2.0462, 0.09853],
            [2.1559, 3.16378, 1.59255, 0.12656],
            [1.9548, 3.16523, 1.38039, 0.14569],
            [1.75484, 3.17973, 1.3084, 0.15323],
            [1.55723, 3.21122, 1.3084, 0.15293],
            [1.36385, 3.26358, 1.3084, 0.15312],
            [1.17802, 3.34056, 1.3084, 0.15373],
            [0.98293, 3.3764, 1.3084, 0.1516],
            [0.79264, 3.35874, 1.3084, 0.14607],
            [0.62144, 3.2889, 1.32256, 0.1398],
            [0.4779, 3.17528, 1.42098, 0.12883],
            [0.36468, 3.02833, 1.61783, 0.11466],
            [0.27946, 2.85809, 1.93846, 0.09821],
            [0.21672, 2.67289, 1.65293, 0.1183],
            [0.16923, 2.47927, 1.46534, 0.13605],
            [0.12896, 2.28168, 1.41825, 0.14218],
            [0.08933, 2.08396, 1.41825, 0.14218],
            [0.05219, 1.88611, 1.41825, 0.14194],
            [0.03791, 1.68895, 1.41825, 0.13938],
            [0.06075, 1.49788, 1.41825, 0.13568],
            [0.12631, 1.32178, 1.41825, 0.13249],
            [0.23229, 1.16877, 1.45563, 0.12787],
            [0.37218, 1.0439, 1.56868, 0.11954],
            [0.53781, 0.94851, 1.76671, 0.10819],
            [0.72087, 0.88029, 2.11671, 0.09229],
            [0.91391, 0.83325, 2.84517, 0.06983],
            [1.11132, 0.79873, 4.0, 0.0501],
            [1.30839, 0.76098, 4.0, 0.05016],
            [1.50464, 0.71918, 3.63246, 0.05524],
            [1.70015, 0.67383, 3.25497, 0.06166],
            [1.89507, 0.62562, 2.64673, 0.07586],
            [2.08921, 0.57451, 2.5035, 0.08019],
            [2.28444, 0.52817, 2.5035, 0.08015],
            [2.48108, 0.48813, 2.5035, 0.08016],
            [2.67945, 0.45608, 2.5035, 0.08026],
            [2.87968, 0.43409, 2.24166, 0.08986],
            [3.08022, 0.42755, 2.075, 0.09669],
            [3.27977, 0.43812, 2.06145, 0.09694],
            [3.4779, 0.46307, 1.99399, 0.10015],
            [3.67497, 0.49666, 1.87288, 0.10674],
            [3.86763, 0.53297, 1.6379, 0.1197],
            [4.06119, 0.54894, 1.55792, 0.12466],
            [4.25461, 0.54155, 1.55792, 0.12424],
            [4.44659, 0.5105, 1.55792, 0.12483],
            [4.63522, 0.45377, 1.55792, 0.12644],
            [4.8166, 0.3675, 1.55792, 0.12892],
            [5.00809, 0.3196, 1.55792, 0.1267],
            [5.20113, 0.3139, 1.56016, 0.12379],
            [5.38928, 0.34855, 1.65779, 0.1154],
            [5.56866, 0.41794, 1.84842, 0.10406],
            [5.7378, 0.51496, 1.89204, 0.10306],
            [5.89772, 0.63132, 1.89204, 0.10453],
            [6.04852, 0.7581, 1.89204, 0.10413],
            [6.21325, 0.86251, 1.89204, 0.10308],
            [6.39091, 0.94169, 1.82016, 0.10686],
            [6.5787, 0.99585, 1.77618, 0.11004],
            [6.7736, 1.02629, 1.77618, 0.11106],
            [6.97274, 1.03379, 1.77618, 0.1122],
            [7.17288, 1.01777, 1.77618, 0.11304],
            [7.36817, 0.9768, 1.71649, 0.11625],
            [7.55075, 0.90673, 1.68559, 0.11602],
            [7.71712, 0.80896, 1.68559, 0.11449],
            [7.86711, 0.68819, 1.68559, 0.11424],
            [8.00254, 0.54962, 1.68559, 0.11495],
            [8.12167, 0.40214, 1.68559, 0.11247],
            [8.26224, 0.27881, 1.68559, 0.11094],
            [8.42282, 0.18176, 1.7844, 0.10515],
            [8.59982, 0.11015, 1.49618, 0.12762],
            [8.7889, 0.06128, 1.33734, 0.14603],
            [8.98557, 0.03102, 1.3, 0.15306],
            [9.18602, 0.01536, 1.3, 0.15466],
            [9.29012, 0.01158, 1.3, 0.08012],
            [9.41743, 0.01704, 1.3, 0.09803],
            [9.58679, 0.05544, 1.3, 0.13358],
            [9.74803, 0.1415, 1.3, 0.14059],
            [9.87735, 0.2694, 1.34495, 0.13523],
            [9.96811, 0.42765, 1.47375, 0.12378],
            [10.02194, 0.60589, 1.69107, 0.11011],
            [10.04418, 0.79626, 2.04746, 0.09361],
            [10.04267, 0.9931, 2.71702, 0.07245],
            [10.0267, 1.19304, 4.0, 0.05014],
            [10.00562, 1.39358, 2.19608, 0.09182],
            [9.9837, 1.59403, 1.62188, 0.12433],
            [9.96081, 1.79435, 1.4472, 0.13932],
            [9.9367, 1.99447, 1.42909, 0.14105],
            [9.91111, 2.19439, 1.42909, 0.14103],
            [9.88355, 2.39404, 1.42909, 0.14103],
            [9.83531, 2.58478, 1.42909, 0.13767],
            [9.75413, 2.7554, 1.42909, 0.13222],
            [9.63859, 2.8976, 1.42909, 0.12821],
            [9.49348, 3.00761, 1.52153, 0.11968],
            [9.32574, 3.0858, 1.71655, 0.10782],
            [9.1423, 3.13571, 2.00679, 0.09473],
            [8.94891, 3.1625, 2.46899, 0.07908],
            [8.75005, 3.17267, 3.40852, 0.05842],
        ]

        ################## INPUT PARAMETERS ###################

        # Read all input parameters
        all_wheels_on_track = params["all_wheels_on_track"]
        x = params["x"]
        y = params["y"]
        distance_from_center = params["distance_from_center"]
        is_left_of_center = params["is_left_of_center"]
        heading = params["heading"]
        progress = params["progress"]
        steps = params["steps"]
        speed = params["speed"]
        steering_angle = params["steering_angle"]
        track_width = params["track_width"]
        waypoints = params["waypoints"]
        closest_waypoints = params["closest_waypoints"]
        is_offtrack = params["is_offtrack"]

        ############### OPTIMAL X,Y,SPEED,TIME ################

        # Get closest indexes for racing line (and distances to all points on racing line)
        closest_index, second_closest_index = closest_2_racing_points_index(
            racing_track, [x, y]
        )

        # Get optimal [x, y, speed, time] for closest and second closest index
        optimals = racing_track[closest_index]
        optimals_second = racing_track[second_closest_index]

        # Save first racingpoint of episode for later
        if self.verbose == True:
            self.first_racingpoint_index = 0  # this is just for testing purposes
        if steps == 1:
            self.first_racingpoint_index = closest_index

        ################ REWARD AND PUNISHMENT ################

        ## Define the default reward ##
        reward = 1

        ## Reward if car goes close to optimal racing line ##
        DISTANCE_MULTIPLE = 1
        dist = dist_to_racing_line(optimals[0:2], optimals_second[0:2], [x, y])
        distance_reward = max(1e-3, 1 - (dist / (track_width * 0.5)))
        reward += distance_reward * DISTANCE_MULTIPLE

        ## Reward if speed is close to optimal speed ##
        SPEED_DIFF_NO_REWARD = 1
        SPEED_MULTIPLE = 2
        speed_diff = abs(optimals[2] - speed)
        if speed_diff <= SPEED_DIFF_NO_REWARD:
            # we use quadratic punishment (not linear) bc we're not as confident with the optimal speed
            # so, we do not punish small deviations from optimal speed
            speed_reward = (1 - (speed_diff / (SPEED_DIFF_NO_REWARD)) ** 2) ** 2
        else:
            speed_reward = 0
        reward += speed_reward * SPEED_MULTIPLE

        # Reward if less steps
        REWARD_PER_STEP_FOR_FASTEST_TIME = 1
        STANDARD_TIME = 37
        FASTEST_TIME = 27
        times_list = [row[3] for row in racing_track]
        projected_time = projected_time(
            self.first_racingpoint_index, closest_index, steps, times_list
        )
        try:
            steps_prediction = projected_time * 15 + 1
            reward_prediction = max(
                1e-3,
                (
                    -REWARD_PER_STEP_FOR_FASTEST_TIME
                    * (FASTEST_TIME)
                    / (STANDARD_TIME - FASTEST_TIME)
                )
                * (steps_prediction - (STANDARD_TIME * 15 + 1)),
            )
            steps_reward = min(
                REWARD_PER_STEP_FOR_FASTEST_TIME, reward_prediction / steps_prediction
            )
        except:
            steps_reward = 0
        reward += steps_reward

        # Zero reward if obviously wrong direction (e.g. spin)
        direction_diff = racing_direction_diff(
            optimals[0:2], optimals_second[0:2], [x, y], heading
        )
        if direction_diff > 30:
            reward = 1e-3

        # Zero reward of obviously too slow
        speed_diff_zero = optimals[2] - speed
        if speed_diff_zero > 0.5:
            reward = 1e-3

        ## Incentive for finishing the lap in less steps ##
        REWARD_FOR_FASTEST_TIME = (
            1500  # should be adapted to track length and other rewards
        )
        STANDARD_TIME = 37  # seconds (time that is easily done by model)
        FASTEST_TIME = 27  # seconds (best time of 1st place on the track)
        if progress == 100:
            finish_reward = max(
                1e-3,
                (-REWARD_FOR_FASTEST_TIME / (15 * (STANDARD_TIME - FASTEST_TIME)))
                * (steps - STANDARD_TIME * 15),
            )
        else:
            finish_reward = 0
        reward += finish_reward

        ## Zero reward if off track ##
        if all_wheels_on_track == False:
            reward = 1e-3

        ####################### VERBOSE #######################

        if self.verbose == True:
            print("Closest index: %i" % closest_index)
            print("Distance to racing line: %f" % dist)
            print("=== Distance reward (w/out multiple): %f ===" % (distance_reward))
            print("Optimal speed: %f" % optimals[2])
            print("Speed difference: %f" % speed_diff)
            print("=== Speed reward (w/out multiple): %f ===" % speed_reward)
            print("Direction difference: %f" % direction_diff)
            print("Predicted time: %f" % projected_time)
            print("=== Steps reward: %f ===" % steps_reward)
            print("=== Finish reward: %f ===" % finish_reward)

        #################### RETURN REWARD ####################

        # Always return a float value
        return float(reward)


reward_object = Reward()  # add parameter verbose=True to get noisy output for testing


def reward_function(params):
    return reward_object.reward_function(params)
