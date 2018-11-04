#!/usr/bin/env python

"""Simple server using epoll."""

from __future__ import print_function
from contextlib import contextmanager
import socket
import select
import traceback
import json
import multiprocessing
from multiprocessing import Process, Manager, Value


def handler1(request_dic):
    return {
        "status": True,
        "content": "Light workload"
    }

def handler2(request_dic):
    print ("LLLLLL")
    return {
        "status": True,
        "content": "heavy workingload"
    }

@contextmanager
def socketcontext(*args, **kwargs):
    """Context manager for a socket."""
    s = socket.socket(*args, **kwargs)
    try:
        yield s
    finally:
        print("Close socket")
        s.close()


@contextmanager
def epollcontext(*args, **kwargs):
    """Context manager for an epoll loop."""
    e = select.epoll()
    e.register(*args, **kwargs)
    try:
        yield e
    finally:
        print("\nClose epoll loop")
        e.unregister(args[0])
        e.close()


def init_connection(server, connections, requests, responses, epoll):
    """Initialize a connection."""
    connection, address = server.accept()
    connection.setblocking(0)

    fd = connection.fileno()
    epoll.register(fd, select.EPOLLIN)
    connections[fd] = connection
    requests[fd] = ''
    responses[fd] = ''

    print("New server from {0} is ")

def receive_request(fileno, requests, connections, responses, epoll):
    """Receive a request and add a response to send.
    Handle client closing the connection.
    """
    print("Trigger the EPOLLIN event")
    try:
        ##Handle the wrong EPOLLINT trigger by ctrlc from the client
        st = connections[fileno].recv(8).decode('utf-8')
        if len(st) == 0:
            delete_client(fileno, connections, requests, responses, epoll)
            return
        requests[fileno] += st
        while True:
            st = connections[fileno].recv(8).decode('utf-8')
            if len(st) == 0:
                break
            requests[fileno] += st
    except socket.error:
        print ("Error..")
        pass

    print("Read all the request data.... from {0}: {1}".format(fileno, requests[fileno]))
    import pdb; pdb.set_trace()

    request_dic = json.loads(requests[fileno])
    requests[fileno] = ''
    if (request_dic["type"] == "h"):
        print ("Heavy load task...., spawning a new process to handle....")
        def wrapper(request_dic, response, fileno, handler):
            response[fileno] = json.dumps(handler(request_dic))
            print(response[fileno])
            epoll.modify(fileno, select.EPOLLOUT)

        p = multiprocessing.Process(target=wrapper,
                args=(request_dic, responses, fileno, handler2))
        p.start()
    else:
        print("Lightweighted load task...., process it in the main thread....")
        responses[fileno] = json.dumps(handler1(request_dic))
        epoll.modify(fileno, select.EPOLLOUT)


def send_response(fileno, connections, responses, epoll):
    """Send a response to a client."""
    print ("Begin to send data to {0}: {1}".format(fileno, responses[fileno].encode("utf-8")))
    byteswritten = connections[fileno].sendall(responses[fileno].encode("utf-8"))
    responses[fileno] = ''
    epoll.modify(fileno, select.EPOLLIN)
    print ("Response finished")

def delete_client(fileno, connections, requests, responses, epoll):
    print('[{:02d}] exit or hung up'.format(fileno))
    epoll.unregister(fileno)
    connections[fileno].close()

    del connections[fileno], requests[fileno], responses[fileno]
    return

def run_server(socket_options, address):
    """Run a simple TCP server using epoll."""
    with socketcontext(*socket_options) as server, \
            epollcontext(server.fileno(), select.EPOLLIN) as epoll:

        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(address)
        server.listen(5)
        server.setblocking(0)
        server.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        print("Listening")

        connections = {}
        requests = {}
        responses = {}
        server_fd = server.fileno()

        while True:
            events = epoll.poll()
            for fileno, event in events:
                if fileno == server_fd:
                    init_connection(server, connections, requests, responses, epoll)
                elif event & select.EPOLLHUP:
                    delete_client(fileno, connections, requests, responses, epoll)
                elif event & select.EPOLLIN:
                    receive_request(fileno, requests, connections, responses, epoll)
                elif event & select.EPOLLOUT:
                    send_response(fileno, connections, responses, epoll)



if __name__ == '__main__':
    try:
        run_server([socket.AF_INET, socket.SOCK_STREAM], ("0.0.0.0", 4343))
    except KeyboardInterrupt as e:
        print("Shutdown")
        print(traceback.print_exc())