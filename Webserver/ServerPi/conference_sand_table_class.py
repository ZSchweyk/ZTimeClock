# import sys
# sys.path.insert(0, "/home/pi/.local/lib/python3.7/site-packages")
import sys
print("Python version:", sys.version)
import time
from ServerPi.settings import *
from math import *
import numpy as np
import odrive
import ServerPi.ODrive_Ease_Lib as ODrive_Ease_Lib
from ServerPi.server import ThetaServer


def scale(value, v_min, v_max, r_min, r_max):
    percentage = (value - v_min) / (v_max - v_min)
    return round(r_min + percentage * (r_max - r_min), 2)


class ConferenceSandTable:
    gear_ratio = 562.5  # (90/15)×(90/15)×(90÷18)×(50/16)
    radius_motor_max_rotations = 25
    rotations_from_center = 2  # TODO: test out making this smaller (1.5 maybe)
    homing_speed = 5

    def __init__(self, server_ip):
        print("Attempting to connect to theta board")
        self.theta_board = odrive.find_any(serial_number="388937553437")
        print("Connected to theta board")

        # Make sure that everything is okay with the brake resistors
        assert self.theta_board.config.enable_brake_resistor, "Check for faulty theta brake resistor."

        self.theta_board.clear_errors()

        self.theta_motor = ODrive_Ease_Lib.ODrive_Axis(self.theta_board.axis0, current_lim=30, vel_lim=30)

        while not self.theta_motor.is_calibrated():
            # self.theta_motor.calibrate_encoder()
            self.theta_motor.calibrate()
            # self.theta_board.reboot()
            print("Calibrated theta")
        print("Finished Calibrating Theta Board")

        self.theta_motor.axis.controller.config.enable_overspeed_error = False

        self.radius_motors_homed = False

        print("Starting ThetaServer...")
        self.server = ThetaServer(server_ip)
        print("Client connected")

        self.ENABLED = True


    def home_radius_motors(self):
        self.server.send_to_radius_client({"method": "home"})
        message = self.server.receive_from_radius_client()
        print("Message from client is:", message)
        if message == "Finished homing":
            print("Entered body")
            self.radius_motors_homed = True

    @staticmethod
    def is_equation_valid(equation):
        builtin_restrictions = {
            "min": min,
            "max": max,
            "abs": abs,
        }
        other_restrictions = {
            "sqrt": sqrt,
            "sin": sin,
            "cos": cos,
        }
        theta = 0
        other_restrictions["theta"] = theta

        try:
            eval(equation, {"__builtins__": builtin_restrictions}, other_restrictions)
        except Exception as exception:
            return False
        return True

    def pre_check(self, equation, theta_speed):
        if not self.is_equation_valid(equation):
            raise Exception("Invalid Equation")

        if not self.radius_motors_homed:
            self.home_radius_motors()

        assert 0 <= theta_speed <= 1, "Incorrect theta_speed bounds. Must be between 0 and 1."

    @staticmethod
    def get_theta_range(equation, count_accuracy=10):
        theta = 0
        theta_increment = pi / 100
        cartesian_coordinates = []
        count = 0
        while True:
            r = eval(equation)
            x, y = r * cos(theta), r * sin(theta)
            if (x, y) in cartesian_coordinates:
                count += 1
            else:
                count = 0

            if count == count_accuracy:
                return theta

            cartesian_coordinates.append((x, y))
            theta += theta_increment


    def draw_equation(self, equation: str, period, theta_speed=.75, scale_factor=1):
        method_start_time = time.perf_counter()
        self.pre_check(equation, theta_speed)
        print("Waiting...")
        time.sleep(1)

        scale_factor = max(min(scale_factor, 1), 0)  # This bounds scale_factor between 0 and 1

        # Find min and max radii for r1 and r2 to scale properly below.
        all_r1_values = []
        all_r2_values = []
        for theta1 in np.arange(0, period / 2, pi / 100):
            theta2 = theta1 + pi
            r1 = eval(equation.replace("theta", "theta1"))
            r2 = eval(equation.replace("theta", "theta2"))
            if (round(r1, 3) >= 0) != (round(r2, 3) >= 0):
                print("Drawing with only 1 motor!")
                return self.draw_equation_with_1_motor(
                    equation,
                    period,
                    theta_speed=theta_speed,
                    scale_factor=scale_factor
                )

            all_r1_values.append(r1)
            all_r2_values.append(r2)

        smallest_r1, largest_r1 = min(min(all_r1_values), 0), max(all_r1_values)
        smallest_r2, largest_r2 = min(min(all_r2_values), 0), max(all_r2_values)





        ##################### GO TO FIRST POINT (THIS COULD BE FAR AWAY) #########################
        initial_r1 = eval(equation.replace("theta", "0"))
        initial_r2 = eval(equation.replace("theta", "pi"))

        r1 = scale(initial_r1, smallest_r1, largest_r1, -self.radius_motor_max_rotations * scale_factor,
                   self.radius_motor_max_rotations * scale_factor)
        r2 = scale(initial_r2, smallest_r2, largest_r2, -self.radius_motor_max_rotations * scale_factor,
                   self.radius_motor_max_rotations * scale_factor)

        accel = 2
        vel = 3
        decel = 2

        dict_of_points = {}
        if r1 >= 0:
            r1 = max(r1, self.rotations_from_center)
            r2 = max(r2, self.rotations_from_center)
            dict_of_points["set_pos_traj"] = [("r1", -r1, accel, vel, decel), ("r2", -r2, accel, vel, decel)]
        else:
            r1 = min(r1, -self.rotations_from_center)
            r2 = min(r2, -self.rotations_from_center)
            dict_of_points["set_pos_traj"] = [("r1", r2, accel, vel, decel), ("r2", r1, accel, vel, decel)]

        self.server.send_to_radius_client(dict_of_points)
        if self.server.receive_from_radius_client() == "Finished writing this point":
            pass

        ##########################################################################################






        theta_speed = theta_speed * (
                self.theta_motor.get_vel_limit() * CAP_THETA_VELOCITY_AT)  # capped max vel to 85% of max speed
        # because I don't want to lose connection to the motor

        time_intervals = [.044]
        self.theta_motor.set_home()
        print("theta motor homed")
        self.theta_motor.set_vel(theta_speed)
        print("set vel to theta motor")
        max_rotations = self.gear_ratio * .5 * period / (2 * pi)
        previous_thetas = [0]
        while self.theta_motor.get_pos() < max_rotations and self.ENABLED:
            start = time.perf_counter()
            percent_complete = self.theta_motor.get_pos() / max_rotations
            print("Percent Complete: " + str(round(percent_complete * 100, 2)) + "%")
            theta1 = self.theta_motor.get_pos() / self.gear_ratio * 2 * pi
            theta2 = theta1 + pi
            previous_thetas.append(theta1 * 180 / pi)

            r1 = eval(equation.replace("theta", "theta1"))
            r2 = eval(equation.replace("theta", "theta2"))

            r1 = scale(r1, smallest_r1, largest_r1, -self.radius_motor_max_rotations * scale_factor,
                       self.radius_motor_max_rotations * scale_factor)
            r2 = scale(r2, smallest_r2, largest_r2, -self.radius_motor_max_rotations * scale_factor,
                       self.radius_motor_max_rotations * scale_factor)

            bandwidth = (1 / np.mean(time_intervals))
            dict_of_points = {}
            if r1 >= 0:
                r1 = max(r1, self.rotations_from_center)
                r2 = max(r2, self.rotations_from_center)
                dict_of_points["set_pos_filter"] = [("r1", -r1, bandwidth), ("r2", -r2, bandwidth)]
            else:
                r1 = min(r1, -self.rotations_from_center)
                r2 = min(r2, -self.rotations_from_center)
                dict_of_points["set_pos_filter"] = [("r1", r2, bandwidth), ("r2", r1, bandwidth)]

            self.server.send_to_radius_client(dict_of_points)
            if self.server.receive_from_radius_client() == "Finished writing this point":
                pass
            end = time.perf_counter()
            time_intervals.append(end - start)

        self.ENABLED = True
        self.theta_motor.set_vel(0)
        method_end_time = time.perf_counter()
        self.server.send_to_radius_client("Finished Drawing Equation")

        return {
            "Time Taken": method_end_time - method_start_time,  # seconds
            "Average Time Difference": np.mean(time_intervals),
            "Average Angle Difference": np.mean(np.diff(previous_thetas)),
            "Min Angle Difference": min(np.diff(previous_thetas)),
            "Max Angle Difference": max(np.diff(previous_thetas))
        }



    def draw_equation_with_1_motor(self, equation: str, period, theta_speed=.75, scale_factor=1):
        method_start_time = time.perf_counter()  # start timing how long the method takes
        self.pre_check(equation, theta_speed)  # validate inputs

        theta_speed = theta_speed * (
                self.theta_motor.get_vel_limit() * CAP_THETA_VELOCITY_AT)  # capped max vel to 85% of max speed
        # because I don't want to lose connection to the motor

        scale_factor = max(min(scale_factor, 1), 0)  # This bounds scale_factor between 0 and 1

        all_r_values = [eval(equation) for theta in np.arange(0, period, pi / 100)]  # calculate all r values

        # find the range of the r values to later deal with scaling them properly.
        smallest_r, largest_r = min(min(all_r_values), 0), max(all_r_values)






        ##################### GO TO FIRST POINT (THIS COULD BE FAR AWAY) #########################
        initial_r = eval(equation.replace("theta", "0"))

        r = scale(initial_r, smallest_r, largest_r, -self.radius_motor_max_rotations * scale_factor,
                   self.radius_motor_max_rotations * scale_factor)
        print(r)

        accel = 2
        vel = 3
        decel = 2

        dict_of_points = {}
        if r >= 0:
            r = max(r, self.rotations_from_center)
            dict_of_points["set_pos_traj"] = [("r1", -r, accel, vel, decel)]
        else:
            r = min(r, -self.rotations_from_center)
            dict_of_points["set_pos_traj"] = [("r2", r, accel, vel, decel)]

        print("sending to client")
        self.server.send_to_radius_client(dict_of_points)
        if self.server.receive_from_radius_client() == "Finished writing this point":
            print("client finished")

        ##########################################################################################





        time_intervals = [.044]
        self.theta_motor.set_home()
        self.theta_motor.set_vel(theta_speed)
        max_rotations = self.gear_ratio * period / (2 * pi)
        previous_thetas = [0]
        # self.server.send_to_radius_client({"point (set_pos)": ("r2", 0)})
        while self.theta_motor.get_pos() < max_rotations and self.ENABLED:
            start = time.perf_counter()

            percent_complete = self.theta_motor.get_pos() / max_rotations
            print("Percent Complete: " + str(round(percent_complete * 100, 2)) + "%")

            theta = self.theta_motor.get_pos() / self.gear_ratio * 2 * pi
            previous_thetas.append(theta * 180 / pi)
            # print("theta1", theta1 * 180 / pi)

            r = eval(equation)
            r = scale(r, smallest_r, largest_r, -self.radius_motor_max_rotations * scale_factor,
                      self.radius_motor_max_rotations * scale_factor)

            bandwidth = (1 / np.mean(time_intervals))
            dict_of_points = {}
            if r >= 0:
                # +
                r = max(r, self.rotations_from_center)
                dict_of_points["set_pos_filter"] = [("r1", -r, bandwidth)]
            else:
                # -
                r = min(r, -self.rotations_from_center)
                dict_of_points["set_pos_filter"] = [("r2", r, bandwidth)]
            # self.r2.wait() Does not work with set_pos_filter
            self.server.send_to_radius_client(dict_of_points)
            if self.server.receive_from_radius_client() == "Finished writing this point":
                pass
            end = time.perf_counter()
            time_intervals.append(end - start)

        self.ENABLED = True
        self.theta_motor.set_vel(0)
        method_end_time = time.perf_counter()
        self.server.send_to_radius_client("Finished Drawing Equation")

        return {
            "Time Taken": method_end_time - method_start_time,  # seconds
            "Average Time Difference": np.mean(time_intervals),
            "Average Angle Difference": np.mean(np.diff(previous_thetas)),
            "Min Angle Difference": min(np.diff(previous_thetas)),
            "Max Angle Difference": max(np.diff(previous_thetas)),
            "STD Angle Difference": np.std(np.diff(previous_thetas))
        }

