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

  # this one you might want to remove, since it connects to a hardcoded ircd
  #TODO FIXME
#  def testBotSocket(self):
#    import bot
#    import confman
#    from subprocess import call
#    b = bot.Bot(confman.ConfManager("pybotrc"), "zero9f9.com", True)
#    b.worker()
#    assert b.s is not None
#    b.exit()

  # if this fails someone screwed something up
  def testEventMatches(self):
    import event
    e = event.Event('__.test__')
    assert e is not None
    assert e._type is not None and e._type == "__.test__"
    e.define(msg_definition="^test")
    assert e.msg_definition == "^test"
    assert e.matches(":hlmtre!~hlmtre@bxr.bxr.bxr PRIVMSG #bots :test") == True
