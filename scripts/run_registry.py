import json
import os
import subprocess
import sys
from urllib.parse import urlparse

import hermes
import yaml
from  nested_dict import nested_dict as nested_dict

REGISTRY_CONFIG_PATH = '/etc/docker/registry/config.yml'
DEFAULT_STORAGE_PATH = '/repository'


# configdict = lambda x: defaultdict(configdict, x)
# cd = lambda: defaultdict(cd)


def parse_base_registry_config():
    with open(os.path.join(os.path.dirname(__file__), '..', 'config', 'base_registry_config.yml')) as f:
        return nested_dict(yaml.load(f))


def main():
    command = "/go/bin/registry {}".format(REGISTRY_CONFIG_PATH).split()
    config = hermes.get_config('config.json')
    base_config = parse_base_registry_config()
    from pprint import pprint
    new_config = nested_dict(base_config)
    new_config['aa']['bb']['cc'] = 'test'
    pprint(new_config)
    out_config = new_config.to_dict()
    pprint(out_config)
    print(yaml.dump(out_config, default_flow_style=False))

    sys.exit(0)
    env = {}
    if 'SSL_CRT_FILE' in config:
        env['REGISTRY_HTTP_TLS_CERTIFICATE'] = hermes.get_config_file_path(config['SSL_CRT_FILE'])
    if 'SSL_KEY_FILE' in config:
        env['REGISTRY_HTTP_TLS_KEY'] = hermes.get_config_file_path(config['SSL_KEY_FILE'])

    if 'HTTP_AUTH_USER' in config and 'HTTP_AUTH_PASSWORD' in config:
        user = config['HTTP_AUTH_USER']
        password = config['HTTP_AUTH_PASSWORD']
        subprocess.check_output('htpasswd -Bbn "{}" "{}" > /tmp/htpasswd'.format(user, password), shell=True)
        env['REGISTRY_AUTH'] = 'htpasswd'
        env['REGISTRY_AUTH_HTPASSWD_REALM'] = 'Registry Realm'
        env['REGISTRY_AUTH_HTPASSWD_PATH'] = '/tmp/htpasswd'

    if config.get('READ_ONLY'):
        # env['REGISTRY_STORAGE_MAINTENANCE'] = 'readonly'
        env['REGISTRY_STORAGE_MAINTENANCE_READONLY'] = 'true'
        # env['REGISTRY_STORAGE_MAINTENANCE_READONLY'] = '{"enabled": "true"}'
        env['REGISTRY_STORAGE_MAINTENANCE_READONLY_ENABLED'] = 'true'

    storage_path = config.get('REPOSITORY_PATH') or DEFAULT_STORAGE_PATH
    parsed_storage_path = urlparse(storage_path)
    if parsed_storage_path.scheme == 's3':
        # Fix s3 schemas with too many "/":
        if storage_path.startswith('s3:///'):
            parsed_storage_path = urlparse(storage_path.replace('s3:///', 's3://'))
        s3_bucket = parsed_storage_path.netloc
        s3_directory = parsed_storage_path.path
        env['REGISTRY_STORAGE'] = 's3'
        env['REGISTRY_STORAGE_S3_BUCKET'] = s3_bucket
        env['REGISTRY_STORAGE_S3_ROOTDIRECTORY'] = s3_directory
        env['REGISTRY_STORAGE_S3_REGION'] = config['REGISTRY_STORAGE_S3_REGION']
        env['REGISTRY_STORAGE_S3_ACCESSKEY'] = config['AWS_ACCESS_KEY']
        env['REGISTRY_STORAGE_S3_SECRETKEY'] = config['AWS_ACCESS_SECRET']
    else:
        if not os.path.exists(storage_path):
            os.makedirs(storage_path)
        os.chmod(storage_path, 0o777)
        env['REGISTRY_STORAGE_FILESYSTEM_ROOTDIRECTORY'] = storage_path

    print(json.dumps(env, indent=4))
    sys.stdout.flush()
    os.execve(command[0], command, env)


if __name__ == '__main__':
    main()
