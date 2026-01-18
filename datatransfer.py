import machine
import time

uart1 = machine.UART(1,baudrate=9600,tx=machine.Pin(4),rx=machine.Pin(5),timeout=1000)
while True:
    print(uart1.read())
    time.sleep(0.1)
    
