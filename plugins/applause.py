from . import bot
import re

@bot.firehose
def listen(message, args):
    # Attempt to strip out URLs
    message= re.sub('(https?|ftp)://\S+', '', message)

    pattern = "applau(d|se)|bravo|slow clap"
    m = re.search(pattern, message, re.IGNORECASE)
    if m:
        image = 'http://i.imgur.com/9Zv4V.gif'
        bot.speak(image)
