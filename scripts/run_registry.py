import os
import subprocess
import sys
from urlparse import urlparse

import yaml
from armada import hermes
from nested_dict import nested_dict

from config.config_json import get_config_json

REGISTRY_CONFIG_PATH = '/etc/docker/registry/config.yml'
DEFAULT_STORAGE_PATH = '/repository'


def parse_base_registry_config():
    with open('config/base_registry_config.yml') as f:
        return nested_dict(yaml.load(f))


def main():
    registry_config = parse_base_registry_config()
    ssl_crt_file = get_config_json('SSL_CRT_FILE')
    ssl_key_file = get_config_json('SSL_KEY_FILE')
    if ssl_crt_file:
        registry_config['http']['tls']['certificate'] = hermes.get_config_file_path(ssl_crt_file)
    if ssl_key_file:
        registry_config['http']['tls']['key'] = hermes.get_config_file_path(ssl_key_file)

    if get_config_json('HTTP_AUTH_USER') and get_config_json('HTTP_AUTH_PASSWORD'):
        user = get_config_json('HTTP_AUTH_USER')
        password = get_config_json('HTTP_AUTH_PASSWORD')
        subprocess.check_output('htpasswd -Bbn "{}" "{}" > /tmp/htpasswd'.format(user, password), shell=True)
        registry_config['auth']['htpasswd']['realm'] = 'Dockyard'
        registry_config['auth']['htpasswd']['path'] = '/tmp/htpasswd'

    if get_config_json('READ_ONLY'):
        registry_config['storage']['maintenance']['readonly']['enabled'] = True

    storage_path = get_config_json('REPOSITORY_PATH') or DEFAULT_STORAGE_PATH
    parsed_storage_path = urlparse(storage_path)
    if parsed_storage_path.scheme == 's3':
        # Fix s3 schemas with too many "/":
        if storage_path.startswith('s3:///'):
            parsed_storage_path = urlparse(storage_path.replace('s3:///', 's3://'))
        s3_bucket = parsed_storage_path.netloc
        s3_directory = parsed_storage_path.path
        registry_config['storage']['s3'] = {
            'bucket': s3_bucket,
            'rootdirectory': s3_directory,
            'region': get_config_json('AWS_REGION'),
            'accesskey': get_config_json('AWS_ACCESS_KEY'),
            'secretkey': get_config_json('AWS_ACCESS_SECRET'),
            'secure': True
        }
    else:
        if not os.path.exists(storage_path):
            os.makedirs(storage_path)
        os.chmod(storage_path, 0o777)
        registry_config['storage']['filesystem']['rootdirectory'] = storage_path

    saved_dict = registry_config.to_dict()
    with open(REGISTRY_CONFIG_PATH, 'w') as f:
        f.write(yaml.safe_dump(saved_dict, default_flow_style=False))
    sys.stdout.flush()

    command = "/go/bin/registry serve {}".format(REGISTRY_CONFIG_PATH).split()
    os.execv(command[0], command)


if __name__ == '__main__':
    main()
