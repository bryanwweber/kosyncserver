from granian import Granian

from .config import get_settings

if __name__ == "__main__":
    settings = get_settings()
    server = Granian(
        "kosyncserver.app:app",
        interface=settings.interface,
        port=settings.port,
        address=settings.host,
        loop=settings.loop,
        reload=settings.reload,
    )
    server.serve()
