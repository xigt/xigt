from . import algnexpr

class Xigt(object):
    def __init__(self, id=None, tiers=None):
        self.id = id
        self.tiers = tiers

class Tier(object):
    def __init__(self, type=None, id=None, ref=None, items=None):
        self.type = type
        self.id = id
        self.ref = ref
        self.items = items or []

    def __repr__(self):
        return 'Tier({},{},{},[{}])'.format(
            str(self.type) if self.type is not None else 'Basic',
            str(self.id) if self.id is not None else '?',
            str(self.ref) if self.ref is not None else '?',
            ','.join(self.items))

    def __getitem__(self, item_id):
        try:
            # attempt list indexing
            return self.items[item_id]
        except TypeError:
            return self.get(item_id)

    def get(self, item_id, default=None):
        # iterate over list? make an ordereddict?
        for item in self.items:
            if item.id == item_id:
                return item
        return None

class Item(object):
    def __init__(self, type=None, id=None, ref=None, content=None):
        self.type = type
        self.id = id
        self.ref = ref
        self.content = content

    def __repr__(self):
        return 'Item({},{},{},{})'.format(
            str(self.type) if self.type is not None else 'Basic',
            str(self.id) if self.id is not None else '?',
            str(self.ref) if self.ref is not None else '?',
            str(self.content))

    def __str__(self):
        if self.content is not None:
            return str(self.content)
        else:
            #TODO proper alignment expression resolution
            return str(self.ref)

    def span(self, start, end):
        return self.content[start:end]

