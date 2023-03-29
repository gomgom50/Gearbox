from pyray import *
import math

class Gearclass:
    def __init__(self, module, radius, width, angle=0, speed_rpm=0):
        self.module = module
        self.radius = radius
        self.width = width
        self.angle = angle
        self.speed = self.calculate_speed_degrees(speed_rpm)
        self.num_teeth = self.calculate_teeth()
        self.diameters = self.calculate_diameters()
        self.torque = 0


    def calculate_teeth(self):
        return int(round(self.radius / self.module))

    def calculate_diameters(self):
        pitch_diameter = self.radius*2
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
    def __init__(self, gears, connections, input_speed_rpm):
        self.gears = gears
        self.connections = connections
        self.input_speed_rpm = input_speed_rpm
        self.gear_data = self.calculate_gear_data(20)
        self.update_gear_speeds()

    def update(self):
        for gear in self.gears:
            gear.update()

    def add_gear(self, gear):
        self.gears.append(gear)
        self.gear_data = self.calculate_gear_data()
        self.update_gear_speeds()

    def add_connection(self, gear1_index, gear2_index):
        self.connections.append((gear1_index, gear2_index))
        self.gear_data = self.calculate_gear_data()
        self.update_gear_speeds()

    def calculate_gear_data(self, torque):
        gear_data = [None] * len(self.gears)
        speed_rpm = self.input_speed_rpm


        def calculate_connected_gear_data(index, speed_rpm, torque, direction_multiplier):
            if gear_data[index] is not None:
                return

            gear_data[index] = {"speed_rpm": speed_rpm, "torque": torque, "direction_multiplier": direction_multiplier}

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

def draw_gearbox(gearbox, initial_position):
    gear_positions = [None] * len(gearbox.gears)

    def dfs_traverse(gear_index, position, visited, connection_angle=0):
        if visited[gear_index]:
            return
        visited[gear_index] = True

        gear_positions[gear_index] = position
        x, y = position

        for connection in gearbox.connections:
            if connection[0] == gear_index:
                connected_gear_index = connection[1]
                distance = (gearbox.gears[gear_index].diameters["pitch"] / 2) + (gearbox.gears[connected_gear_index].diameters["pitch"] / 2)
                new_position = (x, y + distance)
                dfs_traverse(connected_gear_index, new_position, visited, connection_angle = 0)
            elif connection[1] == gear_index:
                connected_gear_index = connection[0]
                distance = (gearbox.gears[gear_index].diameters["pitch"] / 2) + (gearbox.gears[connected_gear_index].diameters["pitch"] / 2)
                new_position = (x, y - distance)
                dfs_traverse(connected_gear_index, new_position, visited, connection_angle = 0)

    visited = [False] * len(gearbox.gears)
    dfs_traverse(0, initial_position, visited)

    for gear, position in zip(gearbox.gears, gear_positions):
        if position is not None:
            draw_gear(gear, position[0], position[1])


