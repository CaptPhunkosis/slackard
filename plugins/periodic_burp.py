from . import bot

def periodic_burp():
    bot.speak(":fire: :fire: _Buuuuuuuuuuuuuuuurp..._ :fire: :fire: ...sorry. :skull:")

bot.add_periodic_event(periodic_burp, 10, "periodic_burp")
