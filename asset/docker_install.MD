# Install this addon as a standalone docker 

## Build the docker container

Currently, no ready-to-use docker image is available. So clone this repository, run `docker build . -t mysimplescheduler:latest` and push the image to your registry.

## Create a token to access homeassistant

Log in to home assistant, go to your user profile, create a long running access token and copy it.

## Create a folder to store persistent data

You need to create a folder where the addon will save the data. You need to specify tha path in the docker run command

## Run the docker image

Run with:

```
docker run -d -e SUPERVISOR_TOKEN=previously-created-token -e HASSIO_URL=http://your-hass-url:port/api -v /path/to/persistent/data:/share/simplescheduler -p 8099:8099 mysimplescheduler:latest
```

You can access the scheduler now at `http://localhost:8099`.

## Change Addon Options

After the first run you will find the option.dat file in the persistent data folder. Change it and rerun the container.


(Thanks to https://github.com/micw)