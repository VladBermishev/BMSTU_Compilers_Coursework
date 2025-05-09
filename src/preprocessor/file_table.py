from pathlib import Path

class FileTable:

    def __init__(self, current_directory=None, include_directories=None):
        self.exclude_paths = []
        self.default_locations = FileTable.__default_locations()
        self.include_directories = [] if include_directories is None else include_directories
        if current_directory is not None:
            self.include_directories = [Path(current_directory)] + self.include_directories

    def exclude(self, path: Path):
        if not path.exists():
            raise ValueError(f"Can't exclude {path}, no such file")
        if not path.is_file():
            raise ValueError(f"Can't exclude {path}: isn't a file")
        if path not in self.exclude_paths:
            self.exclude_paths.append(path)

    def add_directory(self, path: Path):
        if not path.exists():
            raise ValueError(f"Can't include {path}, no such directory")
        if not path.is_dir():
            raise ValueError(f"Can't exclude {path}: isn't a directory")
        if path not in self.include_directories:
            self.include_directories.append(path)

    def find(self, path: Path):
        for prob_dir in self.locations():
            if (prob_path := (prob_dir/path)).exists() and prob_path.is_file() and prob_path not in self.exclude_paths:
                return prob_path
        return None

    def is_excluded(self, path: Path):
        for prob_dir in self.locations():
            if (prob_path := (prob_dir/path)).exists() and prob_path.is_file():
                return prob_path in self.exclude_paths
        return False

    def locations(self):
        return self.include_directories + self.default_locations

    @staticmethod
    def __default_locations():
        defaults = [
            Path("/usr/local/include/"),
            Path("/usr/include"),
            Path("/usr/local/lib/tbasic/"),
            Path("/usr/lib/tbasic/"),
        ]
        return [ loc for loc in defaults if loc.exists() ]