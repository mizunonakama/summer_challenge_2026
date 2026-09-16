import sys
import math
import random

# Connect towns with your train tracks and disrupt the opponent's.

my_id = int(input())  # 0 or 1
opponent_id = 1 - my_id
width = int(input())  # map size
height = int(input())

_map = [[{"region_id":-1, "_type":-1} for _ in range(width)] for _ in range(height)]
for i in range(height):
    for j in range(width):
        # _type: 0 (PLAINS), 1 (RIVER), 2 (MOUNTAIN), 3 (POI)
        region_id, _type = [int(k) for k in input().split()]
        _map[i][j]["region_id"] = region_id
        _map[i][j]["_type"] = _type

town_count = int(input())
towns = {}
for i in range(town_count):
    inputs = input().split()
    town_id = int(inputs[0])
    town_x = int(inputs[1])
    town_y = int(inputs[2])
    desired_connections = inputs[3]  # comma-separated town ids e.g. 0,1,2,3

    towns[f"{town_id}"] = {
        "town_x": town_x, 
        "town_y": town_y, 
        "desired_connections": desired_connections.split(",")
    }

selected_town_id = [
    town_id for town_id in list(towns.keys()) \
    if towns[town_id]["desired_connections"] !="x"
][0]

#print(selected_town_id, file=sys.stderr, flush=True)

# game loop
while True:
    my_score = int(input())
    foe_score = int(input())
    tracks_map = [[0 for _ in range(width)] for _ in range(height)]
    opponent_tracks = []
    my_tracks = []
    for i in range(height):
        for j in range(width):
            inputs = input().split()
            tracks_owner = int(inputs[0])
            instability = int(inputs[1])  # region inked (destroyed) when this >= 3.
            inked = inputs[2] != "0"  # true if region is destroyed.
            part_of_active_connections = inputs[3]  # if this cell is part of one or more railway connections, this will be town ids (separated by -) in a list separated by commas. e.g. 0-1,1-2,1-3. "x" otherwise.

            if tracks_owner == opponent_id:
                tracks_map[i][j] = 1
                opponent_tracks.append((i,j))
            elif tracks_owner == my_id:
                tracks_map[i][j] = -1
                my_tracks.append((i,j))
            
    # Write an action using print
    # To debug: print("Debug messages...", file=sys.stderr, flush=True)
    command_line = ""

    selected_town = towns[selected_town_id]

    from_x = selected_town["town_x"]
    from_y = selected_town["town_y"]

    to_town_id = str(selected_town["desired_connections"][0])
    #print(towns, file=sys.stderr, flush=True)

    to_x = towns[to_town_id]["town_x"]
    to_y = towns[to_town_id]["town_y"]
    command_line += f"AUTOPLACE {from_x} {from_y} {to_x} {to_y}"

    print(opponent_tracks, file=sys.stderr, flush=True)
    if len(opponent_tracks) > 0:
        to_disrupt_y, to_disrupt_x  = random.choice(opponent_tracks)
        command_line += f";DISRUPT {to_disrupt_x} {to_disrupt_y}" 
                
    # AUTOPLACE x1 y1 x2 y2 | PLACE_TRACKS x y | DISRUPT regionId | MESSAGE text
    # print("WAIT")
    print(command_line)
