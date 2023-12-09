from flask import Flask, render_template, request, redirect, make_response
import paho.mqtt.client as mqtt
import flask.cli
import logging
import glob
import os
import json
import uuid
from datetime import datetime, timedelta
import pytz
import requests
import re
import psutil

import simpleschedulerconf

valid_domains = ["light", "scene", "switch", "script", "camera", "climate", "cover", "vacuum", "fan", "humidifier",
                 "automation", "input_boolean", "media_player"]
lwt_topic = "homeassistant/switch/simplescheduler/availability"
sun_data = ""
schedulers_list = []
options = []
weekday = []
has_changed: bool = False
mqttclient = None
ha_timezone = "utc"
scheduler_pid = 0
request_timeout = 5  # seconds
domain_list = []

app = Flask(__name__)


@app.route("/")
@app.route("/main")
def webserver_home():
    return render_template('index.html',
                           data=load_json_schedulers(),
                           o=get_options(),
                           css=get_css(),
                           switchlist=get_switch_html_select_options(),
                           friendlynames=get_switch_friendly_names(),
                           sort=get_sort_list(),
                           weekday=weekday,
                           statusbarinfo=get_statusbar_info()
                           )


@app.route("/new")
def webserver_new():
    return render_template('new.html')


@app.route('/delete', methods=['GET'])
def webserver_delete():
    args = request.args
    sid = args.get('id')
    file = simpleschedulerconf.json_folder + sid + '.json'
    if os.path.exists(file):
        os.remove(file)
    if options['MQTT']['enabled']:
        mqttclient.publish('homeassistant/switch/simplescheduler/' + sid + '/config', "", qos=0, retain=1)
    return redirect("main")


@app.route('/edit', methods=['GET'])
def webserver_edit():
    is_new = False
    args = request.args
    sid = args.get('id')
    stype: str = args.get('type')
    file = simpleschedulerconf.json_folder + sid + '.json'
    if sid != "0":
        with open(file, "r") as read_file:
            param = json.load(read_file)
    else:
        param = json.loads(get_json_template(stype))
        param['id'] = uuid.uuid4().hex
        is_new = True

    return render_template('edit.html',
                           p=param,
                           o=get_options(),
                           weekday=weekday,
                           switchlist=get_switch_html_select_options(),
                           is_new=is_new
                           )


@app.route('/config', methods=['GET'])
def webserver_config():
    return render_template('config.html',
                           o=get_options(),
                           d=valid_domains
                           )


@app.route('/saveconfig', methods=['GET'])
def webserver_saveconfig():
    jsondata = {}
    translations = {}
    components = {}
    mqttconf = {}
    content = request.args
    for item in content:
        if content[item] == '0' or content[item] == '1':
            value = int(content[item])
        else:
            value = content[item]
        if "." in item:
            p = item.split(".")
            cat = p[0].lower()
            subcat = p[1]
            if cat == "translations":  translations[subcat] = value
            if cat == "components":  components[subcat] = value
            if cat == "mqtt":  mqttconf[subcat] = value
        else:
            jsondata[item] = value

    jsondata["translations"] = translations
    jsondata["components"] = components
    jsondata["MQTT"] = mqttconf

    option_file_path = os.path.join(simpleschedulerconf.json_folder, "options.dat")
    with open(option_file_path, 'w') as option_file:
        json_config = json.dump(jsondata, option_file)

    init()

    return redirect("main")


@app.route('/clone', methods=['GET'])
def webserver_clone():
    args = request.args
    sid = args.get('id')
    file = simpleschedulerconf.json_folder + sid + '.json'
    if os.path.exists(file) and sid != "0":
        with open(file, "r") as read_file:
            param = json.load(read_file)
        newsid = uuid.uuid4().hex
        newfile = simpleschedulerconf.json_folder + newsid + '.json'
        param['id'] = newsid
        param['name'] = param['name'] + " (2) "
        with open(newfile, 'w') as jsonFile:
            json.dump(param, jsonFile)
    return redirect("main")


@app.route("/update", methods=['POST'])
def webserver_update():
    sid = request.form.get('id')
    enabled = request.form.get("enabled")
    dontretry = request.form.get("dontretry")
    name = request.form.get("name")
    entity_id = request.form.getlist('entity_id[]')
    type = request.form.get('type')
    if type != 'weekly':
        on_tod = request.form.get('on_tod')
        off_tod = request.form.get('off_tod')
        on_dow = ""
        off_dow = ""
        for o in request.form.getlist('on_dow[]'):
            on_dow += o
        for o in request.form.getlist('off_dow[]'):
            off_dow += o

    data = json.loads(get_json_template(type))
    data['id'] = sid
    data['name'] = name if name else sid
    data['enabled'] = enabled if enabled else 0
    data['dontretry'] = dontretry if dontretry else 0
    data['entity_id'] = entity_id
    if type == 'weekly':
        data['weekly']['on_1'] = request.form.get('on_1')
        data['weekly']['on_2'] = request.form.get('on_2')
        data['weekly']['on_3'] = request.form.get('on_3')
        data['weekly']['on_4'] = request.form.get('on_4')
        data['weekly']['on_5'] = request.form.get('on_5')
        data['weekly']['on_6'] = request.form.get('on_6')
        data['weekly']['on_7'] = request.form.get('on_7')
        data['weekly']['off_1'] = request.form.get('off_1')
        data['weekly']['off_2'] = request.form.get('off_2')
        data['weekly']['off_3'] = request.form.get('off_3')
        data['weekly']['off_4'] = request.form.get('off_4')
        data['weekly']['off_5'] = request.form.get('off_5')
        data['weekly']['off_6'] = request.form.get('off_6')
        data['weekly']['off_7'] = request.form.get('off_7')
    elif type == 'recurring':
        data['recurring']['on_start'] = request.form.get('on_start')
        data['recurring']['on_end'] = request.form.get('on_end')
        data['recurring']['on_interval'] = request.form.get('on_interval')
        data['recurring']['off_start'] = request.form.get('off_start')
        data['recurring']['off_end'] = request.form.get('off_end')
        data['recurring']['off_interval'] = request.form.get('off_interval')
        data['on_tod'] = on_tod
        data['off_tod'] = off_tod
        data['on_dow'] = on_dow
        data['off_dow'] = off_dow
    else:
        data['on_tod'] = on_tod
        data['off_tod'] = off_tod
        data['on_dow'] = on_dow
        data['off_dow'] = off_dow
    file = simpleschedulerconf.json_folder + sid + '.json'
    with open(file, 'w') as jsonFile:
        json.dump(data, jsonFile)
    if options['MQTT']['enabled']:
        mqtt_send_config(mqttclient)
        # mqtt_publish_state(mqttclient, id, enabled, True)
    return redirect("main")


@app.route("/sort", methods=['GET'])
def webserver_sort():
    data = request.args
    save_sort_list(data)
    return make_response("", 200)


@app.route("/log", methods=['GET'])
def webserver_log():
    response = ""
    logfilepath = os.path.join(simpleschedulerconf.json_folder, "simplescheduler.log")
    with open(logfilepath, "r", encoding='utf-8') as logfile:
        response += logfile.read()
    return make_response(response, 200)


@app.route("/dirty")
def webserver_dirty():
    global has_changed
    if has_changed:
        r = '1'
        has_changed = False
    else:
        r = '0'
    return make_response(r, 200)


@app.context_processor
def utility_processor():
    def format_event(value: str, showvalue: bool):
        if not value: return ''
        result: str = ""
        extra: str = ""
        events = value.upper().replace(',', ' ').replace(';', ' ').split(' ')

        for e in events:
            p = e.split('>')  # separate time from extra commands
            t: str = p[0]
            extra = ""
            if len(p) > 1 and showvalue:  # verify extra commands
                prefix = p[1][0]
                v: str = p[1][1:]
                if prefix == 'F':
                    extra = '<span class="event-type-f"><i class="mdi mdi-fan" aria-hidden="true"></i>' + v + '%</span>'
                if prefix == 'P':
                    extra = '<span class="event-type-p"><i class="mdi mdi-arrow-up-down" aria-hidden="true"></i>' + v + '%</span>'
                if prefix == 'T':
                    if v[0] == 'O':
                        v = v[1:]
                        extra = '<span class="event-type-to"><i class="mdi mdi-thermometer" aria-hidden="true"></i>' + v + '&deg;</span>'
                    else:
                        extra = '<span class="event-type-t"><i class="mdi mdi-power" aria-hidden="true"></i>' + v + '&deg;</span>'
                if prefix == 'H':
                        extra = '<span class="event-type-h"><i class="mdi mdi-water-percent" aria-hidden="true"></i>' + v + '%</span>'
                if prefix == 'B':
                    vv = v.split('|')
                    brightness = vv[0]
                    extrainfo = ""
                    if len(vv) > 1 :
                        color = vv[1]
                        colorValue = color[1:]
                        if color[0] == 'K':
                            extrainfo = ' <span class="colorkelvin">' + colorValue + '&deg;K</span>'
                        else:
                            extrainfo = ' <div class="colorsample" title="#' + color + '" style="background-color:#' + color + ';" ></div>'
                    if brightness[0] == 'A':
                        brightness = brightness[1:]
                        extra = '<span class="event-type-b"><i class="mdi mdi-lightbulb" aria-hidden="true"></i>' + brightness +  extrainfo +'</span>'
                    else:
                        extra = '<span class="event-type-b"><i class="mdi mdi-lightbulb" aria-hidden="true"></i>' + brightness + '%' + extrainfo + '</span>'


            result += '<span>' + t + extra + '</span >'
        return result

    return dict(format_event=format_event)


@app.context_processor
def utility_processor():
    def get_friendly_html_dow(value: str, is_on: bool):
        result: str = "<div>"
        if len(value) > 0:
            onOffClass = "dowHiglightG" if is_on else "dowHiglightR"
            for wd in range(1, 8):
                d = weekday[wd]
                dclass = ""
                if str(wd) in value:
                    dclass = onOffClass
                result += '<div class="dowIcon ' + dclass + ' " >' + d + '</div>'
            result += '</div>'
        return result

    return dict(get_friendly_html_dow=get_friendly_html_dow)


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        printlog("STATUS: MQTT connected! ")
        client.publish(lwt_topic, payload="online", qos=0, retain=True)
        client.subscribe("homeassistant/switch/simplescheduler/#")
    else:
        printlog("ERROR: MQTT Error " + str(rc))


def on_message(client, userdata, msg):
    global has_changed
    payload = 0
    pieces = msg.topic.split("/")
    if len(pieces) > 4:
        if pieces[4] == "set":
            sid = pieces[3]
            printlog('MQTT: RCV ' + msg.topic + " --> " + msg.payload.decode())
            if msg.payload.decode() == 'ON':
                payload = 1
            update_json_file(sid, 'enabled', payload)
            if options['MQTT']['enabled']:
                mqtt_publish_state(client, sid, payload, True)
                has_changed = "1"


def get_statusbar_info():
    r = {
        "sunrise": "N/A",
        "sunset": "N/A",
        "timezone": "N/A",
        "scheduler": "Not running",
        "mqtt": "Disabled"
    }
    tz = get_ha_timezone()
    sunrise, sunset = get_sun(tz)
    r['timezone'] = tz if tz else "N/A"
    r['sunrise'] = sunrise.strftime("%H:%M") if sunrise else "N/A"
    r['sunset'] = sunset.strftime("%H:%M") if sunset else "N/A"
    pid = get_scheduler_pid()
    if pid > 0:
        r['scheduler'] = "Running (PID %s)" % pid
    if options['MQTT']['enabled']:
        r['mqtt'] = "Connected" if mqttclient.is_connected() else "Disconnected"
    return r


def get_switch_list(domains):
    full_switch_list = []
    url = simpleschedulerconf.HASSIO_URL + "/states"
    headers = {'content-type': 'application/json', 'Authorization': 'Bearer ' + simpleschedulerconf.SUPERVISOR_TOKEN}
    try:
        r = requests.get(url=url, headers=headers, timeout=request_timeout)
        for block in r.json():
            item = {
                "id": block["entity_id"],
                "state": block["state"],
                "friendly_name": "",
                "domain": "",
            }

            pieces = block["entity_id"].split(".")
            item["domain"] = pieces[0]

            attributes = block["attributes"]
            if "friendly_name" in attributes:
                item["friendly_name"] = attributes["friendly_name"]

            if item["domain"] in domains:
                full_switch_list.append(item)

        full_switch_list.sort(key=lambda x: x["id"], reverse=False)
    except:
        printlog("ERROR: Unable to obtain entities info from Home Assistant")
    return full_switch_list


def get_domains():
    domain_list = []
    url = simpleschedulerconf.HASSIO_URL + "/states"
    headers = {'content-type': 'application/json', 'Authorization': 'Bearer ' + simpleschedulerconf.SUPERVISOR_TOKEN}
    try:
        r = requests.get(url=url, headers=headers, timeout=request_timeout)
        for block in r.json():

            pieces = block["entity_id"].split(".")
            if pieces[0] not in domain_list:
                domain_list.append(pieces[0])

        domain_list.sort()
    except:
        printlog("ERROR: Unable to obtain domain list from Home Assistant")
    return domain_list


def get_switch_friendly_names():
    friendly_names = {}
    url = simpleschedulerconf.HASSIO_URL + "/states"
    headers = {'content-type': 'application/json', 'Authorization': 'Bearer ' + simpleschedulerconf.SUPERVISOR_TOKEN}
    try:
        r = requests.get(url=url, headers=headers, timeout=request_timeout)
        for block in r.json():
            key = block["entity_id"]
            value = key
            if "friendly_name" in block["attributes"]:
                value = block["attributes"]["friendly_name"]
            friendly_names[key] = value
    except:
        printlog("ERROR: Unable to obtain entities names from Home Assistant")
    return friendly_names


def update_json_file(object_id, field_name, field_value):
    file = simpleschedulerconf.json_folder + object_id + '.json'
    try:
        if os.path.exists(file):
            with open(file, "r") as jsonFile:
                data = json.load(jsonFile)
            data[field_name] = field_value
            with open(file, "w") as jsonFile:
                json.dump(data, jsonFile)
    except:
        printlog("ERROR: Unable to update JSON file")
    return True


def load_json_schedulers():
    ss = []
    os.chdir(simpleschedulerconf.json_folder)
    for file in glob.glob("*.json"):
        with open(file, "r") as read_file:
            try:
                ss.append(json.load(read_file))
            except:
                printlog("ERROR: scheduler file %s is corrupted" % file)
    return ss


def mqtt_publish_state(client, object_id, pub_value, echo=False):
    payload = 'OFF'
    if pub_value:
        payload = 'ON'
    topic = 'homeassistant/switch/simplescheduler/' + object_id + '/state'
    client.publish(topic, payload, qos=0, retain=1)
    if echo:
        printlog('MQTT: PUB ' + topic + ' --> ' + payload)


def mqtt_send_config(client):
    schedulers = load_json_schedulers()
    payload_template = '{"unique_id": "simplescheduler_###",' \
                       '"name": "SimpleScheduler: @@@" ,' \
                       '"icon":"mdi:calendar-clock" ,' \
                       '"cmd_t": "homeassistant/switch/simplescheduler/###/set",' \
                       '"stat_t": "homeassistant/switch/simplescheduler/###/state",' \
                       '"avty_t": "homeassistant/switch/simplescheduler/availability",' \
                       '"pl_avail":"online",' \
                       '"pl_not_avail":"offline"}'
    config_topic_template = 'homeassistant/switch/simplescheduler/###/config'
    for S in schedulers:
        if S and 'name' in S:
            topic = config_topic_template.replace('###', S['id'])
            payload = payload_template.replace('###', S['id'])
            payload = payload.replace('@@@', S['name'])
            # slug = slugify(S['name'], separator="_")
            # payload = payload.replace('&&&', slug)
            client.publish(topic, payload, qos=0, retain=1)
            # time.sleep(.1)
            mqtt_publish_state(client, S['id'], S['enabled'], False)
            # time.sleep(.1)


def get_options():
    # path = "/data/options.json"
    path = os.path.join(simpleschedulerconf.json_folder, "options.dat")
    if not os.path.exists(path):
        path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "options.dat")
    with open(path, "r", encoding='utf-8') as read_file:
        opt = json.load(read_file)
    return opt


def get_css():
    global options
    path_light = os.path.join(os.path.dirname(os.path.realpath(__file__)), "templates", "light.css")
    path_dark = os.path.join(os.path.dirname(os.path.realpath(__file__)), "templates", "dark.css")
    css = ""
    # try:
    with open(path_light, "r", encoding='utf-8') as css_file:
        css += css_file.read()
    if options['dark_theme']:
        with open(path_dark, "r", encoding='utf-8') as css_file:
            css += css_file.read()
    # except:
    #     printlog("ERROR: Something went wrong while loading CSS")
    return css


def get_enabled_domains():
    enabled_domains = []
    opt = get_options()
    for d in opt['components']:
        if opt['components'][d]:
            enabled_domains.append(d)
    return enabled_domains


def get_switch_html_select_options():
    htmlstring: str = ''
    switch_list = get_switch_list(get_enabled_domains())
    comp = ""
    for s in switch_list:
        c = s['id'].split('.')
        if comp != c[0]:
            if comp != "":
                htmlstring += '</optgroup>'
            comp = c[0]
            htmlstring += '<optgroup label="' + comp + '">'
        name = s['id'] if s['friendly_name'] == "" else s['friendly_name'] + '(' + s['id'] + ')'
        htmlstring += '<option value="' + s['id'] + '">' + name + '</option>'
    htmlstring += '</optgroup>'
    htmlstring = htmlstring.replace(chr(39), "&#39;")
    return htmlstring


def get_json_template(t: str):
    t = t.lower()
    json_template: str = ''
    if t == 'w' or t == 'weekly':
        json_template = '{"id":"","name":"","enabled":"1","entity_id":[""],"weekly":{"on_1":"","on_2":"","on_3":"",' \
                        '"on_4":"","on_5":"","on_6":"","on_7":"","off_1":"","off_2":"","off_3":"","off_4":"",' \
                        '"off_5":"","off_6":"","off_7":""}} '
    if t == 'd' or t == 'daily' or t is None:
        json_template = '{"id":"","name":"","enabled":"1","entity_id":[""],"on_tod":"","on_dow":"","off_tod":"",' \
                        '"off_dow":""} '
    if t == 'r' or t == 'recurring':
        json_template = '{"id":"","name":"","enabled":"1","entity_id":[""],"recurring":{"on_start":"","on_end":"",' \
                        '"on_interval":"","off_start":"","off_end":"","off_interval":""},"on_tod":"","on_dow":"",' \
                        '"off_tod":"","off_dow":""} '

    return json_template


def get_sort_list():
    sorting = {}
    sort_file_path = simpleschedulerconf.json_folder + "sort.dat"
    if os.path.exists(sort_file_path):
        with open(sort_file_path, "r") as sort_file:
            order = json.load(sort_file)
        i = 0
        for sid in order['id_order']:
            sorting[sid] = i
            i = i + 1
    return sorting


def save_sort_list(data):
    idlist = []
    for el in data:
        idlist.append(data[el])
    jsonlist = json.loads('{"id_order":[]}')
    jsonlist['id_order'] = idlist
    with open(simpleschedulerconf.json_folder + "sort.dat", "w") as sort_file:
        json.dump(jsonlist, sort_file)
    return True


def get_events_in_html():
    events_html = {"events_on": "events_on", "events_off": "events_off", "days_on": "days_on", "days_off": "days_off"}
    return events_html


def get_entity_status(e, check):
    response = ""
    url = simpleschedulerconf.HASSIO_URL + "/states/" + e
    headers = {'content-type': 'application/json', 'Authorization': 'Bearer ' + simpleschedulerconf.SUPERVISOR_TOKEN}
    try:
        r = requests.get(url=url, headers=headers, timeout=request_timeout)
        result = r.json()
        response = str(result['state']).lower()
        if check:
            altered_response = response
            domain = e.lower().split(".")
            if domain[0] == 'cover':
                altered_response = 'on' if response == "open" else 'off'
            if domain[0] == 'climate' and response != 'off':
                altered_response = 'on'

            response = altered_response
    except:
        printlog("ERROR: Unable to obtain entity status from Home Assistant")
    return response


def call_ha_api(command_url: str, post_data: str):
    opt = get_options()
    headers = {'content-type': 'application/json', 'Authorization': 'Bearer ' + simpleschedulerconf.SUPERVISOR_TOKEN}
    try:
        r = requests.post(url=command_url, data=post_data, headers=headers, timeout=request_timeout)
        command = command_url.replace(simpleschedulerconf.HASSIO_URL + "/services/", "")
        if opt['debug']: printlog("DEBUG: %s %s" % (command, post_data))
        if r.status_code != 200:
            printlog("ERROR:  Error calling HA API " + str(r.status_code))
    except:
        printlog("ERROR: Unable to call Home Assistant service")
    return True


def call_ha(eid_list, action, passedvalue, friendly_name):
    if not isinstance(eid_list, list):
        eid_list = {eid_list}
    for eid in eid_list:
        command = "Turning " + action.upper()
        extra = ""
        v = ""
        value = passedvalue.upper()
        domain = eid.split(".")
        command_url = simpleschedulerconf.HASSIO_URL + "/services/" + domain[0] + "/turn_" + action
        postdata = '{"entity_id":"%s"}' % eid

        if action == 'on':
            if domain[0] == "light" and value != "":
                pieces = value.split("|")
                part_one = pieces[0]
                part_two = pieces[1]

                if part_one[0] == "A":
                    v = int(part_one[1:])
                    extra = "to %d" % v
                elif part_one.isdigit():
                    v = int(int(part_one) * 2.55)
                    extra = "to " + part_one + '%'
                postdata = '{"entity_id":"%s","brightness":"%d"}' % (eid, v)

                if part_two:
                    if part_two[0]=="K":
                        kelvin = int(part_two[1:])
                        postdata = '{"entity_id":"%s","brightness":"%d","color_temp_kelvin":"%d"}' % (eid, v, kelvin)
                    else:
                        HEX_color = part_two
                        rgb = list(int(HEX_color[i:i + 2], 16) for i in (0, 2, 4))
                        postdata = '{"entity_id":"%s","brightness":"%d","rgb_color":%s}' % (eid, v , rgb)

            if domain[0] == "fan" and value != "":
                v = value
                extra = "to " + v + '%'
                postdata = '{"entity_id":"%s","percentage":"%s"}' % (eid, v)

            if domain[0] == "cover":
                if value != "":
                    command_url = simpleschedulerconf.HASSIO_URL + "/services/cover/set_cover_position"
                    postdata = '{"entity_id":"%s","position":"%s"}' % (eid, value)
                    command = "Setting"
                    extra = "position to " + value + '%'
                else:
                    if action == "on":
                        command_url = simpleschedulerconf.HASSIO_URL + "/services/cover/open_cover"
                        command = "Opening"

            if domain[0] == "climate" and value != "":
                if value[0] == "O":
                    v = value[1:]
                    command_url = simpleschedulerconf.HASSIO_URL + "/services/climate/set_temperature"
                    postdata = '{"entity_id":"%s","temperature":"%s"}' % (eid, v)
                    command = "Setting"
                    extra = "temperature to " + v + '°'

        else:
            if domain[0] == "cover":
                command_url = simpleschedulerconf.HASSIO_URL + "/services/cover/close_cover"
                command = "Closing"

        printlog("SCHED: %s [%s] %s" % (command, friendly_name.get(eid, eid), extra))
        call_ha_api(command_url, postdata)

        if domain[0] == "climate" and value != "":
            if value[0] != "O":
                command_url = simpleschedulerconf.HASSIO_URL + "/services/climate/set_temperature"
                postdata = '{"entity_id":"%s","temperature":"%s"}' % (eid, value)
                call_ha_api(command_url, postdata)
                command = "Setting"
                extra = "temperature to " + value + '°'
                printlog("SCHED: %s [%s] %s" % (command, friendly_name.get(eid, eid), extra))

        if domain[0] == "humidifier" and value != "":
            command_url = simpleschedulerconf.HASSIO_URL + "/services/humidifier/set_humidity"
            postdata = '{"entity_id":"%s","humidity":"%s"}' % (eid, value)
            call_ha_api(command_url, postdata)
            command = "Setting"
            extra = "humidity to " + value + '%'
            printlog("SCHED: %s [%s] %s" % (command, friendly_name.get(eid, eid), extra))

    return True


def is_a_retry_domain(entity):
    response = True
    if "scene." in entity: response = False
    if "script." in entity: response = False
    if "automation." in entity: response = False
    if "media_player." in entity: response = False
    if "camera." in entity: response = False
    return response


def get_events_array(s):
    s = s.upper().replace(',', ' ').replace(';', ' ').strip()
    s = re.sub(' +', ' ', s)
    events = s.split(' ')
    return events


def evaluate_event_time(s, sunrise, sunset):
    event = ""
    sunrise_day = ""
    sunset_day = ""

    if sunrise:
        sunrise_day = sunrise.strftime("%d")
    if sunset:
        sunset_day = sunset.strftime("%d")
    today = datetime.now().strftime("%d")
    if len(s) > 3:
        p = s.upper().split('>')
        event = p[0]
        operator = "~"
        if event[:3] == "SUN":
            if event.find('+') != -1: operator = "+"
            if event.find('-') != -1: operator = "-"
            eventime = event.split(operator)
            event = ""
            if eventime[0] == "SUNRISE" and sunrise_day == today:
                event = sunrise.strftime("%H:%M")
            if eventime[0] == "SUNSET" and sunset_day == today:
                event = sunset.strftime("%H:%M")
            if event != "" and len(eventime) > 1:
                hm = event.split(":")
                if operator == '+':
                    event = (datetime(2022, 1, 1, int(hm[0]), int(hm[1])) + timedelta(
                        minutes=int(eventime[1]))).strftime("%H:%M")
                else:
                    event = (datetime(2022, 1, 1, int(hm[0]), int(hm[1])) - timedelta(
                        minutes=int(eventime[1]))).strftime("%H:%M")
        if event:
            hm = event.split(":")
            if 0 <= int(hm[0]) < 24 and 0 <= int(hm[1]) < 60:
                event = datetime(2022, 1, 1, int(hm[0]), int(hm[1])).strftime("%H:%M")  # fix missing leading zeroes

    return event


def get_sun(tz, sunrise="", sunset=""):
    if tz:
        mytimezone = pytz.timezone(tz)
        url = simpleschedulerconf.HASSIO_URL + "/states/sun.sun"
        headers = {'content-type': 'application/json',
                   'Authorization': 'Bearer ' + simpleschedulerconf.SUPERVISOR_TOKEN}
        try:
            r = requests.get(url=url, headers=headers, timeout=request_timeout)
            result = r.json()
            response = result['attributes']
            sunrise = datetime.fromisoformat(response['next_rising']).astimezone(mytimezone)
            sunset = datetime.fromisoformat(response['next_setting']).astimezone(mytimezone)
        except:
            printlog("ERROR: Unable to obtain sun info from Home Assistant")
    return sunrise, sunset


def get_ha_timezone():
    response = ""
    url = simpleschedulerconf.HASSIO_URL + "/config"
    headers = {'content-type': 'application/json', 'Authorization': 'Bearer ' + simpleschedulerconf.SUPERVISOR_TOKEN}
    try:
        r = requests.get(url=url, headers=headers, timeout=request_timeout)
        result = r.json()
        response = result['time_zone']
    except:
        printlog("ERROR: Unable to obtain timezone from Home Assistant")
    else:
        try:
            if not response:
                response = os.environ["TZ"]
        except:
            printlog("ERROR: Unable to obtain timezone from OS")
    return response


def get_scheduler_pid():
    pid = 0
    try:
        for process in psutil.process_iter():
            if "/simplescheduler/scheduler.py" in process.cmdline():
                pid = process.pid
    except:
        printlog("ERROR: Unable to obtain scheduler PID")
    return pid


def printlog(message):
    t = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    fullrow = "[%s] %s" % (t, message)
    print(fullrow)

    if not os.path.exists(simpleschedulerconf.json_folder):
        os.makedirs(simpleschedulerconf.json_folder)

    logfilepath = os.path.join(simpleschedulerconf.json_folder, "simplescheduler.log")
    with open(logfilepath, "a", encoding='utf-8') as logfile:
        logfile.write(fullrow + "\n")


def init():
    global options
    global weekday
    global schedulers_list
    global ha_timezone
    global domain_list

    options = get_options()
    weekday = \
        [
            options['translations']['text_sunday'][:2],
            options['translations']['text_monday'][:2],
            options['translations']['text_tuesday'][:2],
            options['translations']['text_wednesday'][:2],
            options['translations']['text_thursday'][:2],
            options['translations']['text_friday'][:2],
            options['translations']['text_saturday'][:2],
            options['translations']['text_sunday'][:2]
        ]

    if options['debug']:
        printlog("   QUESTION: What do you get if you multiply six by nine?")
        printlog("   ANSWER: 42")

    # domain_list = get_domains()
    schedulers_list = load_json_schedulers()

    ha_timezone = get_ha_timezone()


if __name__ == '__main__':

    printlog('STATUS: Starting main program')

    init()

    if options['MQTT']['enabled']:
        printlog('STATUS: Starting MQTT')
        mqttclient = mqtt.Client(client_id="SimpleScheduler", clean_session=False)
        mqttclient.on_connect = on_connect
        mqttclient.on_message = on_message
        mqttclient.will_set(lwt_topic, payload="offline", qos=0, retain=True)
        mqttclient.username_pw_set(options['MQTT']['username'], options['MQTT']['password'])
        try:
            mqttclient.connect(options['MQTT']['server'], int(options['MQTT']['port']), 60)
        except:
            printlog("ERROR: MQTT Connection failed")
        else:
            mqttclient.loop_start()
            mqtt_send_config(mqttclient)

    # Disable Flask Messages
    log = logging.getLogger('werkzeug')
    log.disabled = True
    flask.cli.show_server_banner = lambda *args: None
    # app.logger.disabled = True

    printlog('STATUS: Starting WebServer')
    app.run(host='0.0.0.0', port=8099, debug=False)
