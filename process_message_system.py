import os
import sys
import pickle
import threading
import time
import queue

ANY = any

class Message:
    def __init__(self, name_in, **action_in):
        self.name = name_in
        self.action = action_in

    def get_name(self):
        return self.name

    def get_action(self):
        return self.action

class MessageProc:

    def __init__(self):

        self.my_pid = None
        self.pipe_name = None
        self.communication_queue = None
        self.arrived_condition = None
    def main(self):
        # set pid and pipe name
        self.my_pid = os.getpid()
        self.pipe_name = "/tmp/{}.pkl".format(self.my_pid)
        self.communication_queue = queue.Queue()
        self.arrived_condition = threading.Condition()
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

    def extract_from_pipe(self):

        if not os.path.exists(self.pipe_name):
            os.mkfifo(self.pipe_name)

        with open(self.pipe_name, 'rb') as unpickle_file:
            while True:
                try:
                    line = pickle.load(unpickle_file)
                    
                    with self.arrived_condition:
                        self.communication_queue.put(line)

                        self.arrived_condition.notify()
                except EOFError:
                    time.sleep(0.01)


    def give(self, pid, label, *arg):

        # open desired pipe file for writing
        pipe_out = "/tmp/{}.pkl".format(pid)
        while not os.path.exists(pipe_out):
            time.sleep(0.01)
        pickle_file = open(pipe_out, 'wb', buffering = 0)
        # pickle data

        pickle.dump((label, arg), pickle_file)
        # close pickle file
        pickle_file.close()

    def receive(self, *messages):

        dictionary = {}
        for message in messages:
            key = message.get_name()
            value = message.get_action()
            dictionary[key]=value

        # arrived_condition = threading.Condition()
        transfer_thread = threading.Thread(target=self.extract_from_pipe, daemon=True)

        transfer_thread.start()


        while True:
            with self.arrived_condition:
                self.arrived_condition.wait()

                arg = self.communication_queue.get()
                try:
                    return dictionary[arg[0]]['action'](arg[1][0])
                except KeyError:
                    return dictionary[ANY]['action']()
                except IndexError:
                    return dictionary[arg[0]]['action']()



