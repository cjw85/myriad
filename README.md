# swarm
Some simple distributed computing components using only the python standard library.

# Installation
swarm can be installed in the usual way with

    python setup.py install

It should be installed on all computers that will do any processing.

# Usage
swarm contains client and server components. The server manages input and output queues, which clients can have access. The basic pattern is to start and server, push work to its input queues, launch clients, and finally collect results from the server. An example is given in the `swarm.components` module, which provides the swarm command-line entry point. Here's a full example.

    from swarm.components import SwarmServer
    from random import randint

    host = 'localhost'
    port = '12345'
    key = 'auth_key'
    worker = ... # mysterious function that transforms inputs to outputs

    # Create a server
    server = SwarmServer(worker, port, key)
    # Push some jobs to the server
    for _ in xrange(5):
        server.put(randint(1,3))
    
    # Start a client
    subprocess.Popen(['swarm', '--client',
        '--host', 'localhost', '--port', port, '--key', key])
    # Collect results from server
    for result in server:
        print "Server got back '{}'".format(result)

In the above we start a subprocess running swarm with the `--client` option. Of course this line could be amended to, for example, submit clients to a cluster.
