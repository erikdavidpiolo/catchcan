from machine import UART, Pin
import time
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

# UART0: GP0 = TX, GP1 = RX
uart = UART(0, baudrate=115200, tx=Pin(0), rx=Pin(1))

# LED pin (CHANGE THIS if needed)
LED_PIN = 16          # GP16 for external LED
# LED_PIN = 25        # uncomment this instead for built-in LED

led = Pin(LED_PIN, Pin.OUT)
led.value(0)          # LED OFF at startup

# Optional: let the Pi know Pico is alive
uart.write("READY\n")
print("Ready")


m1 = Motor(65535, "brake", 1, 2, 3)
m2 = Motor(65535, "brake", 3, 4, 5)
m3 = Motor(65535, "brake", 6, 7, 8)
m4 = Motor(65535, "brake", 9, 10, 11)

while True:
    if uart.any():
        line = uart.readline()
        if line:
            try:
                cmd = line.decode("utf-8").strip()
            except:
                cmd = ""

            if cmd == "FIRE":
                led.value(1)
                m1.forward()
                # m2.forward()
                # m3.forward()
                # m4.forward()
                uart.write("OK_ON\n")

            elif cmd == "LED_OFF":
                led.value(0)
                m1.brake()
                # m2.brake()
                # m4.brake()
                # m3.brake()
                uart.write("OK_OFF\n")

            else:
                uart.write("UNKNOWN\n")

    time.sleep(0.01)