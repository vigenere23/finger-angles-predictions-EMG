from serial import Serial

serial = Serial(port='/dev/ttyACM1', baudrate=115200)
serial.reset_input_buffer()
serial.reset_output_buffer()

while True:
    serial.read(serial.in_waiting)
    print(serial.read(1))
