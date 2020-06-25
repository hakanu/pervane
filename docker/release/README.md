# How to use pervane with Docker

## Start pervane in a container

The following command starts pervane in a container on `port=5000` with the
host network. You can access it at `localhost:5000` on your browsers.

`docker run --rm --network host pervane/pervane`

This command pulls the image tagged with `latest` from Docker Hub and starts
pervane with that image.

The `latest` image on Docker Hub contains the most recent pervane version which
existed at the build time of the image. If a new pervane version is published
after you pull the `latest` image, when you run a container it will upgrade
pervane before start. However, when you stop the container and run another one,
it will repeat the upgrade step. A warning is printed for you to pull the new
`latest` image from Docker Hub again so you can prevent the upgrade step every
time you start a pervane container.

## Mount local config and note directories

The following command mounts `/home/basri/notes` and `/home/basri/.pervane` to
the container. You can run pervane with the user and note data on your host.
Make sure to change the host directories to your own setup.

```shell
docker run \
--rm --network host \
--mount type=bind,source=/home/basri/notes,target=/pervane-notes \
--mount type=bind,source=/home/basri/.pervane,target=/pervane-config \
pervane/pervane --dir=/pervane-notes --config_dir=/pervane-config
```

You can do the same with environment variables as follows:

```shell
docker run \
--rm --network host \
-e PERVANE_HOME=/pervane-notes -e PERVANE_CONFIG_HOME=/pervane-config \
--mount type=bind,source=/home/basri/notes,target=/pervane-notes \
--mount type=bind,source=/home/basri/.pervane,target=/pervane-config \
pervane/pervane
```

`PERVANE_HOME` and `PERVANE_CONFIG_HOME` point to `/var/opt/pervane` and
`/etc/opt/pervane` by default. You can mount your host directories to their
default values as below:

```shell
docker run \
--rm --network host \
--mount type=bind,source=/home/basri/notes,target=/var/opt/pervane \
--mount type=bind,source=/home/basri/.pervane,target=/etc/opt/pervane \
pervane/pervane
```

## See pervane help

`docker run --rm pervane/pervane --help`
