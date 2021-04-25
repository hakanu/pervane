
# How to test pervane locally with Docker

## Build an image for local testing

Run the following command from the repository root directory.

`docker build -f docker/dev/Dockerfile -t pervane:dev .`

## Start pervane in a container

The following command starts pervane in a container on `port=5001` with the
host network. You can access it at `localhost:5001` on your browsers.

`docker run --rm --network host pervane:dev`

This command does not specify the notes and config directories so pervane uses
the `PERVANE_HOME` and `PERVANE_CONFIG_HOME` environment variables.

## Mount local config and note directories

The following command mounts `/home/basri/notes` and `/home/basri/.pervane` to
the container. You can test pervane with the user and note data on your host.
Make sure to change the host directories to your own setup.

```shell
docker run \
--rm --network host \
--mount type=bind,source=/home/basri/notes,target=/pervane-notes \
--mount type=bind,source=/home/basri/.pervane,target=/pervane-config \
pervane:dev --dir=/pervane-notes --config_dir=/pervane-config
```

You can do the same with environment variables as follows:

```shell
docker run \
--rm --network host \
-e PERVANE_HOME=/pervane-notes -e PERVANE_CONFIG_HOME=/pervane-config \
--mount type=bind,source=/home/basri/notes,target=/pervane-notes \
--mount type=bind,source=/home/basri/.pervane,target=/pervane-config \
pervane:dev
```

`PERVANE_HOME` and `PERVANE_CONFIG_HOME` point to `/var/opt/pervane` and
`/etc/opt/pervane` by default. You can mount your host directories to their
default values as below:

```shell
docker run \
--rm --network host \
--mount type=bind,source=/home/basri/notes,target=/var/opt/pervane \
--mount type=bind,source=/home/basri/.pervane,target=/etc/opt/pervane \
pervane:dev
```

## See pervane help

`docker run --rm pervane:dev --help`

## `sh` into to the pervane container for investigating files

`docker exec --rm -it $CONTAINER sh`
