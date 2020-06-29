# Release a new "latest" image for a new pervane version

## Build the image

When a new pervane version is published, we build a new "latest" image and push
it to Docker Hub. To do that, `cd` into `/docker/release` and run:

`docker build -t pervane/pervane:latest .`

## Push the image to Docker Hub

`docker push pervane/pervane:latest .`
