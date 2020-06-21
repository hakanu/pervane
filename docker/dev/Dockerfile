FROM python:3-slim

LABEL org.label-schema.name="Dockerfile for testing pervane"
LABEL org.label-schema.description="You can build an image to test pervane with Docker."
LABEL org.label-schema.url="https://hakanu.github.io/pervane/"
LABEL org.label-schema.vcs-url="https://github.com/hakanu/pervane/"
LABEL org.label-schema.version="dev"
LABEL org.label-schema.docker.cmd.help="docker exec -it $CONTAINER python serve.py --help"

# pervane source files will be placed to this directory.
# you can override it with `--build-arg PERVANE_WD=your_dir_name`
# while building the image
ARG PERVANE_WD=/opt/pervane


# NOTICE:
# you can override all of the environments below with arguments you pass to
# docker run. for instance, `docker run -p 5001:5001 pervane:dev --port=5001 `
# starts pervane on port 5001 even though PERVANE_PORT is set to 5000.
# in short, program args are prioritized against environment variables.


# pervane will put config file to this directory.
# you can mount a host directory to it.
# you can override it or use --config_dir while starting a container.
ENV PERVANE_CONFIG_HOME=/etc/opt/pervane

# pervane will use this directory for notes.
# you can mount a host directory to it.
# you can override it or use --dir while starting a container.
ENV PERVANE_HOME=/var/opt/pervane

# env vars below are added for verbosity.
# you can override it or use --host while starting a container.
ENV PERVANE_HOST=0.0.0.0
# default port is 5001 to prevent conflict with personal pervane.
# you can override it or use --port while starting a container.
ENV PERVANE_PORT=5001
# you can override it or use --allow_multi_user while starting a container.
ENV PERVANE_ALLOW_MULTI_USER=False
# you can override it or use --debug while starting a container.
ENV PERVANE_DEBUG=True

EXPOSE ${PERVANE_PORT}

WORKDIR ${PERVANE_WD}

ADD requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
ADD pervane/version.txt .
ADD pervane/serve.py .
ADD pervane/templates templates
ADD pervane/static static

ENTRYPOINT ["python", "serve.py"]
