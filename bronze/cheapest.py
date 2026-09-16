import sys
import math
import random

# Connect towns with your train tracks and disrupt the opponent's.

my_id = int(input())  # 0 or 1
opponent_id = 1 - my_id
width = int(input())  # map size
height = int(input())

map_points = {
    0:1, # plains
    1:2, # river
    2:3, # mountain
    3:100 # point_of_interest
}

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
town_regions = list(set(town_regions))



def get_route(world_map, base, target, route_type: str = "shortest")->tuple:
    """
    compute the cheapest route from a base point
    to a target point
    """
    #buffer_points = 6
    # there are more points than necessary
    route_distance = abs(base[0] -target[0]) + abs(base[1]-target[1])
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

        # check cheapest options from 2 possible directions always towards target
        options = [(base[0]+direction_x, base[1]), (base[0], base[1]+direction_y)]
        cheapest_option = options[0]
        # print(cheapest_option, file=sys.stderr, flush=True)
        cheapest_points = world_map[cheapest_option[1]][cheapest_option[0]]["paint_points"]
        
        for option in options:
            option_paint_points = world_map[
                option[1]][option[0]
                ]["paint_points"]
            if option_paint_points<cheapest_points:
                cheapest_option = option
                cheapest_points = option_paint_points
        route += [cheapest_option]
        base = cheapest_option

        route_points += cheapest_points

    return route, route_points

towns_ids = list(towns.keys())
selected_town_id = random.choice([
    town_id for town_id in towns_ids \
    if "x" not in towns[town_id]["desired_connections"]
])

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

            if tracks_owner == my_id:
                tracks_map[i][j] = -1
                my_tracks += [(i,j)]
                my_regions += [_map[i][j]["region_id"]]

            attack_weight = instability + 2*track_importance
            if tracks_owner == opponent_id and not inked:
                tracks_map[i][j] = 1
                opponent_tracks += [(i,j)]
                opponent_regions += attack_weight*[_map[i][j]["region_id"]]

            
            
    # Write an action using print
    # To debug: print("Debug messages...", file=sys.stderr, flush=True)
    command_line = ""

    selected_town = towns[selected_town_id]
    # print(selected_town, file=sys.stderr, flush=True)
    selected_routes = list(selected_town["routes"].values())
    selected_scores = list(selected_town["scores"].values())
    print(selected_routes, file=sys.stderr, flush=True)
    print(selected_scores, file=sys.stderr, flush=True)
    cheapest_route = selected_routes[0]
    lowest_score = selected_scores[0]
    for i in range(len(selected_scores)):
        if selected_scores[i]<lowest_score:
            cheapest_route = selected_routes[i]
            lowest_score = selected_scores[i]
    
    for point in cheapest_route:
        if paint_points >0:
            if point not in opponent_tracks and point not in my_tracks:
                command_line += f"PLACE_TRACKS {point[0]} {point[1]};"
                paint_points-=1

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
