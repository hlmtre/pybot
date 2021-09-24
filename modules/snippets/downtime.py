import random

from util import commands, parse_line


@commands(".downtime")
def _downtime(bot, message, channel):
    drinks = [
        'a beer',
        'a scotch',
        'a bloody mary',
        'a nice glass of wine',
        'FUCKIN FOUR LOKO',
        'a crisp cider',
        'a margarita from BoneKin and Jennos\'s house']
    action_string = "\001ACTION "
    user = parse_line(message).user
    if user.lower() == "george" or "thorogood" in user.lower():
        bot.say(channel, action_string + ' gets ' + user +
                ' one bourbon, one scotch, one beer' + "\001\n")
    else:
        bot.say(
            channel,
            action_string +
            ' gets ' +
            user +
            ' ' +
            random.choice(drinks) +
            "\001\n")
