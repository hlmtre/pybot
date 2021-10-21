from util import commands


@commands(".mock")
def mock(bot, message, channel):
    replace_string = ""
    i = 0
    for letter in message.replace(".mock ", ""):
        if i % 2 == 0:
            replace_string += letter.upper()
        else:
            replace_string += letter
        i += 1

    bot.say(channel, replace_string)
