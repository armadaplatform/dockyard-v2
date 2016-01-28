import json
import os
import sys

import hermes

REGISTRY_CONFIG_PATH = '/etc/docker/registry/config.yml'


def main():
    command = "/go/bin/registry {}".format(REGISTRY_CONFIG_PATH).split()
    env = hermes.get_config('config.json')
    if 'SSL_CRT_FILE' in env:
        env['REGISTRY_HTTP_TLS_CERTIFICATE'] = hermes.get_config_file_path(env['SSL_CRT_FILE'])
    if 'SSL_KEY_FILE' in env:
        env['REGISTRY_HTTP_TLS_KEY'] = hermes.get_config_file_path(env['SSL_KEY_FILE'])

    is_read_only = env.pop('READ_ONLY', False)

    print(json.dumps(env, indent=4))
    sys.stdout.flush()
    os.execve(command[0], command, env)


if __name__ == '__main__':
    main()
