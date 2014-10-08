# coding=utf-8
from util import commands

@commands(".test",".lel")
def test_function(bot, message):
  print bot
  print message
  print "TEST FUNCTION"
