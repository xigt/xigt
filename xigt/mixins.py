
import warnings

# common strings
ID = 'id'
TYPE = 'type'
ALIGNMENT = 'alignment'
CONTENT = 'content'
SEGMENTATION = 'segmentation'


def _has_parent(obj):
    return hasattr(obj, '_parent') and obj._parent is not None


class XigtContainerMixin(object):
    """
    Common methods for accessing subelements in XigtCorpus, Igt, and
    Tier objects.
    """
    def __init__(self):
        self._list = []
        self._dict = {}

    def __iter__(self):
        return iter(self._list)

    def __len__(self):
        return len(self._list)

    def __getitem__(self, obj_id):
        try:
            # attempt list indexing
            obj_id = int(obj_id)
            return self._list[obj_id]
        except ValueError:
            return self._dict[obj_id]

    def get(self, obj_id, default=None):
        try:
            return self[obj_id]
        except (KeyError, IndexError):
            pass
        return default

    def select(self, id=None, type=None,
               alignment=None, content=None, segmentation=None):
        match = lambda x: (
            (id is None or x.id == id) and
            (type is None or x.type == type) and
            (alignment is None or x.alignment == alignment) and
            (content is None or x.content == content) and
            (segmentation is None or x.segmentation == segmentation)
        )
        return filter(match, self)

    def append(self, obj):
        obj._parent = self
        self._create_id_mapping(obj)
        self._list.append(obj)

    def insert(self, i, obj):
        obj._parent = self
        self._create_id_mapping(obj)
        self._list.insert(i, obj)

    def extend(self, objs):
        for obj in objs:
            self.append(obj)

    def _create_id_mapping(self, obj):
        if obj.id is not None:
            if obj.id in self._dict:
                warnings.warn(
                    'Id "{}" already exists in collection.'.format(obj.id),
                    XigtWarning
                )
            self._dict[obj.id] = obj

    def refresh_index(self):
        self._dict = {}
        for obj in self._list:
            self._create_id_mapping(obj)

    def clear(self):
        self._dict = {}
        self._list = []

    # deprecated methods

    def add(self, obj):
        warnings.warn(
            'add(x) is deprecated; use append(x) instead.',
            DeprecationWarning
        )
        return self.append(obj)

    def add_list(self, objs):
        warnings.warn(
            'add_list(xs) is deprecated; use extend(xs) instead.',
            DeprecationWarning
        )
        return self.extend(objs)


class XigtAttributeMixin(object):

    def __init__(self, id=None, type=None, attributes=None):
        self.id = id
        self.type = type
        self.attributes = dict(attributes or [])
        # if id is not None or ID not in self.attributes:
        #     self.attributes[ID] = id
        # if type is not None or TYPE not in self.attributes:
        #     self.attributes[TYPE] = type

    def get_attribute(self, key, default=None, inherit=False):
        try:
            return self.attributes[key]
        except KeyError:
            if not inherit or not _has_parent(self) or key:
                raise
                # raise XigtAttributeError('No attribute {}.'.format(key))
            if key in (ID, TYPE):
                return None  # don't inherit local-only attributes
            return self._parent.get_attribute(key, default, inherit)

    # @property
    # def id(self):
    #     return self.attributes[ID]
    # @id.setter
    # def id(self, value):
    #     self.attributes[ID] = value
    
    # @property
    # def type(self):
    #     return self.attributes[TYPE]
    # @type.setter
    # def type(self, value):
    #     self.attributes[TYPE] = value


class XigtReferenceAttributeMixin(object):

    @property
    def alignment(self):
        return self.attributes.get(ALIGNMENT)
    @alignment.setter
    def alignment(self, value):
        self.attributes[ALIGNMENT] = value

    @property
    def content(self):
        return self.attributes.get(CONTENT)
    @content.setter
    def content(self, value):
        self.attributes[CONTENT] = value

    @property
    def segmentation(self):
        return self.attributes.get(SEGMENTATION)
    @segmentation.setter
    def segmentation(self, value):
        self.attributes[SEGMENTATION] = value


class XigtMetadataMixin(object):
    """
    Enables the inheritance of metadata.
    """
    def __init__(self, metadata):
        self.metadata = list(metadata or [])

    def get_meta(self, key, conditions=None, default=None, inherit=True):
        if conditions is None:
            conditions = []
        metas = []
        for metadata in self.metadata:
            if metadata.type != 'xigt-meta':
                continue
            for meta in metadata.text:
                if meta.type == key and all(c(meta) for c in conditions):
                    metas.append(meta)
        if metas:
            return metas
        elif inherit and _has_parent(self):
            return self._parent.get_meta(key, conditions, default, inherit)
        else:
            return default

