import os
from armada import hermes
from functools import lru_cache


@lru_cache(None)
def get_cached_config():
    return hermes.get_merged_config('config.json')


def get_config_value(key: str, default: str = None):
    config = get_cached_config()
    if key in config:
        return config[key]
    
    return os.environ.get(key, default)
