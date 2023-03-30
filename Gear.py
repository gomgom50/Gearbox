from pyray import *
import math

class Axle:
    def __init__(self, gears):
        self.gears = gears

    def add_gear(self, gear):
        self.gears.append(gear)

class Gearclass:
    def __init__(self, module, radius, width, angle=0, speed_rpm=0, index=None):
        self.module = module
        self.radius = radius
        self.width = width
        self.angle = angle
        self.speed = self.calculate_speed_degrees(speed_rpm)
        self.num_teeth = self.calculate_teeth()
        self.diameters = self.calculate_diameters()
        self.torque = 0
        self.index = index


    def calculate_teeth(self):
        return int(round(self.radius / self.module))

    def calculate_diameters(self):
        pitch_diameter = self.radius * 2
        outer_diameter = pitch_diameter + 2 * self.module
        inner_diameter = pitch_diameter - 2 * self.module
        return {"pitch": pitch_diameter, "outer": outer_diameter, "inner": inner_diameter}

    def update(self):
        self.angle += self.speed
        self.angle %= 360
        self.num_teeth = int(round(self.radius / self.module))
        self.diameters = self.calculate_diameters()

    def calculate_speed_degrees(self, speed_rpm):
        degrees_per_revolution = 360
        frames_per_minute = 60 * 60  # 60 frames per second * 60 seconds per minute
        return (speed_rpm * degrees_per_revolution) / frames_per_minute

    def calculate_rpm_degrees(self, angle_per_minute):
        degrees_per_revolution = 360
        frames_per_minute = 60 * 60  # 60 frames per second * 60 seconds per minute
        return (angle_per_minute * frames_per_minute) / degrees_per_revolution


def draw_centered_rectangle(x, y, width, height, color):
    centered_y = y - height // 2
    draw_rectangle(x, centered_y, width, height, color)


def draw_gear(gear, x, y):
    draw_rectangle(int(x - gear.width // 2), int(y - gear.diameters["outer"] // 2), int(gear.width), int(gear.diameters["outer"]),
                   GRAY)

    draw_rectangle(int(x - gear.width // 2), int(y - gear.diameters["pitch"] // 2), int(gear.width),
                   int(gear.diameters["pitch"]),
                   LIGHTGRAY)

    draw_rectangle(int(x - gear.width // 2), int(y - gear.diameters["inner"] // 2), int(gear.width), int(gear.diameters["inner"]),
                        DARKGRAY)
    tooth_base_height = gear.module
    perspective_factor = 1  # Adjust this value to control the perspective effect

    for i in range(gear.num_teeth):
        angle = (360 / gear.num_teeth) * i + gear.angle
        start_y = y + gear.diameters["outer"] // 2 * math.sin(math.radians(angle))
        end_y = y + gear.diameters["outer"] // 2 * math.sin(math.radians(angle))

        tooth_top_height = int(tooth_base_height * (1 - perspective_factor * (1 - abs(math.cos(math.radians(angle))))))
        tooth_top_height = min(tooth_top_height, gear.diameters["outer"] // 2 - gear.diameters["pitch"] // 2) * 4
        remaining_distance = gear.diameters["outer"] // 2 - (
                    gear.diameters["outer"] // 2 - gear.diameters["pitch"] // 2)
        tooth_top_height = min(tooth_top_height, remaining_distance)  #

        tooth_top_y = int((start_y + end_y) / 2 - tooth_top_height / 2)

        if math.cos(math.radians(angle)) > 0:  # Only render the teeth if they are visible from the side view
            tooth_rectangle_x = int(x - gear.width // 2)
            tooth_rectangle_y = int(tooth_top_y)
            tooth_rectangle_width = int(gear.width)
            tooth_rectangle_height = int(tooth_top_height)

            draw_rectangle(tooth_rectangle_x, tooth_rectangle_y, tooth_rectangle_width, tooth_rectangle_height, RAYWHITE)
    draw_text("RPM", int(x+gear.width), int(y-30/2), 5, RAYWHITE)
    gui_text_box(Rectangle(x+gear.width, y-15/2, 50, 15), str(gear.calculate_rpm_degrees(gear.speed)), 5, False)
    draw_text("Torque", int(x + gear.width), int(y + 15 / 2), 5, RAYWHITE)
    gui_text_box(Rectangle(x + gear.width, y + 30 / 2, 50, 15), str(gear.torque), 5, False)

    def update_gear_speeds(self):
        for i, gear in enumerate(self.gears):
            gear.speed = gear.calculate_speed_degrees(self.gear_data[i]['speed_rpm'])

class GearBox:
    def __init__(self, axles, connections, input_speed_rpm):
        self.axles = axles
        self.connections = connections
        self.gears = [gear for axle in self.axles for gear in axle.gears]
        self.input_speed_rpm = input_speed_rpm
        self.gear_data = self.calculate_gear_data(20)
        self.update_gear_speeds()

    def update(self):
        self.update_gear_speeds()
        self.gear_data = self.calculate_gear_data(20)
        for gear in self.gears:
            gear.update()


    def add_gear(self, gear):
        self.gears.append(gear)
        #.gear_data = self.calculate_gear_data()
        self.update_gear_speeds()

    def add_connection(self, gear1_index, gear2_index):
        self.connections.append((gear1_index, gear2_index))
        self.gear_data = self.calculate_gear_data()



    def find_gear(self, index):
        for axle in self.axles:
            for gear in axle.gears:
                if gear.index == index:
                    return gear
        return None

    def calculate_gear_data(self, torque):
        gear_data = [None] * sum(len(axle.gears) for axle in self.axles)
        speed_rpm = self.input_speed_rpm

        def calculate_connected_gear_data(index, speed_rpm, torque, direction_multiplier):
            if gear_data[index] is not None:
                return

            gear_data[index] = {"speed_rpm": speed_rpm, "torque": torque, "direction_multiplier": direction_multiplier}

            # Handle parallel connections (gears on the same axle)
            for axle in self.axles:
                axle_gear_indices = [gear.index for gear in axle.gears]
                if index in axle_gear_indices:
                    for connected_gear_index in axle_gear_indices:
                        if connected_gear_index != index:
                            calculate_connected_gear_data(connected_gear_index, speed_rpm, torque, direction_multiplier)

            # Handle series connections (gears connected through the connections list)
            for connection in self.connections:
                if connection[0] == index:
                    next_speed_rpm = speed_rpm * (self.gears[index].num_teeth / self.gears[connection[1]].num_teeth)
                    next_torque = torque * (self.gears[connection[1]].num_teeth / self.gears[index].num_teeth)
                    calculate_connected_gear_data(connection[1], next_speed_rpm, next_torque, -direction_multiplier)
                elif connection[1] == index:
                    next_speed_rpm = speed_rpm * (self.gears[index].num_teeth / self.gears[connection[0]].num_teeth)
                    next_torque = torque * (self.gears[connection[0]].num_teeth / self.gears[index].num_teeth)
                    calculate_connected_gear_data(connection[0], next_speed_rpm, next_torque, -direction_multiplier)

        calculate_connected_gear_data(0, speed_rpm, torque, 1)
        return gear_data

    def update_gear_speeds(self):
        for i, gear in enumerate(self.gears):
            if self.gear_data[i] is not None:
                gear.speed = gear.calculate_speed_degrees(self.gear_data[i]['direction_multiplier'] * self.gear_data[i]['speed_rpm'])
                gear.torque = self.gear_data[i]['direction_multiplier'] * self.gear_data[i]['torque']

    def axle_of_gear(self, gear_index):
        for axle in self.axles:
            for gear in axle.gears:
                if gear.index == gear_index:
                    return axle
        return None


def draw_gearbox(self, initial_position):
    gear_positions = [None] * len(self.gears)
    axle_positions = [None] * len(self.axles)
    axle_width = 10  # The width of the axle rectangle

    def dfs_traverse(axle, gear_index, position, visited, connection_angle=0):
        gear = self.find_gear(gear_index)
        if visited[gear_index] or gear is None:
            return
        visited[gear_index] = True

        gear_positions[gear_index] = position
        x, y = position

        # Handle parallel gears (gears on the same axle)
        axle_of_current_gear = self.axle_of_gear(gear_index)
        if axle_of_current_gear:
            for parallel_gear in axle_of_current_gear.gears:
                if parallel_gear.index != gear_index:
                    parallel_position = (x + gear.width + parallel_gear.width, y)
                    dfs_traverse(axle_of_current_gear, parallel_gear.index, parallel_position, visited, connection_angle=0)

        # Handle series gears (gears connected through the connections list)
        for connection in self.connections:
            if connection[0] == gear_index:
                connected_gear_index = connection[1]
                connected_gear = self.find_gear(connected_gear_index)
                distance = gear.diameters["pitch"] / 2 + connected_gear.diameters["pitch"] / 2
                new_position = (x, y + distance)
                dfs_traverse(axle, connected_gear_index, new_position, visited, connection_angle=0)
            elif connection[1] == gear_index:
                connected_gear_index = connection[0]
                connected_gear = self.find_gear(connected_gear_index)
                distance = gear.diameters["pitch"] / 2 + connected_gear.diameters["pitch"] / 2
                new_position = (x, y - distance)
                dfs_traverse(axle, connected_gear_index, new_position, visited, connection_angle=0)

    visited = [False] * len(self.gears)
    for axle in self.axles:
        for gear in axle.gears:
            dfs_traverse(axle, gear.index, initial_position, visited)

    for i, axle in enumerate(self.axles):
        if len(axle.gears) == 1:
            gear_position = gear_positions[axle.gears[0].index]
            x = gear_position[0] - axle_width - axle.gears[0].width // 2
            y = gear_position[1] - axle_width // 2
            axle_positions[i] = (x, y)
            draw_rectangle(x, y, axle_width, axle_width, GRAY)
        else:
            gear_positions_on_axle = [gear_positions[gear.index] for gear in axle.gears]
            min_x = min(pos[0] for pos in gear_positions_on_axle)
            max_x = max(pos[0] for pos in gear_positions_on_axle)
            y = gear_positions_on_axle[0][1]
            axle_positions[i] = (min_x - axle_width, y - axle_width // 2)
            draw_rectangle(int(min_x - axle_width),int(y - axle_width // 2),int(max_x - min_x + axle_width * 2), axle_width, GRAY)

    for gear, position in zip(self.gears, gear_positions):
        if position is not None:
            draw_gear(gear, int(round(position[0])), int(round(position[1])))




