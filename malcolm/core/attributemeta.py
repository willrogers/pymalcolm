from collections import OrderedDict

from malcolm.core.monitorable import Monitorable

class AttributeMeta(Monitorable):
    """Abstract base class for Meta objects"""

    # This will be set by subclasses calling cls.register_subclass()
    metaOf = None
    # dict mapping metaOf name -> cls
    _subcls_lookup = {}

    def __init__(self, name, description):
        super(AttributeMeta, self).__init__(name=name)
        self.description = description

    def validate(self, value):
        """
        Abstract function to validate a given value

        Args:
            value(abstract): Value to validate
        """

        raise NotImplementedError(
            "Abstract validate function must be implemented in child classes")

    def to_dict(self):
        """Convert object attributes into a dictionary"""

        d = OrderedDict()
        d["description"] = self.description
        d["metaOf"] = self.metaOf

        return d

    @classmethod
    def register_subclass(cls, subcls, metaOf):
        """Register a subclass so from_dict() works

        Args:
            subcls (AttributeMeta): AttributeMeta subclass to register
            metaOf (str): Like "malcolm:core/String:1.0"
        """
        cls._subcls_lookup[metaOf] = subcls
        subcls.metaOf = metaOf

    @classmethod
    def from_dict(cls, name, d):
        """Create a AttributeMeta subclass instance from the serialized version
        of itself

        Args:
            name (str): AttributeMeta instance name
            d (dict): Something that self.to_dict() would create
        """
        metaOf = d["metaOf"]
        subcls = cls._subcls_lookup[metaOf]
        assert subcls is not cls, \
            "Subclass %s did not redefine from_dict" % subcls
        attribute_meta = subcls.from_dict(name, d)
        return attribute_meta
