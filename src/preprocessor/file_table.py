from pathlib import Path

class FileTable:

    def __init__(self, include_directories=None):
        self.exclude_paths = []
        self.default_locations = FileTable.__default_locations()
        self.include_directories = [] if include_directories is None else include_directories

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

    @staticmethod
    def __default_locations():
        return [
            Path("/usr/local/include/"),
            Path("/usr/include"),
            Path("/usr/local/lib/tbasic/"),
            Path("/usr/lib/tbasic/"),
        ]