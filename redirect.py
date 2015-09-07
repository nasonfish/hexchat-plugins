__module_name__ = "redirect"
__module_description__ = "Provides an interface for filtering/redirecting messages"
__module_version__ = "0.1"

# /redirect text_event regex network channel target
# (network, channel, and target can be "0" for "any"/"none")
# /redirects
# /redirects delete id

import hexchat
import re
import os
import shlex
import json

CONFIG_FILE = ".config/hexchat/filter.conf"

class Redirect:
    def __init__(self, command, regex, network=None, channel=None, target=None, handler=None):
        self.command = command
        self.regex = regex
        self.network = None if (network == "0") else network
        self.channel = None if (channel == "0") else channel
        self.target = None if (target == "0") else target
        self.handler = handler
    def serialize(self):
        return dict(command=self.command, regex=self.regex, network=self.network,
                    channel=self.channel, target=self.target)
        


if not os.path.isfile(CONFIG_FILE):
    with open(CONFIG_FILE, "w") as f:
        json.dump({"redirects": []}, f)

with open(CONFIG_FILE, "r") as f:
    config = json.load(f)

def to_redirect(args):
    return Redirect(**args)

redirects = config['redirects']
redirects = map(to_redirect, redirects)

"""
redirects:
[{
"command": "...",
"regex": "...",
"network": None or "",
"channel": None or ""
"target": None or "",
}, ...]

"""

def do_hook(redir):
    def _hook(*args, **kwargs):
        if hexchat.get_info("channel") == redir.target:
            return hexchat.EAT_NONE  # nothing to do
        if redir.network and redir.network != hexchat.get_info("network"):
            return hexchat.EAT_NONE
        if redir.channel and redir.channel != hexchat.get_info("channel"):
            return hexchat.EAT_NONE
        if re.search(redir.regex, '|'.join(args[0])):  # args[1] is word_eol
            if redir.target:
                ctx = hexchat.find_context(channel=redir.target)
                if ctx == None:
                    hexchat.command("query " + redir.target)
                    ctx = hexchat.find_context(channel=redir.target)
                ctx.emit_print(redir.command, *args[0])
            return hexchat.EAT_ALL
        return hexchat.EAT_NONE
    print("Hooking \x0303{command}\x0f with regex \x0303{regex}\x0f (\x0304{network}\x0f/\x0304{channel}\x0f) => \x0305{target}\x0f".format(**redir.serialize()))
    redir.handler = hexchat.hook_print(redir.command, _hook)
    

# upon startup
for i in redirects:
    do_hook(i)

def redirect_command(word, word_eol, userdata):
    args = word[1:]  # already split by quotes, just remove the "redirect" at the beginning of the list
    # word[1:] is all arguments, as word[0] is the command
    if len(args) < 2:
        print("Usage: /redirect text_event regex network channel target")
        return hexchat.EAT_ALL
    redir = Redirect(*args)
    do_hook(redir)
    redirects.append(redir)
    with open(CONFIG_FILE, 'w') as f:
        json.dump({"redirects": [redir.serialize() for redir in redirects]}, f)
    return hexchat.EAT_ALL

def redirect_help(word, word_eol, userdata):
    if len(word) == 1:
        for i,val in enumerate(redirects):
            print "#{id}: \x0303{command}\x0f with regex \x0303{regex}\x0f (\x0304{network}\x0f/\x0304{channel}\x0f) => \x0305{target}\x0f".format(id=i, **val.serialize())
    if len(word) == 3 and word[1] == "delete":
        d=False
        for i,val in enumerate(redirects):
            if str(i) == word[2]:
                hexchat.unhook(redirects[i].handler)
                del(redirects[i])
                with open(CONFIG_FILE, 'w') as f:
                    json.dump({"redirects": [redir.serialize() for redir in redirects]}, f)
                print("Deleted #{id}".format(id=i))
                d=True
        if d is False:
            print("Could not find #{id}".format(id=i))
    return hexchat.EAT_ALL

hexchat.hook_command("redirects", redirect_help)
hexchat.hook_command("redirect", redirect_command)
