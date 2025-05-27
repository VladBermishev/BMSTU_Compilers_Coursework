from collections import defaultdict


class Scope:
    def __init__(self, parent=None):
        self.parent = parent
        self.name_usage = defaultdict(int)
        self.name_usage[""] = 1

    def register(self, name):
        basename = name
        suff = ""
        while self.is_used(name):
            suff = str(self.name_usage[name] + 1)
            name = f"{basename}{suff}"
        self.name_usage[name] = int(suff or "1")
        return name

    def is_used(self, name):
        return self.name_usage[name] != 0

    def child(self):
        return type(self)(parent=self.parent)


def mditer(dims):
    idx = [0 for _ in range(len(dims))]
    while all([lhs < rhs for lhs, rhs in zip(idx, dims)]):
        yield tuple(idx)
        idx[-1] += 1
        for iter in range(len(idx) - 1, 0, -1):
            if idx[iter] != dims[iter]:
                break
            idx[iter] = 0
            idx[iter - 1] += 1
            iter -= 1
