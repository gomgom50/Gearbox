from pyray import *
from Gear import Gearclass, draw_gear, draw_centered_rectangle, draw_gearbox, GearBox, Axle

def main():
    init_window(1280, 800, b"Gear Simulation")
    set_target_fps(60)
    module = 15
    speed = 1
    radius = 150
    module = 5
    gear = Gearclass(20, 200, 50, 0, -5)
    gear1 = Gearclass(module=2.5, radius=25, width=80, angle=0, speed_rpm=0, index=0)
    gear2 = Gearclass(module=2.5, radius=50, width=30, angle=0, speed_rpm=0,index=1)
    gear3 = Gearclass(module=2.5, radius=35, width=90, angle=0, speed_rpm=0, index=2)
    gear4 = Gearclass(module=2.5, radius=75, width=50, angle=0, speed_rpm=0, index=3)
    gear5 = Gearclass(module=2.5, radius=50, width=40, angle=0, speed_rpm=0, index=4)
    gear6 = Gearclass(module=2.5, radius=50, width=80, angle=0, speed_rpm=0, index=5)
    gears = [gear1, gear2, gear3, gear4, gear5, gear6]
    axle1 = Axle(gears=[gear1, gear2])
    axle2 = Axle(gears=[gear3, gear4])
    axle3 = Axle(gears=[gear5, gear6])
    Axels = [axle1, axle2, axle3]
    gearbox = GearBox(Axels, input_speed_rpm=speed, connections=[(0, 2), (3,4)])
    width = 100

    while not window_should_close():
        begin_drawing()
        clear_background(BLACK)


        module = gui_slider(Rectangle(50, 200, 100, 20), "Module", str(module), module, 1, 40)
        speed = gui_slider(Rectangle(50, 150, 100, 20), "Speed", str(speed), speed, 1, 50)
        radius = gui_slider(Rectangle(50, 100, 100, 20), "Radius", str(radius), radius, 5, 400)
        width = gui_slider(Rectangle(50, 100, 100, 20), "Radius", str(radius), radius, 5, 400)
        gear.module = int(module)
        gear1.radius = radius
        gear.speed = gear.calculate_speed_degrees(-speed)

        for gearr in gears:
            gearr.module = int(module)

        gearbox.input_speed_rpm = speed

        #draw_gear(gea  r, 400, 300)
        #gear.update()
        # Example usage:
        # Define gear positions (x, y) for drawing

        # Update and draw the entire gearbox
        gearbox.update()

        draw_gearbox(gearbox, (250, 250))

        end_drawing()

    close_window()

if __name__ == "__main__":
    main()