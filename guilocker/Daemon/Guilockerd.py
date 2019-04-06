from guilocker.Daemon.Module import daemon
from guilocker.Core.GuiLocker import GuiLocker
from guilocker.Core.Module import Core

class GuiDaemon(daemon):
    def __init__(self, pidfile):
        daemon.__init__(self, pidfile)
        self.g = GuiLocker()
        self.c = Core()

    def run(self):
        while True:
            try:
                self.g.run()
            except Exception as e:
                pass
                """test"""

    def umount(self):
        device = self.c.get_mounted_device()
        try:
            self.c.umount(device)
        except Exception as e:
            print(e)

