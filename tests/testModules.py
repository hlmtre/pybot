class TestModules():
    irc_server = "irc.zero9f9.com"

    def testBaseModule(self):
        from modules.basemodule import BaseModule

    def testExtension(self):
        import bot
        import confman
        from modules.basemodule import BaseModule
        b = bot.Bot(
            confman.ConfManager("pybotrc"),
            TestModules.irc_server,
            d=False)

        class testExtended(BaseModule):
            def post_init(self):
                pass

        assert issubclass(testExtended, BaseModule)
