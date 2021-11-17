from serial import Serial

serial = Serial(port='/dev/ttyACM1', baudrate=115200)
serial.reset_input_buffer()
serial.reset_output_buffer()
if serial.in_waiting:
    serial.read(serial.in_waiting)

while True:
    print(serial.read(1))
