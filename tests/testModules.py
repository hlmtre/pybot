class TestModules():
  def testBaseModule(self):
    from modules.basemodule import BaseModule

  def testExtension(self):
    import bot
    import confman
    from modules.basemodule import BaseModule
    b = bot.Bot(confman.ConfManager("pybotrc"), "zero9f9.com", True)

    class testExtended(BaseModule):
      def post_init(self):
        pass

    assert issubclass(testExtended, BaseModule)
