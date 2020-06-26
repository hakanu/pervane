FROM python:3-slim

LABEL org.label-schema.name="Dockerfile for running pervane"
LABEL org.label-schema.description="You can use this image to run pervane with Docker."
LABEL org.label-schema.url="https://hakanu.github.io/pervane/"
LABEL org.label-schema.vcs-url="https://github.com/hakanu/pervane/"
LABEL org.label-schema.docker.cmd.help="docker exec --rm -it CONTAINER_ID pervane --help"


# NOTICE: 

# you can override all of the environments below by passing arguments to docker
# run. for instance, `docker run -p 5001:5001 pervane:dev --port=5001` starts
# pervane on port 5001 even though PERVANE_PORT is set to 5000. in short,
# program args are prioritized against environment variables.


# pervane puts its config files to this directory.
# you can mount a host directory to it.
# you can override it or use --config_dir while starting a container.
ENV PERVANE_CONFIG_HOME=/etc/opt/pervane

# pervane uses this directory for storing notes.
# you can mount a host directory to it.
# you can override it or use --dir while starting a container.
ENV PERVANE_HOME=/var/opt/pervane

# env vars below are added for verbosity.
# you can override it or use --host while starting a container.
ENV PERVANE_HOST=0.0.0.0
# you can override it or use --port while starting a container.
ENV PERVANE_PORT=5000
# you can override it or use --allow_multi_user while starting a container.
ENV PERVANE_ALLOW_MULTI_USER=False

EXPOSE ${PERVANE_PORT}

RUN pip install --no-cache-dir pervane

WORKDIR /opt/pervane

ADD run.sh .
RUN chmod +x run.sh

ENTRYPOINT ["./run.sh"]
