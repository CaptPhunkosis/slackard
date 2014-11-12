from . import bot

@bot.subscribe('^.compliment', include_user_info=True)
def compliment(message, user_info):
    bot.speak("Gee <@%s>...you're pretty swell." % user_info["id"])
