"""
 _   _
| | | | mu
| |_| | (c) 2026 all rights reserved
| ._,_| https://github.com/brodyking/mu
|_|

"""


class SchemaError(Exception):
    def __init__(self, expected, found):
        self.expected = expected
        self.found = found
        super().__init__(
            f"Incompatible database schema: expected v{expected}, found v{found}. "
            "Please run migrations before starting the application."
        )
