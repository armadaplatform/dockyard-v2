import json
import os


def get_config_json(key, default=None):
    for config_dir in os.environ.get('CONFIG_PATH', '').split(os.pathsep):
        path = os.path.join(config_dir, 'config.json')
        if os.path.exists(path):
            try:
                with open(path) as f:
                    config = json.load(f)
                if key in config:
                    return config[key]
            except:
                pass

    return os.environ.get(key, default)
