# Install this addon as a standalone docker 

## Build the docker container

There is no ready-to-use docker image at the moment, so you have to build it. \
After you clone the repository, cd to the folder that contain the Dockerfile and run:
```
docker build . -t mysimplescheduler:latest --build-arg BUILD_FROM="ghcr.io/hassio-addons/debian-base/amd64:5.3.1"
```
For architectures other than amd64, just replace amd64 with one of the following: aarch64 , armhf , armv7 , i386. 


## Create a token to access homeassistant

Log in to home assistant, go to your user profile, create a long running access token and copy it.

## Create a folder to store persistent data

You need to create a folder where the addon will save the data. You need to specify tha path in the docker run command

## Run the docker image

Run:

```
docker run -d -e SUPERVISOR_TOKEN=previously-created-token -e HASSIO_URL=http://your-hass-url:port/api -v /path/to/persistent/data:/share/simplescheduler -p 8099:8099 mysimplescheduler:latest
```

You can access the scheduler now at `http://localhost:8099`.


