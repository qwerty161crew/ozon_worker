from config.config import Config, PostgreSQL

config = Config.create()

__all__ = ["PostgreSQL", "config"]
