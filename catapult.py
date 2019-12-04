from pybricks import ev3brick as brick
from pybricks.ev3devices import (Motor)
from pybricks.parameters import (Stop, Direction)

# This code assumes that the linear actuator is correctly setup manually by ensuring
# that the splint part of the actuator is inside of the driving gear and aligned with the
# black plastic completely, without being inside of the grey area of the gear
class Catapult:
    # The servo motor at the base of the catapult
    # Enables drawing the arm back
    base_motor = None

    # The linear actuator at the base of the catapult
    # Enables locking the drive mechanism and releasing it once loaded
    linear_actuator = None

    # The current percentage of the retraction
    retract_percentage = None

    # Whether or not the catapult is in a safe (controlled) state
    safe = False

    # The time to retract the entire span of the arm is 47 seconds for the white version, with full batteries
    # The time to retract the entire span of the arm is 52 seconds for the black version, with full batteries
    time_to_retract = 47

    # Constructor for the robot arm
    def __init__(self, base_motor_port, linear_actuator_port, time_to_retract=None):
        # Initialize the base servo motor
        self.base_motor = Motor(base_motor_port, Direction.CLOCKWISE)
        # Initialize the linear actuator
        self.linear_actuator = Motor(linear_actuator_port, Direction.CLOCKWISE)

        if time_to_retract is not None:
            self.time_to_retract = time_to_retract

    # Reset the robot arm
    # Ensure that the splint is able to cleany enter the driving gear completely
    # Ensure that the actuator retracts to the start of its course
    # This is a manual process
    def reset(self):
        # Retract the linear actuator completely to ensure that the catapult is disarmed
        self.linear_actuator.run_until_stalled(-100)
        # Extend the actuator to its maximum position to ensure clearence through the driving gear
        self.linear_actuator.run_time(100, 1500)
        # Retract the actuator again
        self.linear_actuator.run_until_stalled(-100)
        # Extend it to its starting position so that it can follow the driving gear
        self.linear_actuator.run_time(100, 900)

        self.retract_percentage = 0
        self.safe = True

    # Lock the driving gear using the linear actuator
    def safe_lock(self):
        if not self.safe:
            return

        self.linear_actuator.run_time(100, 650)

    # Unlock the driving gear using the linear actuator
    def safe_unlock(self):
        if not self.safe:
            return

        # The retraction is about 20% faster than extending the actuator
        # We must account for this
        self.linear_actuator.run_time(-100, 570)

    # Unlock the driving gear using the linear actuator
    def unlock(self):
        self.safe = False

        # This line is repeated so that the only stall is when it has retracted completely
        for i in range(3):
            self.linear_actuator.run_until_stalled(-100)

    # Retract the catapult arm a certain absolute percentage
    # This code assumes that the string attached to the catapult's arm
    # has full tension when the arm is rotated fully and pressed against
    # the catapult's base plate
    def retract(self, percentage):
        # Only allow percentages within the safety span
        if percentage < 0 or percentage > 100:
            return

        self.safe = False

        # Start drawing the arm back without waiting for it to complete
        self.base_motor.run_time(9000, self.time_to_retract * 1000 * (percentage / 100), True)
        while True:
            if self.base_motor.stalled() or self.base_motor.speed() == 0:
                self.base_motor.stop()
                return
