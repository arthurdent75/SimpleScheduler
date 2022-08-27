# Install on home assistant (without hass.io)

## Build the docker container

Currently, no ready-to-use docker image is available. So clone this repository, run `docker build . -t mysimplescheduler:latest` and push the image to your registry.

## Optional: custom config

Create a data directory containing a `options.dat` for custom configuration. You can copy `options.example.json` and modify it to your needs. This way you can also change translations.

## Create a token to access homeassistant

Log in to home assistant, go to your user profile, create a long running access token and copy it.

## Run the docker image

Run with:

```
docker run -d -e SUPERVISOR_TOKEN=previously-created-token -e HASSIO_URL=http://local-hass-url/api -v /path/to/datadir:/share/simplescheduler -p 8099:8099 mysimplescheduler:latest
```

You can access the scheduler now at `http://localhost:8099`.

(Thanks to https://github.com/micw)