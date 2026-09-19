# Using random route analysis gave timeout
import sys
import math
import random

# Connect towns with your train tracks and disrupt the opponent's.

my_id = int(input())  # 0 or 1
opponent_id = 1 - my_id
neutral_id = 2
width = int(input())  # map size
height = int(input())
town_type = 4
track_type = 5
ink_type = 6
map_points = {
    0: 1, # plains
    1: 2, # river
    2: 3, # mountain
    3: 10, # point_of_interest
    town_type: 1000, # Town
    track_type: 1000,
    ink_type: 1000 # inked
}

# FUNCTIONS ------------------------------------------------------

def get_2d_distance(origin: tuple, target: tuple)->int:
    distance = abs(target[0]-origin[0]) + abs(target[1]-origin[1])
    return distance

def get_distance(points)->int:
    distance = len(points)
    return distance

def get_route(world_map, base, target, route_type: str = "shortest")->tuple:
    """
    compute the cheapest route from a base point
    to a target point
    """
    #buffer_points = 6
    # there are more points than necessary
    route_distance = get_2d_distance(base,target)
    route_points = 0
    route = []
    for _ in range(route_distance):
        # Get vectors and directions
        v_x = target[0]-base[0]
        v_y = target[1]-base[1]
        direction_x = 0
        direction_y = 0
        if v_x != 0:
            direction_x = int(v_x/abs(v_x))
        if v_y !=0:
            direction_y = int(v_y/abs(v_y))

        #print(f"base {base}", file=sys.stderr, flush=True)
        #print(f"target {target}", file=sys.stderr, flush=True)
        #print(f"dir x, dir y {(direction_x, direction_y)}", file=sys.stderr, flush=True)
        # check shortest options from 2 possible directions always towards target
        options = [
            (base[0]+direction_x, base[1]),
            (base[0]-direction_x, base[1]), 
            (base[0], base[1]+direction_y),
            (base[0], base[1]-direction_y)
            ]
        # rm base from option due to problem whne base is cheaper than advance
        clean_options = []
        for option in options:
            option_type = world_map[option[1]][option[0]]["_type"]
            
            if option!=base \
            and option!=target \
            and option_type not in (3, 4):
                clean_options += [option]

        if not clean_options:
            continue
        shortest_option = clean_options[0]
        print(clean_options, file=sys.stderr, flush=True)
        shortest_points = world_map[shortest_option[1]][shortest_option[0]]["paint_points"]
        remaining_distance = get_2d_distance(shortest_option,target)
        for option in clean_options:
            option_paint_points = world_map[
                option[1]][option[0]
                ]["paint_points"]
            new_remaining_distance = get_2d_distance(option,target)
            if new_remaining_distance <= remaining_distance:
                if option_paint_points <= shortest_points:
                    shortest_option = option
                    shortest_points = option_paint_points
                    remaining_distance = new_remaining_distance

        route += [shortest_option]
        base = shortest_option

        route_points += shortest_points

    return route, route_points

def get_random_route(world_map, base, target, n_routes = 3)-> tuple:
    """
    Try multiple options and select one with good score, the score can be by price or by lowest number of points
    Note: In the future we do not need to complete all the route to return it
    and use it
    """
    #buffer_points = 6
    # there are more points than necessary
    routes = []
    for _ in range(n_routes):

        #print(f"base {base}", file=sys.stderr, flush=True)
        #print(f"target {target}", file=sys.stderr, flush=True)
        #print(f"dir x, dir y {(direction_x, direction_y)}", file=sys.stderr, flush=True)
        # check shortest options from 4 possible directions always towards target
        uncomplete_route = True
        route = []
        route_points = 0
        while uncomplete_route:
            options = [
                (base[0]+1, base[1]),
                (base[0]-1, base[1]), 
                (base[0], base[1]+1),
                (base[0], base[1]-1)
                ]
            
            if target in options:
                uncomplete_route = False
                break
            
            clean_options = []
            for option in options:
                #print(f"base {option}", file=sys.stderr, flush=True)
                option_type = world_map[option[1]][option[0]]["_type"]
                
                # what is a POI, 3? lets check not using it
                if option[0] >=0 and option[1]>=0\
                and option[0] <width and option[1]<height\
                and option!=base \
                and option!=target \
                and option_type not in (town_type, ink_type)\
                and option not in route:
                    clean_options += [option]

            if not clean_options:
                break
            
            random_option = random.choice(clean_options)

            route += [random_option]
            base = random_option
            route_points += world_map[random_option[1]][random_option[0]]["_type"]

        routes += [
            {
                "route": route, 
                "route_points": route_points, 
                "route_distance": len(route)
            }
        ]
    if not routes:
        return [], None

    # Select the shortest for agility
    shortest_distance = routes[0]["route_distance"]
    selected_route = routes[0]
    for route in routes:
        if route["route_distance"] < shortest_distance:
            selected_route = route
            shortest_distance = route["route_distance"]

    return selected_route, shortest_distance

# HELPERS ------------------------------------------------------

_map = [[{"region_id":-1, "_type":-1} for _ in range(width)] for _ in range(height)]
for i in range(height):
    for j in range(width):
        # _type: 0 (PLAINS), 1 (RIVER), 2 (MOUNTAIN), 3 (POI)
        region_id, _type = [int(k) for k in input().split()]
        _map[i][j]["region_id"] = region_id
        _map[i][j]["_type"] = _type
        _map[i][j]["paint_points"] = map_points[_type]

town_count = int(input())
towns = {}
town_points = []
town_regions = []
for i in range(town_count):
    inputs = input().split()
    town_id = int(inputs[0])
    town_x = int(inputs[1])
    town_y = int(inputs[2])
    desired_connections = inputs[3]  # comma-separated town ids e.g. 0,1,2,3

    town_regions.append(_map[town_y][town_x]["region_id"])

    towns[f"{town_id}"] = {
        "_x": town_x,
        "_y": town_y, 
        "desired_connections": desired_connections.split(",")
    }
    _map[town_y][town_x]["_type"] = town_type
    town_points += [(town_x, town_y)]

town_regions = list(set(town_regions))

# look one forward for cheapest
for town_id, town_data in list(towns.items()):
    base_town = towns[town_id]
    base_x = base_town["_x"]
    base_y = base_town["_y"]
    base = (base_x, base_y)

    towns[town_id]["routes"] = {}
    towns[town_id]["scores"] = {}

    if "x" not in base_town["desired_connections"]:
        for target_town_id in base_town["desired_connections"]:
            target_town = towns[str(target_town_id)]
            target_x = target_town["_x"]
            target_y = target_town["_y"]
            target = (target_x, target_y)

            towns[town_id]["routes"][(base,target)], towns[town_id]["scores"][(base, target)] = get_route(_map, base, target)

towns_ids = list(towns.keys())
# selected_town_id = random.choice([
#     town_id for town_id in towns_ids \
#     if "x" not in towns[town_id]["desired_connections"]
# ])
selected_town_id = towns_ids[0]
selected_town_data = towns[selected_town_id]
base_mean_points = sum(
    selected_town_data["scores"].values()
    )/len(
        selected_town_data["scores"].keys()
        )
for town_id, town_data in list(towns.items()):
    if len(town_data["scores"].keys())>0:
        mean_points = sum(town_data["scores"].values())/len(town_data["scores"].keys())
        if mean_points<base_mean_points:
            base_mean_points= mean_points
            selected_town_id = town_id
            selected_town_data = town_data

#print(selected_town_id, file=sys.stderr, flush=True)

# game loop
while True:
    paint_points = 3
    my_score = int(input())
    foe_score = int(input())

    tracks_map = [[0 for _ in range(width)] for _ in range(height)]

    opponent_tracks = []
    opponent_regions = []
    my_tracks = []
    my_regions = []
    inked_tracks = []
    inked_regions = []
    for i in range(height):
        for j in range(width):
            inputs = input().split()
            tracks_owner = int(inputs[0])
            instability = int(inputs[1])  # region inked (destroyed) when this >= 3.
            inked = inputs[2] != "0"  # true if region is destroyed.
            part_of_active_connections = inputs[3]  # if this cell is part of one or more railway connections, this will be town ids (separated by -) in a list separated by commas. e.g. 0-1,1-2,1-3. "x" otherwise.
            
            track_importance = 0
            for _ in part_of_active_connections.split(","):
                track_importance += 1
            
            if inked:
                _map[i][j]["_type"] = ink_type
                inked_tracks += [(j,i)]
                inked_regions += [_map[i][j]["region_id"]]

            if tracks_owner == my_id or tracks_owner == neutral_id:
                tracks_map[i][j] = -1
                _map[i][j]["_type"] = track_type
                my_tracks += [(j,i)]
                my_regions += [_map[i][j]["region_id"]]

            attack_weight = instability + 2*track_importance
            if tracks_owner == opponent_id:
                tracks_map[i][j] = 1
                _map[i][j]["_type"] = track_type
                opponent_tracks += [(j,i)]
                opponent_regions += attack_weight*[_map[i][j]["region_id"]]

    # Write an action using print
    # To debug: print("Debug messages...", file=sys.stderr, flush=True)
    command_line = ""

    # SELECT BEST TOWN ---------------------
    #for town_id, town_data in list(towns.items()):
    # for random town
    town_data = towns[selected_town_id]
    # SELECT BEST TARGET -------------------
    base = (town_data["_x"], town_data["_y"])

    for target_town_id in town_data["desired_connections"]:
    # for random target
    #target_town_id = random.choice(town_data["desired_connections"])
        target_town = towns[target_town_id]
        target = (target_town["_x"], target_town["_y"])

    # update routes and scores*
        towns[selected_town_id]["routes"][(base, target)], \
        towns[selected_town_id]["scores"][(base, target)] = \
        get_route(_map, base, target)

        # if len(town_data["scores"].keys())>0:
        #     mean_points = sum(town_data["scores"].values())/len(town_data["scores"].keys())
        #     if mean_points<=base_mean_points:
        #         base_mean_points= mean_points
        #         selected_town_id = town_id
        #         selected_town_data = town_data
            

    # print(selected_town, file=sys.stderr, flush=True)

    #inked_map = any([True for row in _map if ink_type in row])
    #if inked_map:
        # route, score = \
        # get_montecarlo_route(
        #     _map, 
        #     base,
        #     target
        #     )
    #else:
    target_routes = list(selected_town_data["routes"].values())
    target_scores = list(selected_town_data["scores"].values())
    # print(target_routes, file=sys.stderr, flush=True)
    # print(target_scores, file=sys.stderr, flush=True)

    # select cheapest route
    route = target_routes[0]
    score = target_scores[0]
    for i in range(len(target_scores)):
        if target_scores[i] <= score:
            route = target_routes[i]
            score = target_scores[i]
    
    cheapest_point = route[0]
    cheapest_paint_points = _map[cheapest_point[1]][cheapest_point[0]]["paint_points"]
    for point in route:
        point_paint_points = _map[point[1]][point[0]]["paint_points"]

        if paint_points > 0 \
        and point_paint_points <= paint_points\
        and point_paint_points <= cheapest_paint_points\
        and point not in opponent_tracks \
        and point not in my_tracks\
        and point not in town_points\
        and point not in inked_tracks:

            command_line += f"PLACE_TRACKS {point[0]} {point[1]};"
            paint_points -= point_paint_points
            my_tracks += [(point[0], point[1])]

    # from_x = selected_town["_x"]
    # from_y = selected_town["_y"]

    
    # to_town_id = str(random.choice(selected_town["desired_connections"])) # [0]
    # #print(towns, file=sys.stderr, flush=True)

    # to_x = towns[to_town_id]["_x"]
    # to_y = towns[to_town_id]["_y"]
    # command_line += f"AUTOPLACE {from_x} {from_y} {to_x} {to_y}"

    #print(opponent_tracks, file=sys.stderr, flush=True)
    if len(opponent_tracks) > 0:
        # to_disrupt_y, to_disrupt_x  = random.choice(opponent_tracks)
        # command_line += f";DISRUPT {to_disrupt_x} {to_disrupt_y}" 

        # list(set(opponent_regions)) if we want no repeated regions
        opponent_regions_with_no_town = [
            region_id for region_id in opponent_regions\
            if region_id not in town_regions
            ]

        # only_opponent_regions = [
        #    region_id for region_id in opponent_regions_with_no_town\
        #    if region_id not in my_regions
        #    ]
        # remove one occurrence it the region is in my regions
        heavier_opponent_regions = opponent_regions_with_no_town
        for region_id in my_regions:
            if region_id in heavier_opponent_regions:
                heavier_opponent_regions.remove(region_id)

        if len(heavier_opponent_regions) > 0:
            region_to_disrupt = random.choice(heavier_opponent_regions)
            command_line += f"DISRUPT {region_to_disrupt};" 

    # AUTOPLACE x1 y1 x2 y2 | PLACE_TRACKS x y | DISRUPT regionId | MESSAGE text
    # print("WAIT")
    print(command_line)

    selected_town_id = random.choice([
        town_id for town_id in list(towns.keys())+2*[selected_town_id] \
        if "x" not in towns[town_id]["desired_connections"]
    ])
