import sys
import os
import unittest
from collections import OrderedDict
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from pkg_resources import require
require("mock")
from mock import Mock, patch

from malcolm.core.attribute import Attribute
from malcolm.core.attributemeta import AttributeMeta


class TestAttribute(unittest.TestCase):

    def test_init(self):
        meta = Mock()
        a = Attribute("test", meta)
        self.assertEquals("test", a.name)
        self.assertIs(meta, a.meta)
        self.assertIsNone(a.value)

    def test_set_put_function(self):
        func = Mock()
        a = Attribute("test", Mock())
        a.set_put_function(func)
        self.assertIs(func, a.put_func)

    def test_set_value(self):
        value = "test_value"
        a = Attribute("test", Mock())
        a.on_changed = Mock(a.on_changed)
        a.set_value(value)
        self.assertEquals("test_value", a.value)
        a.on_changed.assert_called_once_with([['value'], value])

    def test_put(self):
        func = Mock()
        value = "test_value"
        a = Attribute("test", Mock())
        a.set_put_function(func)
        a.put(value)
        func.assert_called_once_with(value)

    def test_to_dict(self):
        meta = Mock()
        meta.to_dict = Mock(return_value = {"test_meta":"dict"})
        expected = OrderedDict()
        expected["value"] = "test_value"
        expected["meta"] = {"test_meta":"dict"}
        a = Attribute("test", meta)
        a.set_value("test_value")
        self.assertEquals(expected, a.to_dict())

    @patch.object(AttributeMeta, "from_dict")
    def test_from_dict(self, am_from_dict):
        meta = Mock()
        am_from_dict.return_value = meta
        d = {"value":"test_value", "meta":{"meta":"dict"}}
        a = Attribute.from_dict("test", d)
        self.assertEquals("test", a.name)
        self.assertEquals("test_value", a.value)
        self.assertIs(meta, a.meta)

if __name__ == "__main__":
    unittest.main(verbosity=2)
