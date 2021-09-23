class TestBase():
  conf = 'tests/test_pybotrc'
  irc_server = 'irc.zero9f9.com'

  def testConfExistence(self):
    f = open (TestBase.conf)
    assert f is not None

  def testConfman(self):
    import confman
    cm = confman.ConfManager(TestBase.conf)

  def testBase(self):
    import bot
    import confman
    assert bot.Bot(d=False, conf=confman.ConfManager(TestBase.conf), network=TestBase.irc_server) is not None, "bot is None! Check tests/test_pybotrc for reachable IRC server."

  # this one you might want to remove, since it connects to a hardcoded ircd
  def testBotSocket(self):
    import bot
    import confman
    b = bot.Bot(d=False, conf=confman.ConfManager(TestBase.conf), network=TestBase.irc_server)
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
    assert e.matches(":hlmtre!~hlmtre@bxr.bxr.bxr PRIVMSG #bots :test")

  def testLoad(self):
    import bot
    import confman
    b = bot.Bot(conf=confman.ConfManager(TestBase.conf), network=TestBase.irc_server, d=False)
    b.load_modules()
    assert len(b.loaded_modules) > 0
