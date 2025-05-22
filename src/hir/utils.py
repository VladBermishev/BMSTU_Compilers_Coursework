from collections import defaultdict


class Scope:
    def __init__(self, parent=None):
        self.parent = parent
        self.name_usage = defaultdict(int)
        self.name_usage[""] = 1

    def register(self, name):
        basename = name
        while self.is_used(name):
            suff = str(self.name_usage[name] + 1)
            name = f"{basename}{suff}"
        self.name_usage[name] = 1
        return name

    def is_used(self, name):
        return self.name_usage[name] != 0

    def child(self):
        return type(self)(parent=self.parent)