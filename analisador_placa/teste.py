import serial
ser = serial.Serial('COM9')  # open serial port
print(ser.name)         # check which port was really used
ser.write(b'*IDN?')     # write a string
b = ser.readline()
ser.close()             # close port
print(b)