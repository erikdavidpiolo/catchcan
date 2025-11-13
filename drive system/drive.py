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

m1 = Motor(50000, "brake", 0, 1, 2)
m2 = Motor(50000, "brake", 3, 4, 5)
m3 = Motor(50000, "brake", 6, 7, 8)
m4 = Motor(50000, "brake", 9, 10, 11)

while True:
    print("Turning on motor")
    m1.forward()
    m2.forward()
    m3.forward()
    m4.forward()
    sleep(2)
    m1.brake()
    m2.brake()
    m3.brake()
    m4.brake()
    sleep(2)
    m1.backward()
    m2.backward()
    m3.backward()
    m4.backward()
    sleep(2)
