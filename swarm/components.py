from __future__ import absolute_import
import argparse
import time
from random import random
import Queue
import subprocess
from math import exp

from swarm.managers import make_server, make_client

class SwarmServer(object):
    def __init__(self, function, port, authkey):
        """A server containing input and output queues, and a function to
        map inputs over. A connecting client can read the stored function,
        apply it to items in the input queue and post back to the output
        queue

        :param function: function to apply to inputs
        :param port: port over which to server
        :param authkey: authorization key

        """
        self.manager = make_server(function, port, authkey)
        self.job_q = self.manager.get_job_q()
        self.result_q = self.manager.get_result_q()
        self.items = 0

    def put(self, item):
        self.items += 1
        self.job_q.put(item)

    def get(self):
        self.items -= 1
        return self.result_q.get()

    def __iter__(self):
        while self.items > 0:
            self.items -= 1
            yield self.result_q.get()

    def __exit__(self):
        time.sleep(2)
        self.manager.shutdown()


def run_client(ip, port, authkey, max_items=None):
    """Connect to a SwarmServer and do its dirty work.

    :param ip: ip address of server
    :param port: port to connect to on server
    :param authkey: authorization key
    :param max_items: maximum number of items to process from server.
        Useful for say running clients on a cluster.
    """

    manager = make_client(ip, port, authkey)
    job_q = manager.get_job_q()
    result_q = manager.get_result_q()
    function = manager.get_function()._getvalue()

    processed = 0
    keep_going = True
    while keep_going:
        try:
            job = job_q.get_nowait()
            result = function(job)
            result_q.put(result)
        except Queue.Empty:
            return
        processed += 1
        if max_items is not None and processed == max_items:
            keep_going = False
        
def worker(n):
    """Spend some time calculating exponentials."""
    for _ in xrange(999999):
        a = exp(n)
    return n, a

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='localhost')
    parser.add_argument('--port', type=int, default=5000)
    parser.add_argument('--key',  default='123456')
    grp = parser.add_mutually_exclusive_group(required=True)
    grp.add_argument('--client', action='store_true', help='Run client')
    grp.add_argument('--serverclient', action='store_true', help='Run server-client demo')

    args = parser.parse_args()
    if args.client:
        run_client(args.host, args.port, args.key)
    else:
        print "Running server-client demonstration"
        server = SwarmServer(worker, args.port, args.key)
        for i in xrange(1, 500, 1):
            server.put(i)
        subprocess.Popen(['python', __file__, '--client', '--host', args.host, '--port', str(args.port), '--key', args.key])
        for result in server:
            print "Server got back '{}'".format(result)


if __name__ == '__main__':
    main()
