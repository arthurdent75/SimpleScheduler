# Install this addon as a standalone docker 

## Create a token to access homeassistant

Log in to home assistant, go to your user profile, create a long running access token and copy it.

## Create a folder to store persistent data

You need to create a folder where the addon will save the data. You need to specify tha path in the docker run command

## Run the docker image

Run:

```
docker run -d \
  -e SUPERVISOR_TOKEN=previously-created-token \
  -e HASSIO_URL=http://your-hass-url:port/api \
  -v /path/to/persistent/data:/share/simplescheduler \
  -p 8099:8099 \
  ghcr.io/arthurdent75/simplescheduler/amd64:latest
```
For architectures other than amd64, just replace amd64 with one of the following: aarch64 , armhf , armv7.

You can access the scheduler now at `http://localhost:8099`.


