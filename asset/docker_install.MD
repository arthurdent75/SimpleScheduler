# Run this addon as a standalone docker 

If you are reading this tutorial, it's because you are familiar with Docker. Otherwise, it's not a good idea.

## Create a token to access Home Assistant

Log in to Home Assistant, go to your user profile, create a *long-lived access token*, and copy it.

## Create a folder to store persistent data

You have to create a folder where the addon will save the data. You need to specify that path in the docker run command

## Run the docker image

Run:

```
docker run -d \
  -e SUPERVISOR_TOKEN=previously-created-token \
  -e HASSIO_URL=http://your-hass-url:port/api \
  -v /path/to/persistent/data:/share/simplescheduler \
  -p 8099:8099 \
  ghcr.io/arthurdent75/simplescheduler
```

You can access the scheduler now at `http://localhost:8099`.


