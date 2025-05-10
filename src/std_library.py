import pathlib


class StandardLibrary:

    @staticmethod
    def location(_std_module: pathlib.Path = pathlib.Path("std.basic")) -> pathlib.Path | None:
        for prob_dir in StandardLibrary.__default_locations():
            if (prob_path := (prob_dir/_std_module)).exists() and prob_path.is_file():
                return prob_path
        return None

    @staticmethod
    def __default_locations():
        defaults = [
            pathlib.Path("/usr/local/include/"),
            pathlib.Path("/usr/include"),
            pathlib.Path("/usr/local/lib/tbasic/"),
            pathlib.Path("/usr/lib/tbasic/"),
        ]
        return [loc for loc in defaults if loc.exists()]