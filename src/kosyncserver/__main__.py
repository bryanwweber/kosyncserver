from granian import Granian

from . import logging

if __name__ == "__main__":
    server = Granian(
        "kosyncserver.app:app",
        interface="asgi",
        port=8000,
        address="0.0.0.0",
        loop="uvloop",
    )
    server.serve()
    # changes
