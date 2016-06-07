#!/bin/env dls-python
import argparse
import logging
import sys
import os

if __name__ == "__main__":
    # Test
    from pkg_resources import require
    require("tornado")
    sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from malcolm.core.syncfactory import SyncFactory
from malcolm.core.process import Process
from malcolm.core.block import Block
from malcolm.controllers.clientcontroller import ClientController
from malcolm.controllers.hellocontroller import HelloController
from malcolm.wscomms.wsclientcomms import WSClientComms
from malcolm.wscomms.wsservercomms import WSServerComms


class IMalcolm(object):
    def __init__(self):
        self.client_comms = []
        self.server_comms = []
        self.sync_factory = SyncFactory("Sync")
        self.process = Process("Process", self.sync_factory)

    def add_client_comms(self, url):
        assert url.startswith("ws://"), "Can only do websockets"
        cc = WSClientComms(url, self.process, url)
        self.client_comms.append(cc)
        return cc

    def add_server_comms(self, url):
        #assert url.startswith("ws://"), "Can only do websockets"
        ss = WSServerComms(url, self.process, url)
        self.server_comms.append(ss)
        return ss

    def start(self):
        self.process.start()
        for sc in self.server_comms:
            sc.start()
        for cc in self.client_comms:
            cc.start()

    def stop(self):
        for cc in self.client_comms:
            cc.stop()
        for sc in self.server_comms:
            sc.stop()
        self.process.stop()

    def make_client(self, block_name):
        block = Block(block_name)
        ClientController(self.process, block, self.client_comms[-1])
        return block

    def make_hello(self, block_name):
        block = Block(block_name)
        HelloController(block)
        self.process.add_block(block)
        return block

def make_imalcolm():
    parser = argparse.ArgumentParser(
        description="Interactive shell for malcolm")
    parser.add_argument(
        '--client', '-c',
        help="Add a client to given server, like ws://172.23.243.13:5600")
    parser.add_argument(
        '--server', '-s',
        help="Start a server with the given string, like ws://0.0.0.0:5600")
    parser.add_argument(
        '--log', default="INFO",
        help="Lowest level of logs to see. One of: ERROR, WARNING, INFO, DEBUG "
        "Default is INFO")
    args = parser.parse_args()
    # assuming loglevel is bound to the string value obtained from the
    # command line argument. Convert to upper case to allow the user to
    # specify --log=DEBUG or --log=debug
    numeric_level = getattr(logging, args.log.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % args.log)
    logging.basicConfig(level=numeric_level)

    im = IMalcolm()
    if args.client:
        im.add_client_comms(args.client)
    if args.server:
        im.add_server_comms(args.server)
    return im


def main():
    self = make_imalcolm()
    self.start()

    header = """Welcome to iMalcolm.
Type self.make_client("<device_name>") to get a device client
Try:
hello = self.make_client("hello")
print hello.say_hello("me")

or

hello = self.make_hello("hello")
"""
    try:
        import IPython
    except ImportError:
        import code
        code.interact(header, local=locals())
    else:
        IPython.embed(header=header)

if __name__ == "__main__":
    # Entry point
    main()