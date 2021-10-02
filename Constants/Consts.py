###########GLOBAL VARIABLES############

# time between updates for DynamicGUI in ms
speed_dynamic = 200
fast_speed_dynamic = 10
# time between updates for StaticGUI
speed_static = 10
# THE REAL LIFE REPRESENTATION OF TILE SIZE IN CM
tile_size = 40
# The GUI size of tiles in pixels(every pixel represents tile_size/GUI_tile_size)
GUI_tile_size = 4
# The tile sclaing factor is how many cm every pixel represents
tile_scale_fac = tile_size / GUI_tile_size

# bloated tile color
bloated_color = "#ffc0cb"
# obstacle tile color
obstacle_color = "#ffCC99"
# background color
background_color = "#545454"

# height of window
tile_num_height = 200
# width of window
tile_num_width = 200
# visibility radius (in real life cm)
# INV: vis_radius/tile_size must be an int
vis_radius = 1000

# The radius of the robot
robot_radius = 80
# The bloat factor (how many times the radius of robot to bloat tiles by)
bloat_factor = 2
# recalculation rate
steps_to_recalc = 9
# no. of iterations to wait before recalcuting path
recalc_wait = 7
# line length for dynamic smooth path
length_draw = 1
# how many degrees to turn per iteration
turn_speed = 5
# degree frequency at which to generate lidar data
degree_freq = 1
# the radius around the starting position of the robot that should have no obstacles
tol = int(robot_radius/tile_size + (robot_radius / tile_size) * bloat_factor)

# terabee mapping from index to angle
# TODO: UPDATE THESE DICTS ACCORDING TO C1C0
terabee_dict_bot = {}
for i in range(14):
    terabee_dict_bot[i] = i*24
terabee_dict_mid = terabee_dict_bot
terabee_dict_top = terabee_dict_bot

terabee_dict = [terabee_dict_top, terabee_dict_mid, terabee_dict_bot]

obstacle_value = 3
# for the functions in increase score and decrease score in grid.py to determine
# when it's necessary to consider a tile an obstacle
obstacle_threshold = 5

bloat_colors = {1: "#009dc4", 2: "#008db0", 3: "#007e9d", 4: "#006e89", 5: "#005e76", 6: "#004f62", 7: "#003f4e", 8:"#002f3b", 9:"#001f27", 10:"#001014"}
#obstacle_colors = {1: "#ff7034", 2: "#e6652f", 3: "#cc5a2a", 4: "#b34e24", 5: "#99431f", 6: "#80381a", 7: "#662d15", 8: "#4d2210", 9: "#33160a",10: "#190b05"}
obstacle_colors = {1: "#190b05", 2: "#33160a", 3: "#4d2210", 4: "662d15", 5: "#80381a", 6: "#99431f", 7: "#b34e24", 8: "#cc5a2a", 9: "#e6652f",10: "#ff7034"}

# USB port name for indoor GPS
tty = "/dev/tty.usbmodem00000000050C1"
# address of the hedgehog
adr = 97


# gain values for PID
gaine = -0.05
gainI = -0.03
gaind = -0.02
# the score at which the obstacle score increments by
incr_obs_score = 1
# the score at which the obstacle score decrements by
decr_obs_score = 1

vector_draw_length = 350
reached_tile_bound = tile_size * 2.0

time_threshold = 10