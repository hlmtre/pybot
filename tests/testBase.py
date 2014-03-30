def testConfExistence():
  f = open ('pybotrc')
  assert f is not None

def testConfman():
  import confman
  cm = confman.ConfManager("pybotrc")

def testBase():
  import bot
  import confman
  assert bot.Bot(confman.ConfManager("pybotrc"), "zero9f9.com") is not None, "bot is None!"
