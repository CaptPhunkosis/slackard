from . import bot

@bot.subscribe('^.compliment')
def compliment(message, args):
    user_info = bot.fetch_user_info(args['user'])
    bot.speak("Gee <@%s>...you're pretty swell. Can I still call you %s?" % (user_info["id"], user_info['real_name']))
