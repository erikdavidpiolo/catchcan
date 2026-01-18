from machine import Pin,PWM
from utime import sleep

class Motor:
    def __init__(self, speed, reverse, pin1, pin2, en):
        self.speed =  speed
        self.reverse = reverse
        self.in1 = Pin(pin1, Pin.OUT)
        self.in2 = Pin(pin2, Pin.OUT)
        self.en = PWM(Pin(en))
        self.en.freq(5000)
        self.en.duty_u16(self.speed)

    def forward(self):
        self.in1.value(1)
        self.in2.value(0)

    def backward(self):
        self.in1.value(0)
        self.in2.value(1)

    def brake(self):
        self.in1.value(1)
        self.in2.value(1) 

m1 = Motor(65535, "brake", 13, 14, 15)
m2 = Motor(65535, "brake", 3, 4, 5)
m3 = Motor(65535, "brake", 6, 7, 8)
m4 = Motor(65535, "brake", 9, 10, 11)

def drive_forward():
    m1.forward()
    m2.forward()
    m3.forward()
    m4.forward()

def drive_backward():
    m1.backward()
    m2.backward()
    m3.backward()
    m4.backward()

def drive_left():
    m1.backward()
    m2.forward()
    m3.backward()
    m4.forward()

def drive_right():
    m1.forward()
    m2.backward()
    m3.forward()
    m4.backward()

def stop():
    m1.brake()
    m2.brake()
    m3.brake()
    m4.brake()

m1.brake()
m2.brake()
m3.brake()
m4.brake()

motors = [m1,m2,m3,m4]

for motor in motors:
    print("Turning on motor {}".format(motors.index(motor)))
    motor.forward()
    sleep(2)
    print("Turning off motor {}".format(motors.index(motor)))
    motor.brake()
    sleep(2)

   