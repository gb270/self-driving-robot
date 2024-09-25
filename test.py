import serial
import time

ser = serial.Serial('/dev/ttyACM0', 9600)
time.sleep(2)

"""
F: Forward
B: Backward
L: Left
R: Right
Q: Forward Left
E: Forward Right
A: Backward Left
D: Backward Right

X: Exit program
"""

print("Enter X/x to exit program.")
direction = ""
valid_directions = ['F', 'B', 'L', 'R', 'Q', 'E', 'A', 'D']

while direction != 'X':
    direction = input("Input direction: ")
    direction = str(direction)
    if direction in valid_directions:
        ser.write(bytes(direction, 'utf-8'))
        print(f"Accepted command: {direction}")

        if ser.in_waiting > 0:
            received = ser.readline().decode('utf-8').rstrip()
            print("Received:", received)

    elif direction == 'X' or direction == 'x':
        print("exiting program")
        break
    
    else:
        print("Not a valid direction.")


ser.close()