from cmdrinterface import Commander

theboy = Commander(COM9)


"""import serial
import time
ser = serial.Serial('COM9')  # open serial port
print(ser.name)         # check which port was really used
ser.write(b'*CONN')     # write a string
b = ser.readline()
time.sleep(0.2)
print(b)
ser.write(b'*FUCKU')
b = ser.readline()
time.sleep(0.2)
print(b)
for _ in range(0,20):
    ser.write(b'*MOVY-')     # write a string
    b = ser.readline()
    b = ser.readline()
    
    time.sleep(0.2)
    print(b)
ser.close()             # close port"""