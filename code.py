'''
IMPORTS
'''
import board
import usb_cdc
from time import monotonic_ns
from busio import I2C
from digitalio import DigitalInOut, Pull
from HT16K33segment14 import HT16K33Segment14

'''
CONSTANTS
'''
DELAY = 0.01
PAUSE = 3
DEBUG = True
DISPLAY_COUNT = 2


'''
FUNCTIONS
'''
def log(msg):
    if DEBUG: print(msg)


'''
RUNTIME START
'''
if __name__ == '__main__':
    # Get the USB data feed object
    serial = usb_cdc.data

    # Set up I2C and instantiate the display
    i2c = I2C(board.SCL, board.SDA)
    while not i2c.try_lock(): pass
    displays = []
    displays.append(HT16K33Segment14(i2c, 0x71))
    displays.append(HT16K33Segment14(i2c, 0x70))
    displays[0].set_brightness(2)
    displays[1].set_brightness(2)
    buffer = bytearray(8)

    # Set up the BOOT button
    button = DigitalInOut(board.BUTTON)
    button.switch_to_input(pull=Pull.UP)

    # Run-loop management Flags, etc.
    boot_released = False
    boot_pressed = False
    debounce_timer = 0
    last_display_update = 0
    in_data = bytearray()
    out_data = b'WAITING+++'
    out_index = 0

    # Run loop
    while True:
        # Get the nanosecond counter value
        now = monotonic_ns()

        # Button pressed? Debounce the press, then
        # debounce the release
        if not button.value:
            if debounce_timer == 0:
                debounce_timer = now
            else:
                if now > debounce_timer + 20000000:
                    debounce_timer = 0
                    boot_pressed = True
        elif boot_pressed:
            if debounce_timer == 0:
                debounce_timer = now
            else:
                if now > debounce_timer + 20000000:
                    debounce_timer = 0
                    boot_pressed = False
                    boot_released = True
                    out_data = bytearray()

        if now - last_display_update > 400000000:
            last_display_update = now

            displays[0].clear()
            displays[1].clear()

            # Write a chunk of input string to the display buffer
            if len(out_data) > 0:
                a = out_index
                for i in range(0, 8):
                    try:
                        buffer[i] = out_data[a]
                    except IndexError:
                        print(i, a)
                    a += 1
                    if a >= len(out_data): a -= len(out_data)
                out_index += 1
                if out_index >= len(out_data): out_index = 0

            # Output the display buffer
            for i in range(0, 8):
                if i < 4:
                    displays[0].set_character(chr(buffer[i]), i)
                else:
                    displays[1].set_character(chr(buffer[i]), i - 4)
            displays[0].draw()
            displays[1].draw()

        # Check for incoming data
        if serial.in_waiting > 0:
            byte = serial.read(1)
            if byte == b'\r':
                log(in_data.decode("utf-8"))
                out_data = in_data
                out_data += b'  '
                in_data = bytearray()
                out_index = 0
            else:
                in_data += byte
                if len(in_data) == 129:
                    in_data = in_data[128] + in_data[1:127]
