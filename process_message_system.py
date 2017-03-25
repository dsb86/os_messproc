import os
import sys

class MessageProc:

    def __init__(self):

        # d
        self.test = None

    def main(self):
        self.test = None

    def start(self):
        os.fork()
        self.main()
        sys.exit()


