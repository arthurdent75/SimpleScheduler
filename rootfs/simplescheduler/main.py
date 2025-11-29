from flask import Flask, render_template, request, redirect, make_response
import paho.mqtt.client as mqtt
import flask.cli
import logging
import glob
import os
import json
from datetime import datetime, timedelta
import pytz
import requests
import time
import uuid
import threading
import re
import base64
import fnmatch

import simpleschedulerconf

valid_domains = ["light", "scene", "switch", "button", "script", "camera", "climate", "cover", "vacuum", "fan", "humidifier",
                 "valve","automation", "input_boolean", "input_button","media_player"]
lwt_topic = "homeassistant/switch/simplescheduler/availability"
no_notification_placeholder = " - disabled - "
sun_data = ""
schedulers_list = []
options: dict = {}
weekday = []
has_changed: bool = False
mqttclient = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="SimpleScheduler", clean_session=False)
mqtt_enabled = False
ha_timezone = "utc"
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
                           statusbarinfo=get_statusbar_info(),
                           groups=get_groups()
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
        mqttclient.publish('homeassistant/switch/simplescheduler/' + sid + '/config', "", qos=0, retain=True)
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


@app.route('/update_json', methods=['GET'])
def webserver_update_json():
    global mqtt_enabled
    args = request.args
    sid = args.get('id')
    f:str = args.get('f')
    v = args.get('v')
    if f=="enabled": v=int(v)
    result=update_json_file(sid,f,v)
    r = '1' if result else '0'
    if options['MQTT']['enabled']:
        mqtt_enabled = True
        mqtt_send_config(mqttclient)
    return make_response(r, 200)


@app.route('/config', methods=['GET'])
def webserver_config():
    return render_template('config.html',
                           o=get_options(),
                           d=valid_domains,
                           notifiers=get_notifiers()
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
            if item=="excluded_entities":
                value = re.sub(r"[^\n\ra-z0-9_*.]", "", value.lower())
            jsondata[item] = value

    jsondata["translations"] = translations
    jsondata["components"] = components
    jsondata["MQTT"] = mqttconf

    option_file_path = os.path.join(simpleschedulerconf.json_folder, "options.dat")
    with open(option_file_path, 'w') as option_file:
       json.dump(jsondata, option_file) # type: ignore

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
            json.dump(param, jsonFile) # type: ignore
    return redirect("main")


@app.route("/update", methods=['POST'])
def webserver_update():
    on_tod = off_tod = on_dow = off_dow = on_tod_false = off_tod_false = ""
    sid = request.form.get('id')
    enabled = request.form.get("enabled")
    dontretry = request.form.get("dontretry")
    template = request.form.get("template")
    name = request.form.get("name")
    entity_id = request.form.getlist('entity_id[]')
    sched_type:str = request.form.get('type',"")
    if sched_type != 'weekly':
        on_tod = request.form.get('on_tod' , "")
        on_tod_false = request.form.get('on_tod_false')
        off_tod = request.form.get('off_tod')
        off_tod_false = request.form.get('off_tod_false')
        on_dow = ""
        off_dow = ""
        for o in request.form.getlist('on_dow[]'):
            on_dow += o
        for o in request.form.getlist('off_dow[]'):
            off_dow += o

    data = json.loads(get_json_template(sched_type))
    data['id'] = sid
    data['name'] = name if name else sid
    data['enabled'] = enabled if enabled else 0
    data['dontretry'] = dontretry if dontretry else 0
    data['template'] = template.replace('"',"'") if template else ''
    data['entity_id'] = entity_id
    if sched_type == 'weekly':
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
    elif sched_type == 'recurring':
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
        data['on_tod_false'] = on_tod_false
        data['off_tod_false'] = off_tod_false
    file = simpleschedulerconf.json_folder + sid + '.json'
    with open(file, 'w') as jsonFile:
        json.dump(data, jsonFile) # type: ignore
    if options['MQTT']['enabled']:
        mqtt_send_config(mqttclient)
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

@app.route("/validatetemplate", methods=['GET'])
def webserver_validatetemplate():
    response = ""
    data = request.args
    t = data["t"]
    headers = {'content-type': 'application/json', 'Authorization': 'Bearer ' + simpleschedulerconf.SUPERVISOR_TOKEN}
    command_url = simpleschedulerconf.HASSIO_URL + "/template"
    post_data = '{"template":"' + t + '"}'
    try:
        r = requests.post(url=command_url, data=post_data, headers=headers, timeout=request_timeout)
        if r.content:
            response = r.content.decode().lower()
        if r.status_code != 200:
            if "message" in response:
                json_response = json.loads(r.content)
                response = json_response['message']
    finally:
        return make_response(response, 200)

@app.context_processor
def utility_processor():
    def format_event(value: str, showvalue: bool):
        if not value: return ''
        result: str = ""
        value = encode_braces_to_base32(value)
        events = value.upper().replace(',', ' ').replace(';', ' ').split(" ")

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
                    if len(vv) > 1:
                        color = vv[1]
                        colorValue = color[1:]
                        if color[0] == 'K':
                            extrainfo = ' <span class="colorkelvin">' + colorValue + '&deg;K</span>'
                        else:
                            extrainfo = ' <div class="colorsample" title="#' + color + '" style="background-color:#' + color + ';" ></div>'
                    if brightness[0] == 'A':
                        brightness = brightness[1:]
                        extra = '<span class="event-type-b"><i class="mdi mdi-lightbulb" aria-hidden="true"></i>' + brightness + extrainfo + '</span>'
                    else:
                        extra = '<span class="event-type-b"><i class="mdi mdi-lightbulb" aria-hidden="true"></i>' + brightness + '%' + extrainfo + '</span>'
                if prefix == 'J':
                    extra = ' <span class="event-type-j"> <i class="mdi mdi-code-json" aria-hidden="true"></i></span>'
            if t: result += '<span>' + t + extra + '</span >'

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


def on_connect(client, userdata, flags, rc,properties):
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
    if mqtt_enabled and mqttclient is not None:
        r['mqtt'] = "Connected" if mqttclient.is_connected() else "Disconnected"
    return r


def get_switch_list(domains):
    full_switch_list = []
    url = simpleschedulerconf.HASSIO_URL + "/states"
    headers = {'content-type': 'application/json', 'Authorization': 'Bearer ' + simpleschedulerconf.SUPERVISOR_TOKEN}
    try:
        opt = get_options()
        exclusions = opt.get('excluded_entities', "").splitlines()
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
                if not any(fnmatch.fnmatch(block["entity_id"], pattern) for pattern in exclusions):
                    full_switch_list.append(item)

        full_switch_list.sort(key=lambda x: x["id"], reverse=False)
    except Exception as e:
        printlog("ERROR: Unable to obtain entities info from Home Assistant",e)
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
    except Exception as e:
        printlog("ERROR: Unable to obtain domain list from Home Assistant",e)
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
    except Exception as e:
        printlog("ERROR: Unable to obtain entities names from Home Assistant",e)
    return friendly_names


def update_json_file(object_id, field_name, field_value):
    file = simpleschedulerconf.json_folder + object_id + '.json'
    try:
        if os.path.exists(file):
            with open(file, "r") as jsonFile:
                data = json.load(jsonFile)
            data[field_name] = field_value
            with open(file, "w") as jsonFile:
                json.dump(data, jsonFile) # type: ignore
    except Exception as e:
        printlog("ERROR: Unable to update JSON file",e)
    return True


def load_json_schedulers():
    ss = []
    os.chdir(simpleschedulerconf.json_folder)

    for file in glob.glob("*.json"):
        with open(file, "r") as read_file:
            try:
                data = json.load(read_file)
                ss.append(data)

                filename_no_ext = os.path.splitext(file)[0]
                json_id = str(data.get("id", "")).strip()

                if json_id and filename_no_ext != json_id:
                    new_filename = f"{json_id}.json"
                    if not os.path.exists(new_filename):
                        printlog(f"WARNING: Renaming {file} to {new_filename}")
                        os.rename(file, new_filename)
                    else:
                        printlog(f"WARNING: Cannot rename {file} to {new_filename}, file already exists!")
            except Exception as e:
                printlog("ERROR: scheduler file %s is corrupted" % file, e)

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
            mqtt_publish_state(client, S['id'], S['enabled'])
            # time.sleep(.1)


def get_options():
    path = os.path.join(simpleschedulerconf.json_folder, "options.dat")
    if not os.path.exists(path):
        path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "options.default")
    with open(path, "r", encoding='utf-8') as read_file:
        opt = json.load(read_file)
    return opt


def get_css():
    global options
    path_light = os.path.join(os.path.dirname(os.path.realpath(__file__)), "templates", "style.css")
    css = ""
    try:
        with open(path_light, "r", encoding='utf-8') as css_file:
            css += css_file.read()
    except Exception as e:
            printlog("ERROR: Something went wrong while loading CSS",e)
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
        name = s['id'] if s['friendly_name'] == "" else s['friendly_name'] + ' (' + s['id'] + ')'
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
    try:
        if os.path.exists(sort_file_path):
            with open(sort_file_path, "r") as sort_file:
                order = json.load(sort_file)
            i = 0
            for sid in order['id_order']:
                sorting[sid] = i
                i = i + 1
    except Exception as e:
        printlog("ERROR: corrupted sort file",e)
    return sorting

def get_groups():
    g = ""
    group_file_path = simpleschedulerconf.json_folder + "group.dat"
    try:
        if os.path.exists(group_file_path):
            with open(group_file_path, "r") as group_file:
                g = json.load(group_file)
    except Exception as e:
        printlog("ERROR: corrupted group file",e)
    return g

def save_sort_list(data):
    idlist = []
    json_groups=""
    for el in data:
        if el == "groups":
            base64_groups = data[el]
            json_groups = base64.b64decode(base64_groups).decode('utf-8')
        else:
            idlist.append(data[el])
    jsonlist = json.loads('{"id_order":[]}')
    jsonlist['id_order'] = idlist
    with open(simpleschedulerconf.json_folder + "sort.dat", "w") as sort_file:
        json.dump(jsonlist, sort_file) # type: ignore
    if  json_groups.count('{') == json_groups.count('}'):
        with open(simpleschedulerconf.json_folder + "group.dat", "w") as group_file:
            group_file.write(json_groups)
    else:
        printlog("ERROR: Malformed group list received")
        printlog("       "+json_groups)
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
            if domain[0] == 'cover' or domain[0] == 'valve':
                altered_response = 'on' if response == "open" else 'off'
            if domain[0] == 'climate' and response != 'off':
                altered_response = 'on'
            if domain[0] == 'vacuum':
                altered_response = 'on' if response == "cleaning" else 'off'

            response = altered_response
    except Exception as e:
        printlog("ERROR: Unable to obtain entity status from Home Assistant",e)
    return response


def evaluate_template(t: str):
    opt = get_options()
    response: bool = False
    content = ""
    headers = {'content-type': 'application/json', 'Authorization': 'Bearer ' + simpleschedulerconf.SUPERVISOR_TOKEN}
    command_url = simpleschedulerconf.HASSIO_URL + "/template"
    post_data = '{"template":"' + t + '"}'
    try:
        if opt['debug']: printlog("DEBUG: Evaluating template: %s" % (t))
        r = requests.post(url=command_url, data=post_data, headers=headers, timeout=request_timeout)
        if r.content:
            content = r.content.decode()
            if r.status_code == 400 and "unavailable" in content.lower():
                return False
        if r.status_code != 200:
            printlog("ERROR: Error calling HA API " + str(r.status_code))
            if "message" in content.lower():
                json_response = json.loads(r.content)
                error= json_response['message']
                printlog("ERROR: template error: %s" % (error))
        else:
            if content.lower() == 'true':
                response = True

    except Exception as e:
        printlog("ERROR: Unable to call Home Assistant template API",e)
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
    except requests.exceptions.ReadTimeout:
        if not ("/script/" in command_url):
            printlog("ERROR: Unable to call Home Assistant service (timeout)")
            # NB: when you call a script, the response is sent when execution ends,
            #     so scripts with delay throw timeout exception
    except Exception as e:
        printlog("ERROR: Unable to call Home Assistant service",e)
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
                if len(pieces) > 1:
                    part_two = pieces[1]
                else:
                    part_two = ''

                if part_one[0] == "A":
                    v = int(part_one[1:])
                    extra = "to %d" % v
                elif part_one.isdigit():
                    v = int(int(part_one) * 2.55)
                    extra = "to " + part_one + '%'
                postdata = '{"entity_id":"%s","brightness":"%d"}' % (eid, v)

                if part_two:
                    if part_two[0] == "K":
                        kelvin = int(part_two[1:])
                        postdata = '{"entity_id":"%s","brightness":"%d","color_temp_kelvin":"%d"}' % (eid, v, kelvin)
                    else:
                        HEX_color = part_two
                        rgb = list(int(HEX_color[i:i + 2], 16) for i in (0, 2, 4))
                        postdata = '{"entity_id":"%s","brightness":"%d","rgb_color":%s}' % (eid, v, rgb)

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

            if domain[0] == "valve":
                if value != "":
                    command_url = simpleschedulerconf.HASSIO_URL + "/services/valve/set_valve_position"
                    postdata = '{"entity_id":"%s","position":"%s"}' % (eid, value)
                    command = "Setting"
                    extra = "position to " + value + '%'
                else:
                    if action == "on":
                        command_url = simpleschedulerconf.HASSIO_URL + "/services/valve/open_valve"
                        command = "Opening"

            if domain[0] == "climate" and value != "":
                if value[0] == "O":
                    v = value[1:]
                    command_url = simpleschedulerconf.HASSIO_URL + "/services/climate/set_temperature"
                    postdata = '{"entity_id":"%s","temperature":"%s"}' % (eid, v)
                    command = "Setting"
                    extra = "temperature to " + v + '°'

            if domain[0] == "vacuum":
                command_url = simpleschedulerconf.HASSIO_URL + "/services/vacuum/start"
                command = "Starting"

            if domain[0] == "script" and value != "":
                params = base64.b32decode(passedvalue).decode()
                command_url = simpleschedulerconf.HASSIO_URL + "/services/script/"+eid.replace("script.","")
                postdata = params
                command = "Executing"
                extra = "with params " + params

        else:

            if domain[0] == "vacuum":
                command_url = simpleschedulerconf.HASSIO_URL + "/services/vacuum/return_to_base"
                command = "Returning to base"

            if domain[0] == "cover":
                command_url = simpleschedulerconf.HASSIO_URL + "/services/cover/close_cover"
                command = "Closing"

            if domain[0] == "valve":
                command_url = simpleschedulerconf.HASSIO_URL + "/services/valve/close_valve"
                command = "Closing"

            if domain[0] == "scene":
                # command_url = simpleschedulerconf.HASSIO_URL + "/services/scene/turn_on"
                # command = "Turning ON"
                continue

        if domain[0] == "button":
            command_url = simpleschedulerconf.HASSIO_URL + "/services/button/press"
            command = "Pressing"

        if domain[0] == "input_button":
            command_url = simpleschedulerconf.HASSIO_URL + "/services/input_button/press"
            command = "Pressing"

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

def notify_on_error(message):
    response = ""
    opt : dict = get_options()
    notifier = opt.get('notifier', '')

    if notifier != no_notification_placeholder and len(notifier)>0 :
        headers = {'content-type': 'application/json', 'Authorization': 'Bearer ' + simpleschedulerconf.SUPERVISOR_TOKEN}
        command_url = simpleschedulerconf.HASSIO_URL + "/services/notify/" + notifier
        post_data = '{"message":"%s"}' % message
        try:
            r = requests.post(url=command_url, data=post_data, headers=headers, timeout=request_timeout)
            if r.content:
                response = r.content.decode().lower()
                printlog("SCHED:  ↳ Notification sent to %s" % notifier)
            if r.status_code != 200:
                if "message" in response:
                    json_response = json.loads(r.content)
                    response = json_response['message']
                printlog("ERROR:  ↳ Notification NOT sent - " +response )
        except Exception as e:
            printlog("ERROR:  ↳ Something went wrong ",e )
    return True

def get_notifiers():
    notifiers = [no_notification_placeholder]
    headers = {'content-type': 'application/json', 'Authorization': 'Bearer ' + simpleschedulerconf.SUPERVISOR_TOKEN}
    command_url = simpleschedulerconf.HASSIO_URL + "/services"
    try:
        response = requests.get(url=command_url, headers=headers, timeout=request_timeout)
        if response.status_code == 200 :
            services = response.json()
            for domain in services:
                if domain['domain'] == 'notify':
                    for service in domain['services']:
                        if service not in ["send_message","notify"]: notifiers.append(service)
        else:
            if "message" in response:
                json_response = json.loads(response.content)
                response = json_response['message']
            printlog("ERROR: Something went wrong getting notifiers - %s " % response)
    except Exception as e:
        printlog("ERROR: Something went wrong getting notifiers",e )

    return notifiers


def is_a_retry_domain(entity):
    response = True
    if "scene." in entity: response = False
    if "script." in entity: response = False
    if "automation." in entity: response = False
    if "media_player." in entity: response = False
    if "camera." in entity: response = False
    if "button." in entity: response = False
    if "input_button." in entity: response = False
    return response


def encode_braces_to_base32(input_str):
    def encode_match(match):
        json_str = match.group(1)
        json_str_clean = json_str.replace('\n', '').replace('\r', '')
        encoded = base64.b32encode(json_str_clean.encode()).decode()
        return f'J{encoded}'
    pattern = r'J({.*?})'
    result = re.sub(pattern, encode_match, input_str, flags=re.DOTALL)
    return result

def get_events_array(s):
    s = encode_braces_to_base32(s)
    s = s.replace('\n', '').replace('\r', '')
    s = s.upper().replace(',', ' ').replace(';', ' ').strip()
    s = re.sub(' +', ' ', s)
    events = s.split(' ')
    return events


def evaluate_event_time(s, sunrise, sunset):
    event = ""
    sunrise_day = ""
    sunset_day = ""

    s = s.replace('.', ':')
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
        except Exception as e:
            printlog("ERROR: Unable to obtain sun info from Home Assistant", e)
    return sunrise, sunset


def get_ha_timezone():
    response = ""
    url = simpleschedulerconf.HASSIO_URL + "/config"
    headers = {'content-type': 'application/json', 'Authorization': 'Bearer ' + simpleschedulerconf.SUPERVISOR_TOKEN}
    try:
        r = requests.get(url=url, headers=headers, timeout=request_timeout)
        result = r.json()
        response = result['time_zone']
    except Exception as e:
        printlog("ERROR: Unable to obtain timezone from Home Assistant",e)
    else:
        try:
            if not response:
                response = os.environ["TZ"]
        except Exception as e:
            printlog("ERROR: Unable to obtain timezone from OS",e)

    return response

def printlog(message,e=None ):
    fullrow2 = ""
    t = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    fullrow = "[%s] %s" % (t, message)
    print(fullrow)
    if e:
        fullrow2 = "[%s]        %s" % (t, e)
        print(fullrow2)

    if not os.path.exists(simpleschedulerconf.json_folder):
        os.makedirs(simpleschedulerconf.json_folder)

    logfilepath = os.path.join(simpleschedulerconf.json_folder, "simplescheduler.log")
    with open(logfilepath, "a", encoding='utf-8') as logfile:
        logfile.write(fullrow + "\n")
        if e:
            logfile.write(fullrow2 + "\n")


def init():
    global options
    global weekday
    global schedulers_list
    global ha_timezone
    global domain_list
    global mqtt_enabled

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

    # domain_list = get_domains()

    schedulers_list = load_json_schedulers()

    ha_timezone = get_ha_timezone()

    mqtt_enabled = options['MQTT']['enabled']


def run_flask():
    try:
        # Disable Flask Messages
        log = logging.getLogger('werkzeug')
        log.disabled = True
        flask.cli.show_server_banner = lambda *args: None
        # app.logger.disabled = True
        printlog('STATUS: Starting WebServer')
        app.run(host='0.0.0.0', port=8099, debug=False)
    except Exception as e:
        printlog(f"ERROR: Interface thread crashed: [ {e} ]")
        time.sleep(2)


def run_mqtt():
    global mqttclient
    while True:
        if mqtt_enabled:
                try:
                    printlog('STATUS: Starting MQTT')
                    mqttclient.on_connect = on_connect
                    mqttclient.on_message = on_message
                    mqttclient.will_set(lwt_topic, payload="offline", qos=0, retain=True)
                    mqttclient.username_pw_set(options['MQTT']['username'], options['MQTT']['password'])
                    mqttclient.connect(options['MQTT']['server'], int(options['MQTT']['port']), 60)
                    mqttclient.loop_start()
                    mqttclient.publish(lwt_topic, payload="online", qos=0, retain=True)
                    mqtt_send_config(mqttclient)
                    while mqtt_enabled:
                        time.sleep(1)
                    printlog("STATUS: MQTT disabled, disconnecting...")
                    mqttclient.publish(lwt_topic, payload="offline", qos=0, retain=True)
                    mqttclient.loop_stop()
                    mqttclient.disconnect()
                except Exception as e:
                    printlog(f"ERROR: MQTT thread error: [ {e} ]")
                    time.sleep(2)
        else:
            time.sleep(1)


def run_scheduler():
        try:
            command_queue = {}
            sunrise, sunset = "", ""

            printlog('STATUS: Starting Scheduler')

            while True:
                now = datetime.now()
                seconds = now.strftime("%S")
                first_event = True
                if seconds == '00':
                    opt : dict = get_options()
                    max_retry = min(max(int(opt.get('max_retry', 3)), 0), 5)

                    current_time = now.strftime("%H:%M")
                    current_dow = now.strftime("%w")
                    if current_dow == '0':
                        current_dow = '7'

                    if current_time == "00:01" or not sunrise or not sunset:
                        if opt.get('debug'):
                            printlog('DEBUG: Retrieving sunrise and sunset')
                        sunrise, sunset = get_sun(get_ha_timezone())

                    for s in load_json_schedulers():
                        if not s.get('enabled'):
                            continue

                        template = s.get('template', '')
                        dont_retry = s.get('dontretry', 0)
                        week_onoff = s.get('weekly')

                        if opt.get('debug'):
                            printlog(f"DEBUG: Parsing [{s['name']}] [{s['id']}]")

                        if week_onoff:
                            s['weekly'] = ''
                            s['on_tod'] = week_onoff.get(f'on_{current_dow}', '')
                            s['off_tod'] = week_onoff.get(f'off_{current_dow}', '')
                            s['on_dow'] = s['off_dow'] = current_dow

                        for action in ['on', 'off']:
                            if current_dow not in s.get(f'{action}_dow', ''):
                                continue

                            condition = True
                            if template:
                                condition = evaluate_template(template)
                                if opt.get('debug'):
                                    printlog(f"DEBUG: Evaluating template for [{s['name']}]: {condition}")
                            if not condition:
                                tod = s.get(f'{action}_tod_false', '')
                            else:
                                tod = s.get(f'{action}_tod', '')

                            for e in get_events_array(tod):
                                p = e.upper().split('>')
                                event_time = evaluate_event_time(p[0], sunrise, sunset)
                                value = p[1][1:] if len(p) > 1 else ""

                                if event_time != current_time:
                                    continue

                                # retrieve names only if there is an event and only on first event
                                if first_event:
                                    friendly_name = get_switch_friendly_names()
                                    first_event = False
                                    if opt.get('debug'): printlog(f"DEBUG: Retrieving entity names")

                                printlog(f"SCHED: Executing {action.upper()} actions for [{s['name']}]")
                                call_ha(s['entity_id'], action, value, friendly_name)

                                for entity in s['entity_id']:
                                    skip = len(value) > 0 and value[0] == 'O'
                                    if skip or dont_retry or max_retry <= 0:
                                        continue
                                    if is_a_retry_domain(entity):
                                        command_queue[uuid.uuid4().hex] = {
                                            "entity_id": entity,
                                            "sched_id": s['id'],
                                            "state": action,
                                            "value": value,
                                            "countdown": max_retry,
                                            "max_retry": max_retry
                                        }

                    time.sleep(5)

                    if opt.get('debug'):
                        printlog(f"DEBUG: Max Retry: {max_retry}")
                        printlog(f"DEBUG: Starting Queue management - Queue length: {len(command_queue)}")

                    for key in list(command_queue):
                        item = command_queue[key]
                        status = get_entity_status(item['entity_id'], True)

                        if opt.get('debug'):
                            printlog(f"DEBUG: ID:{key} | Entity status:{status.upper()} | Queue item:{item}")

                        name = friendly_name.get(item['entity_id'], item['entity_id'])
                        attempt = item['max_retry'] - item['countdown'] + 1

                        if status == 'unavailable':
                            printlog(f"SCHED: [{name}] is unavailable. Attempt {attempt} of {item['max_retry']}")
                        elif status != item['state']:
                            printlog(f"SCHED: Failed to set [{name}]. Retry {attempt} of {item['max_retry']}")
                            call_ha(item['entity_id'], item['state'], item['value'], friendly_name)
                        else:
                            printlog(f"SCHED: [{name}] is {status.upper()} as requested!")
                            command_queue.pop(key)
                            continue  # Skip countdown update

                        item['countdown'] -= 1
                        if item['countdown'] <= 0:
                            msg = f"SCHED: Giving up on [{name}]"
                            printlog(msg)
                            notify_on_error(msg)
                            command_queue.pop(key)

                    if opt.get('debug'):
                        printlog(f"DEBUG: Finished Queue management - Queue length: {len(command_queue)}")

                time.sleep(1)

        except Exception as e:
            printlog(f"ERROR: Scheduler thread crashed: [ {e} ]")
            time.sleep(2)

def start_thread(target):
    thread = threading.Thread(target=target, daemon=True)
    thread.start()
    return thread


if __name__ == '__main__':

    printlog('STATUS: Starting main program')

    init()

    if options['debug']:
        printlog("   QUESTION: What do you get if you multiply six by nine?")
        printlog("   ANSWER: 42")

    flask_thread = start_thread(run_flask)
    scheduler_thread = start_thread(run_scheduler)
    mqtt_thread = start_thread(run_mqtt)

    try:
        while True:
            if not flask_thread.is_alive():
                printlog("Restarting interface thread...")
                flask_thread = start_thread(run_flask)

            if not scheduler_thread.is_alive():
                printlog("Restarting scheduler thread...")
                scheduler_thread = start_thread(run_scheduler)

            if not mqtt_thread.is_alive()  :
                printlog("Restarting MQTT thread...")
                mqtt_thread = start_thread(run_mqtt)

            time.sleep(1)


    except KeyboardInterrupt:
        printlog("Shutting down...")
