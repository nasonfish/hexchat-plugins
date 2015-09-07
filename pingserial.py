__module_name__ = "rainbow_message"
__module_description__ = "Colors a message to be rainbow when sent to chat."
__module_version__ = "0.1"

import hexchat
import serial

def highlight_cb(word, word_eol, userdata):
    try:
        ser = serial.Serial('/dev/ttyUSB0', 9600)
    except serial.serialutil.SerialException:
        return hexchat.EAT_NONE
    ser.write('1')
    ser.close()
    return hexchat.EAT_NONE

hexchat.hook_print("Channel Msg Hilight", highlight_cb)

