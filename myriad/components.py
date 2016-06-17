from __future__ import absolute_import
import sys
import argparse
import time
from random import random
import Queue
import subprocess
from math import exp
from time import sleep

from myriad.managers import make_server, make_client

class MyriadServer(object):
    def __init__(self, function, port, authkey, qsize=None):
        """A server containing input and output queues, and a function to
        map inputs over. A connecting client can read the stored function,
        apply it to items in the input queue and post back to the output
        queue

        :param function: function to apply to inputs
        :param port: port over which to server
        :param authkey: authorization key
        :param qsize: maximum size of input queue

        """
        self.manager = make_server(function, port, authkey, qsize=qsize)
        self.job_q = self.manager.get_job_q()
        self.result_q = self.manager.get_result_q()
        self._items = 0
        self._closed = self.manager.q_closed()

    def put(self, item, block=True, timeout=None):
        if self.closed:
            raise RuntimeError('Tried to put to MyriadServer, but queue is closed.')
        try:
            self.job_q.put(item, block, timeout)
        except Queue.Full as e:
            raise e
        else:
            self._items += 1

    def get(self):
        try:
            result = self.result_q.get()
        except Exception as e:
            raise e
        else:
            self._items -= 1
            return result

    def close(self):
        self._closed.update(True)

    @property
    def closed(self):
        return self._closed._getvalue().value

    def imap_unordered(self, jobs, timeout=0.5):
        """A iterator over a set of jobs.

        :param jobs: the items to pass through our function
        :param timeout: timeout between polling queues

        Results are yielded as soon as they are available in the output
        queue (up to the discretisation provided by timeout). Since the
        queues can be specified to have a maximum length, the consumption
        of both the input jobs iterable and memory use in the output
        queues are controlled.
        """
        timeout = max(timeout, 0.5)
        jobs_iter = iter(jobs)
        out_jobs = 0
        job = None
        while True:
            if not self.closed and job is None:
                # Get a job
                try:
                    job = jobs_iter.next()
                except StopIteration:
                    job = None
                    self.close()
            if job is not None:
                # Put any job
                try:
                    self.put(job, True, timeout)
                except Queue.Full:
                    pass # we'll try again next time around
                else:
                    job = None
            for result in self.get_finished():
                yield result
                
            # Input and yielded everything?
            if self.closed and self._items == 0:
                break
            sleep(timeout)
            
    def get_finished(self):
        while True:
            try:
                yield self.result_q.get_nowait()
            except Queue.Empty:
                break
            else:
                self._items -= 1

    def __iter__(self):
        while self._items > 0:
            yield self.get()

    def __exit__(self):
        self.closed = True
        time.sleep(2)
        self.manager.shutdown()


def run_client(ip, port, authkey, max_items=None, timeout=2):
    """Connect to a SwarmServer and do its dirty work.

    :param ip: ip address of server
    :param port: port to connect to on server
    :param authkey: authorization key
    :param max_items: maximum number of items to process from server.
        Useful for say running clients on a cluster.
    """

    manager = make_client(ip, port, authkey)
    job_q = manager.get_job_q()
    job_q_closed = manager.q_closed()
    result_q = manager.get_result_q()
    function = manager.get_function()._getvalue()

    processed = 0
    while True:
        try:
            job = job_q.get_nowait()
            result = function(job)
            result_q.put(result)
        except Queue.Empty:
            if job_q_closed._getvalue().value:
                break
        else:
            processed += 1
            if max_items is not None and processed == max_items:
                break
        sleep(timeout)
        
def worker(n):
    """Spend some time calculating exponentials."""
    for _ in xrange(999999):
        a = exp(n)
        b = exp(2*n)
    return n, a

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', type=str, default='localhost')
    parser.add_argument('--port', type=int, default=5000)
    parser.add_argument('--key',  type=str, default='123456')
    parser.add_argument('--max_items', type=int, default=None)
    grp = parser.add_mutually_exclusive_group(required=True)
    grp.add_argument('--client', action='store_true', help='Run client')
    grp.add_argument('--serverclient', action='store_true', help='Run server-client demo')

    args = parser.parse_args()
    if args.client:
        run_client(args.host, args.port, args.key, args.max_items)
    else:
        n_clients = 2
        print "Running server-client demonstration"
        print " - Starting server"
        server = MyriadServer(worker, args.port, args.key, qsize=10)
        print " - Starting {} clients".format(n_clients)
        clients = [subprocess.Popen(['myriad', '--client',
            '--host', args.host, '--port', str(args.port), '--key', args.key])
            for _ in xrange(n_clients)]
        print " - Waiting for results..."
        for result in server.imap_unordered(xrange(10)):
            print "    - Server got back '{}'".format(result)
        print " - Done"


if __name__ == '__main__':
    main()
