"""
 _   _
| | | | muweb
| |_| | (c) 2026 all rights reserved
| ._,_| https://github.com/brodyking/mu
|_|

"""

import uvicorn

from muweb.server import app


def main():
    uvicorn.run(app)


if __name__ == "__main__":
    main()
