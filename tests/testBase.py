class TestBase():
  conf = 'tests/test_pybotrc'
  def testConfExistence(self):
    f = open (TestBase.conf)
    assert f is not None

  def testConfman(self):
    import confman
    cm = confman.ConfManager(TestBase.conf)

  def testBase(self):
    import bot
    import confman
    assert bot.Bot(confman.ConfManager(TestBase.conf), "zero9f9.com") is not None, "bot is None!"

  # this one you might want to remove, since it connects to a hardcoded ircd
  def testBotSocket(self):
    import bot
    import confman
    b = bot.Bot(confman.ConfManager(TestBase.conf), "zero9f9.com", True)
    b.worker(mock=True)
    assert b.s is not None

  # if this fails someone screwed something up
  def testEventMatches(self):
    import event
    e = event.Event('__.test__')
    assert e is not None
    assert e._type is not None and e._type == "__.test__"
    e.define(msg_definition="^test")
    assert e.msg_definition == "^test"
    assert e.matches(":hlmtre!~hlmtre@bxr.bxr.bxr PRIVMSG #bots :test") == True

  def testLoad(self):
    import bot
    import confman
    b = bot.Bot(confman.ConfManager(TestBase.conf), "zero9f9.com", True)
    b.load_modules()
    assert len(b.loaded_modules) > 0
