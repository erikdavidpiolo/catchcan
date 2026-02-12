from machine import Pin, PWM
from utime import sleep
import math

class Motor:
    def __init__(self, speed, reverse, pin1, pin2, en):
        self.speed = speed
        self.reverse = reverse
        self.in1 = Pin(pin1, Pin.OUT)
        self.in2 = Pin(pin2, Pin.OUT)
        self.en = PWM(Pin(en))
        self.en.freq(5000)
        self.en.duty_u16(self.speed)

    def set_speed(self, speed):
        """Update the motor speed dynamically."""
        self.speed = speed
        self.en.duty_u16(self.speed)

    def forward(self, speed=None):
        """Move the motor forward at the specified speed."""
        if speed is not None:
            self.set_speed(speed)
        self.in1.value(1)
        self.in2.value(0)

    def backward(self, speed=None):
        """Move the motor backward at the specified speed."""
        if speed is not None:
            self.set_speed(speed)
        self.in1.value(0)
        self.in2.value(1)

    def brake(self):
        """Stop the motor."""
        self.in1.value(1)
        self.in2.value(1)

m1 = Motor(65535, "brake", 13, 14, 15) #bottom right
m2 = Motor(65535, "brake", 3, 4, 5) #bottom left
m3 = Motor(65535, "brake", 6, 7, 8) #top left
m4 = Motor(65535, "brake", 9, 10, 11) #top right

def drive_forward(speed=65535):
    m1.forward(speed)
    m2.forward(speed)
    m3.forward(speed)
    m4.forward(speed)

def drive_backward(speed=65535):
    m1.backward(speed)
    m2.backward(speed)
    m3.backward(speed)
    m4.backward(speed)

def drive_left(speed=65535):
    m1.backward(speed)
    m2.forward(speed)
    m3.backward(speed)
    m4.forward(speed)

def drive_right(speed=65535):
    m1.forward(speed)
    m2.backward(speed)
    m3.forward(speed)
    m4.backward(speed)

def drive_diagonal_forward_left(speed=65535):
    m1.brake()
    m2.forward(speed)
    m3.brake()
    m4.forward(speed)

def drive_diagonal_forward_right(speed=65535):
    m1.forward(speed)
    m2.brake()
    m3.backward(speed)
    m4.brake()

def drive_diagonal_backward_left(speed=65535):
    m1.backward(speed)
    m2.brake()
    m3.backward(speed)
    m4.brake()

def drive_diagonal_backward_right(speed=65535):
    m1.brake()
    m2.backward(speed)
    m3.brake()
    m4.backward(speed)

def drive_angle(angle, speed):
    trueAngle = angle
    ratio = math.tan(angle)
    if(angle == 0 or angle == 360):
        drive_right(speed)
    elif(angle > 0 and angle < 90):
        #ratio = m1/m3
        m1.forward(speed)
        m3.forward(speed/ratio)
        m2.brake()
        m4.brake()
    elif(angle == 90):
        drive_forward(speed)
    elif(angle > 90 and angle < 180):
        trueAngle = 180 - angle
        #ratio = m2/m4
        m2.forward(speed)
        m4.forward(speed/ratio)
        m1.brake()
        m3.brake()
    elif(angle == 180):
        drive_left(speed)
    elif(angle > 180 & angle < 270):
        trueAngle = angle - 180
        #ratio = m3/m1
        m3.backward(speed)
        m1.backward(speed/ratio)
        m2.brake()
        m4.brake()
    elif(angle == 270):
        drive_backward(speed)
    elif(angle > 270 & angle < 360):
        trueAngle = angle - 270
        #ratio = m4/m2
        m4.backward(speed)        
        m2.backward(speed/ratio)
        m1.brake()
        m3.brake()

def stop():
    m1.brake()
    m2.brake()
    m3.brake()
    m4.brake()

m1.brake()
m2.brake()
m3.brake()
m4.brake()

motors = [m1, m2, m3, m4]

for motor in motors:
    print("Turning on motor {}".format(motors.index(motor)))
    motor.forward(32768)  # Example: Half speed
    sleep(2)
    print("Turning off motor {}".format(motors.index(motor)))
    motor.brake()
    sleep(2)