import os
import sys
import pickle
import threading
import time

ANY = any

class Message:
    def __init__(self, name_in, action_in):
        self.name = name_in
        self.action = action_in

    def get_name(self):
        return self.name

    def get_action(self):
        return self.action

class MessageProc:

    def __init__(self):

        self.pid = None
        self.pipe_name = None
        self.communication_queue

    def main(self):
        # set pid and pipe name
        self.pid = os.getpid()
        self.pipe_name = "/tmp/{}.pkl".format(self.pid)

    def start(self):
        # fork
        pid = os.fork()

        if pid == 0:
            # run main in child process
            self.main()
            sys.exit()
        else:
            # register child with parent
            return pid

    def extract_from_pipe(self, arrived_condition):

        if not os.path.exists(self.pipe_name):
            os.mkfifo(self.pipe_name)

        with open(self.pipe_name, 'rb') as unpickle_file:
            while True:
                try:
                    line = pickle.load(unpickle_file)

                    with arrived_condition:
                        self.communication_queue.put(line)
                        arrived_condition.notify()
                except EOFError:
                    time.sleep(0.01)

    def give(self, pid, arg):
        # open desired pipe file for writing
        pipe_out = "/tmp/{}.pkl".format(pid)
        pickle_file = open(pipe_out, 'wb', buffering = 0)
        # pickle data
        pickle.dump(arg, pickle_file)
        # close pickle file
        pickle_file.close()

    def recieve(self, *messages):
        dictionary = {}
        for message in messages:
            key = message.get_name()
            value = message.get_action()
            dictionary[key]=value

        arrived_condition = threading.Condition()
        transfer_thread = threading.Thread(target=self.extract_from_pipe(arrived_condition), daemon=True)
        transfer_thread.start()





