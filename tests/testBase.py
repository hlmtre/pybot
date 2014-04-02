class TestBase():
  def testConfExistence(self):
    f = open ('pybotrc')
    assert f is not None

  def testConfman(self):
    import confman
    cm = confman.ConfManager("pybotrc")

  def testBase(self):
    import bot
    import confman
    assert bot.Bot(confman.ConfManager("pybotrc"), "zero9f9.com") is not None, "bot is None!"

  # we cannot test initializing the bot yet, because threading is hard.
  # this currently does not work.
  #def testSocket(self):
  #  import bot
  #  import confman
  #  from subprocess import call
  #  b = bot.Bot(confman.ConfManager("pybotrc"), "zero9f9.com", True)
  #  b.start()
  #  # make sure the socket has actually been initialized
  #  import time
  #  time.sleep(5)
  #  assert b.s is not None, "socket is none!"
  #  # since we're threaded and we've started the thread, we have to kill the process
  #  # TODO
