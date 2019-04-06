import sys, os, time, atexit, signal

"""
Ref by https://gist.github.com/andreif/cbb71b0498589dac93cb
"""
class daemon:
    def __init__(self, pidfile):
        self.pidfile = pidfile

    def __delete_pid(self):
        os.remove(self.pidfile)

    def daemonize(self):
        """Daemonize class"""

        # create child
        try:
            pid = os.fork()
            if pid > 0:
                # suicide parent
                sys.exit(0)
        except OSError as err:
            sys.stderr.write(f'fork failed: {err}')
            sys.exit(-1)

        # adopted init child
        os.chdir('/')
        os.setsid()
        os.umask(0)

        # redirect file descriptor 0, 1, 2 (stdin, stdout, stderr) to /dev/null
        sys.stdout.flush()
        sys.stderr.flush()
        stdi = open(os.devnull, 'r')
        stdo = open(os.devnull, 'a+')
        stde = open(os.devnull, 'a+')

        os.dup2(stdi.fileno(), sys.stdin.fileno())
        os.dup2(stdo.fileno(), sys.stdout.fileno())
        os.dup2(stde.fileno(), sys.stdout.fileno())

        atexit.register(self.__delete_pid)

        pid = os.getpid()
        with open(self.pidfile, 'w+') as f:
            f.write(str(pid) + '\n')

    def start(self):
        try:
            with open(self.pidfile, 'r') as pf:
                pid = int(pf.read().strip())
        except IOError:
            pid = None

        if pid:
            message = f"pidfile {self.pidfile} already exist. Please check daemon already running."
            sys.stderr.write(message)
            sys.exit(1)

        self.daemonize()
        try:
            self.run()
        except Exception as e:
            message = "It seems daemon library using without inherit. " +\
                             f"Please override self.run(). ERROR: {e}"
            sys.stderr.write(message)

    def stop(self):
        try:
            with open(self.pidfile, 'r') as pf:
                pid = int(pf.read().strip())
        except IOError:
            pid = None

        if not pid:
            message = f"pidfile {self.pidfile} does not exist. Please check daemon running."
            sys.stderr.write(message)
            sys.exit(1)

        try:
            while True:
                os.kill(pid, signal.SIGTERM)
                time.sleep(0.1)
        except OSError as e:
            if os.path.exists(self.pidfile):
                os.remove(self.pidfile)
            else:
                print(e)
                sys.exit(1)

    def restart(self):
        self.stop()
        self.start()

    # TODO: make status
    def status(self):
        """status"""
