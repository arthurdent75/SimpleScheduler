<?php

# ADDON 

$json_folder = "/share/simplescheduler/";
$SUPERVISOR_TOKEN = getenv('SUPERVISOR_TOKEN');
$HASSIO_URL = getenv('HASSIO_URL') ?: "http://hassio/homeassistant/api";
$options_json_file = $json_folder."options.dat";
$sun_filename = $json_folder."sun.dat";

