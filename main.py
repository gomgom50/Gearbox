from pyray import *
from Gear import Gearclass, draw_gear, draw_centered_rectangle, draw_gearbox, GearBox

def main():
    init_window(1920, 1080, b"Gear Simulation")
    set_target_fps(60)
    module = 15
    speed = 1
    radius = 150
    gear = Gearclass(20, 200, 50, 0, -5)
    gear1 = Gearclass(module=5, radius=150, width=50, angle=0, speed_rpm=0)
    gear2 = Gearclass(module=5, radius=30, width=30, angle=0, speed_rpm=0)
    gear3 = Gearclass(module=5, radius=100, width=50, angle=0, speed_rpm=0)
    gear4 = Gearclass(module=5, radius=200, width=40, angle=0, speed_rpm=0)

    while not window_should_close():
        begin_drawing()

        clear_background(BLACK)
        module = gui_slider(Rectangle(50, 200, 100, 20), "Module", str(module), module, 1, 50)
        speed = gui_slider(Rectangle(50, 150, 100, 20), "Speed", str(speed), speed, 1, 50)
        radius = gui_slider(Rectangle(50, 100, 100, 20), "Radius", str(radius), radius, 5, 400)
        gear.module = int(module)
        gear1.radius = radius
        gear.speed = gear.calculate_speed_degrees(-speed)

        #draw_gear(gear, 400, 300)
        #gear.update()
        # Example usage:

        gearbox = GearBox(gears=[gear1, gear2, gear3, gear4], input_speed_rpm=speed, connections=[(0, 1), (1, 2), (2, 3)])

        # Define gear positions (x, y) for drawing

        # Update and draw the entire gearbox
        gearbox.update()

        draw_gearbox(gearbox, (250, 250))

        end_drawing()

    close_window()

if __name__ == "__main__":
    main()