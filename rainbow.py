__module_name__ = "rainbow_message"
__module_description__ = "Colors a message to be rainbow when sent to chat."
__module_version__ = "0.1"

import hexchat

def rainbow_message(word, word_eol, userdata):
    if len(word) >= 2:
        i = 0
        c = ["04", "07", "08", "09", "03", "10", "11", "12", "13"]
        # c = ["04", "00", "12"]
        s = ""
        for k in word_eol[1]:
            if not k.isspace():
                s += "\x03" + c[i]
                i = (i + 1) % len(c)
            s += k
        hexchat.command("PRIVMSG {} :{}".format(hexchat.get_info("channel"), s))
        hexchat.emit_print("Your Message", hexchat.get_info("nick"), s, "", "")
    return hexchat.EAT_ALL

hexchat.hook_command("rainbow", rainbow_message)

