import unittest
from collections import OrderedDict
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

# mock
from pkg_resources import require
require("mock")
from mock import MagicMock, patch

# logging
import logging
logging.basicConfig(level=logging.DEBUG)

# module imports
from malcolm.controllers.clientcontroller import ClientController
from malcolm.core.process import Process
from malcolm.core.block import Block
from malcolm.core.stringmeta import StringMeta
from malcolm.core.syncfactory import SyncFactory


class TestClientController(unittest.TestCase):

    def setUp(self):
        s = SyncFactory("sync")
        self.p = Process("process", s)
        self.b = Block("blockname")
        self.comms = MagicMock()
        serialized = dict(
            say_hello=dict(
                description="Says hello",
                takes=dict(
                    elements=dict(
                        name=dict(
                            description="A name",
                            metaOf="malcolm:core/String:1.0",
                        ),
                    ),
                    required=["name"],
                ),
                defaults={},
                returns=dict(
                    elements=dict(
                        greeting=dict(
                            description="A greeting",
                            metaOf="malcolm:core/String:1.0",
                        ),
                    ),
                    required=["response"],
                ),
            ),
        )

        def f(request):
            request.respond_with_return(serialized)

        self.comms.q.put.side_effect = f
        self.cc = ClientController(self.p, self.b, self.comms)

    def test_methods_created(self):
        self.assertEqual(self.b._methods.keys(), ["say_hello"])
        m = self.b._methods["say_hello"]
        self.assertEqual(m.name, "say_hello")
        self.assertEqual(m.takes.elements.keys(), ["name"])
        self.assertEqual(type(m.takes.elements["name"]), StringMeta)
        self.assertEqual(m.returns.elements.keys(), ["greeting"])
        self.assertEqual(type(m.returns.elements["greeting"]), StringMeta)
        self.assertEqual(m.defaults, {})

    def test_call_method(self):
        def f(request):
            request.respond_with_return(dict(
                greeting="Hello %s" % request.parameters["name"]))
        self.comms.q.put.side_effect = f
        ret = self.b.say_hello(name="me")
        self.assertEqual(ret["greeting"], "Hello me")

if __name__ == "__main__":
    unittest.main(verbosity=2)
