# dockyard-v2

`dockyard-v2` service contains armadized [Docker Registry 2.0](https://github.com/docker/distribution) - a place to store
your docker container images.

# Building the service.

    armada build dockyard-v2


# Running the service.

## Choosing storage.

The service supports two storage options:

1. Registry stored in filesystem.

    Registry is stored in directory `/repository` inside the container.
    To ensure persistent storage it should be mapped to some folder on the host machine,
    e.g. `/var/opt/dockyard.initech.com`:

        armada run dockyard-v2 -v /var/opt/dockyard.initech.com:/repository


2. Registry stored in AWS S3.

    You have to provide AWS region, S3 bucket path and suitable access and secret keys:

        armada run dockyard-v2 -e "AWS_REGION=us-east-1" "REPOSITORY_PATH=s3://com-initech-dockyard/" \ 
            "AWS_ACCESS_KEY=..." "AWS_ACCESS_SECRET=..."

    Beware not to use dot character in your bucket name (e.g. `com.initech.dockyard`). Amazon's S3 SSL certificate
    is valid only for first-level subdomains of `s3.amazonaws.com` through which API calls are made.
    Requests to `https://com.initech.dockyard.s3.amazonaws.com` would be invalid and the dockyard wouldn't work.


## Securing dockyard.

### HTTPS.

Dockyard can be run either behind HTTP or HTTPS protocols.
The first option may be convenient for local development registry, but in production environments HTTPS should be used.
To run dockyard that way we have to provide correct SSL certificate.
Assuming we have proper keys in `/etc/ssl/dockyard.initech.com` directory we can run:

    armada run dockyard-v2 ... -v /etc/ssl/dockyard.initech.com:/ssl_keys -e "HTTPS_DOMAIN=dockyard.initech.com" \
        "SSL_CRT_FILE=/ssl_keys/dockyard.initech.com.crt" "SSL_KEY_FILE=/ssl_keys/dockyard.initech.com.key"

#### Self-signed SSL certificates.

If you still want to use dockyard behind HTTPS, but you do not own domain with HTTPS or you are using docker >= v1.8.0
and want to avoid problem with HTTP dockyards [described below](#problem-with-using-http-dockyard-with-docker--180),
then you can use self-signed certificate.

But beware, it is less secure than using trusted CA, and requires configuring every host that will access the
Dockyard.

To generate such certificate you can use this script:

    DOMAIN=dockyard.initech.com
    openssl req -newkey rsa:4096 -nodes -sha256 -keyout ${DOMAIN}.key -x509 -days 10000 -subj "/CN=${DOMAIN}" -out ${DOMAIN}.crt

Now you have to put the generated .crt file on all hosts that will access the Dockyard.

You can either install it for docker only, or to the entire system.

To add it to docker, put it here: `/etc/docker/certs.d/${DOMAIN}/ca.crt` and restart docker.
Make sure the armada command users have access to this file. E.g. `sudo chmod 755 /etc/docker` may be required.

Adding it to your system differs between distributions.

E.g. on Ubuntu put it to:
`/usr/local/share/ca-certificates/${DOMAIN}.crt`
and run:

    update-ca-certificates

For more information about using self-signed certificates see:
https://docs.docker.com/registry/insecure/#using-self-signed-certificate

### Basic HTTP authentication.

When using HTTPS, we can also add basic HTTP authentication, so that only users knowing proper credentials can access it.
In addition to other parameters we can run:

    armada run dockyard-v2 ... -e "HTTP_AUTH_USER=admin" "HTTP_AUTH_PASSWORD=secret!"

This type of authentication can only be used with dockyard with HTTPS configured.

### Problem with using HTTP Dockyard with docker >= 1.8.0.

Since docker version 1.8.0, it is not allowed to connect to HTTP Dockyards on other hosts than localhost.
However, if you still want to use HTTP Dockyard and are aware of the insecurity issues with HTTP, you can use
workaround.

Run the proxy service ([armada-bind](https://github.com/armadaplatform/armada-bind)) that will expose access to remote
dockyard on some port on your localhost:

    REMOTE_DOCKYARD_ADDRESS=insecure-dockyard.initech.com:7000
    LOCAL_BIND_PORT=5000
    armada run armada-bind -d armada --rename dockyard-proxy -e SERVICE_ADDRESS=${REMOTE_DOCKYARD_ADDRESS} -p ${LOCAL_BIND_PORT}:80

And add it to your dockyard list:

    armada dockyard set my-dockyard localhost:${LOCAL_BIND_PORT}

### Read only mode.

If you want to run dockyard in read only mode you can add parameter `READ_ONLY`:

    armada run dockyard-v2 ... -e "READ_ONLY=1"

It can be useful to have 2 dockyards running. One with authenticated read/write access for the developers, and the other
read only one for your customers.


## Hermes.

All of the above configuration options can also be supplied by Hermes, so that you don't have to type them all the time.
The configuration should be stored in file `config.json` that contains single json object.
Its key/value pairs correspond to the explained environment variables.
E.g.:

    {
        "REPOSITORY_PATH": "s3:///com-initech-dockyard/",
        "AWS_ACCESS_KEY": "xxx",
        "AWS_ACCESS_SECRET": "xxx",
        "AWS_REGION": "us-east-1",

        "HTTPS_DOMAIN": "dockyard.initech.com",
        "SSL_CRT_FILE": "ssl_keys/dockyard.initech.com.crt",
        "SSL_KEY_FILE": "ssl_keys/dockyard.initech.com.key",

        "READ_ONLY": true
    }

SSL certificate files should also be provided by Hermes. Path to them (`SSL_CRT_FILE`, `SSL_KEY_FILE`) is relative to
`config.json` file.
