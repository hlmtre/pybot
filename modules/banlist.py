import sys
from event import Event
try:
    if sys.version_info > (3, 0, 0):
        from .basemodule import BaseModule
    else:
        from basemodule import BaseModule
except (ImportError, SystemError):
    from modules.basemodule import BaseModule


class BanList(BaseModule):
    def post_init(self):
        banlistevent = Event("__.banlisteventevent__")
        banlistevent.define(msg_definition="^\\.pban")
        banlistevent.subscribe(self)

        self.help = ".pban <map>"
        # register ourself to our new d20event event
        self.bot.register_event(banlistevent, self)
        self.map_to_ops = {
            "themepark": [
                "Thatcher/Thermite",
                "Jager/Lesion"],
            "oregon": [
                "Thatcher/Maverick",
                "Kaid/Mira/Vigil/Lesion"],
            "bank": [
                "Thatcher/Thermite",
                "Mira/Smoke"],
            "border": [
                "Thatcher/Kali",
                "Jager/Echo"],
            "chalet": [
                "Thatcher/Kali",
                "Valkyrie/Echo"],
            "clubhouse": [
                "Thatcher/Kali",
                "Kaid/Jager"],
            "coastline": [
                "Blackbeard/Nomad",
                "Valkyrie/Pulse/Mira"],
            "consulate": [
                "Thatcher/Kali",
                "Valkyrie/Maestro"],
            "kafe": [
                "Gridlock/Jackal/Maverick",
                "Valkyrie/Pulse/Lesion"],
            "kanal": [
                "Thatcher/Maverick",
                "Clash/Echo/Jager"],
            "outback": [
                "Thatcher/Capitao/Gridlock",
                "Clash/Mira/Bandit"],
            "villa": [
                "Blackbeard/IQ/Buck",
                "Clash/Ela"]}

    def handle(self, event):
        try:
            l = event.msg.split(None, 1)
            if len(l) > 1:
                resp = self.map_to_ops[l[1].lower()]
                self.say(
                    event.channel,
                    "Attack: " +
                    resp[0] +
                    ", Defense: " +
                    resp[1])
        except BaseException:
            self.say(event.channel, "you goofed, you goof")
