#!/bin/sh

pip install --upgrade pervane | grep "Successfully installed pervane"

if [ $? -eq 0 ]; then
    echo "Pervane is upgraded since your local image contains an outdated version."
    echo "You can delete the local pervane:latest image with 'docker rmi pervane'."
    echo "Next time you start pervane it will fetch the new image from Docker Hub so you will skip the upgrade step."
fi

exec pervane $@