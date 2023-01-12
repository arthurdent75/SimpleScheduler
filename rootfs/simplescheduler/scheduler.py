import uuid
from datetime import datetime
from time import sleep

import main

command_queue = {}
sunrise = ""
sunset = ""
options = []

if __name__ == '__main__':

    main.printlog('STATUS: Starting scheduler')

    while True:
        seconds = datetime.now().strftime("%S")
        if seconds == '00':
            options = main.get_options()
            try:
                max_retry = int(options['max_retry'])
            except:
                max_retry = 3
            if max_retry < 0: max_retry = 3
            if max_retry > 5: max_retry = 5
            current_time = datetime.now().strftime("%H:%M")
            current_dow = datetime.now().strftime("%w")
            schedulers_list = main.load_json_schedulers()
            friendly_name = main.get_switch_friendly_names()
            if current_time == "00:01" or sunset == "" or sunrise == "":
                if options['debug']:
                    main.printlog('DEBUG: Retrieving sunrise and sunset')
                sunrise, sunset = main.get_sun(main.get_ha_timezone())
            if current_dow == '0':
                current_dow = '7'
            for s in schedulers_list:
                if s['enabled']:
                    dont_retry = s.get('dontretry',0)
                    if options['debug']: main.printlog("DEBUG: Parsing [%s]" % s['name'])
                    week_onoff = s.get('weekly')

                    if week_onoff:
                        s['weekly'] = ''
                        s['on_tod'] = week_onoff['on_' + current_dow]
                        s['off_tod'] = week_onoff['off_' + current_dow]
                        s['on_dow'] = current_dow
                        s['off_dow'] = current_dow

                    if current_dow in s['on_dow']:
                        elist = main.get_events_array(s['on_tod'])
                        for e in elist:
                            value = ""
                            p = e.upper().split('>')
                            t = p[0]
                            if len(p) > 1:
                                value = p[1][1:]
                            event_time = main.evaluate_event_time(t, sunrise, sunset)
                            if event_time == current_time:
                                main.printlog("SCHED: Executing ON actions for [%s]" % s['name'])
                                main.call_ha(s['entity_id'], "on", value, friendly_name )
                                for entity in s['entity_id']:
                                    if (len(value) > 0 and value[0] != 'O') or not value :  # if TemperatureOnly don't add to queue
                                        if not dont_retry and max_retry > 0 :
                                            if main.is_a_retry_domain(entity):
                                                command_queue[uuid.uuid4().hex] = {"entity_id": entity, "sched_id": s['id'],
                                                                                   "state": "on", "value": value,
                                                                                   "countdown": max_retry,"max_retry": max_retry}

                    if current_dow in s['off_dow']:
                        elist = main.get_events_array(s['off_tod'])
                        for e in elist:
                            value = ""
                            p = e.upper().split('>')
                            t = p[0]
                            if len(p) > 1:
                                value = p[1][1:]
                            event_time = main.evaluate_event_time(t, sunrise, sunset)
                            if event_time == current_time:
                                main.printlog("SCHED: Executing OFF actions for [%s]" % s['name'])
                                main.call_ha(s['entity_id'], "off", value, friendly_name )
                                for entity in s['entity_id']:
                                    if (len(value) > 0 and value[0] != 'O') or not value:  # if TemperatureOnly don't add to queue
                                        if not dont_retry and max_retry > 0 :
                                            if main.is_a_retry_domain(entity):
                                                command_queue[uuid.uuid4().hex] = {"entity_id": entity, "sched_id": s['id'],
                                                                                   "state": "off", "value": value,
                                                                                   "countdown": max_retry,"max_retry": max_retry}

            sleep(5)

            if options['debug']: main.printlog("DEBUG: Max Retry: %d" % max_retry)
            if options['debug']: main.printlog("DEBUG: Starting Queue management - Queue length: %d" % len(command_queue))

            for key in command_queue.copy():

                value = command_queue[key]
                entity_status = main.get_entity_status(value['entity_id'], True)
                if options['debug']: main.printlog(
                    "DEBUG: ID:%s | Entity status:%s | Queue item:%s" % (key, entity_status.upper(), value))

                if entity_status == 'unavailable':
                    attempt = 1 +  int(value['max_retry']) - int(value['countdown'])
                    main.printlog("SCHED: [%s] is unavailable. Attempt %d of %d" % (
                        friendly_name.get(value['entity_id'], value['entity_id']), attempt, int(value['max_retry']) ))
                    command_queue[key]['countdown'] = int(value['countdown']) - 1
                    if command_queue[key]['countdown'] <= 0:
                        main.printlog(
                            "SCHED: Giving up on [%s]" % friendly_name.get(value['entity_id'], value['entity_id']))
                        command_queue.pop(key)
                else:
                    if entity_status != value['state']:
                        attempt = 1 +  int(value['max_retry']) - int(value['countdown'])
                        main.printlog("SCHED: Failed to set [%s]. Retry %d of %d " % (
                            friendly_name.get(value['entity_id'], value['entity_id']), attempt, int(value['max_retry'])))
                        main.call_ha(value['entity_id'], value['state'], value['value'], friendly_name )
                        command_queue[key]['countdown'] = int(value['countdown']) - 1
                        if command_queue[key]['countdown'] <= 0:
                            main.printlog(
                                "SCHED: Giving up on [%s]" % friendly_name.get(value['entity_id'], value['entity_id']))
                            command_queue.pop(key)
                    else:
                        main.printlog("SCHED: [%s] is %s as requested!" % (
                            friendly_name.get(value['entity_id'], value['entity_id']), entity_status.upper()))
                        command_queue.pop(key)

            if options['debug']: main.printlog("DEBUG: Finished Queue management - Queue length: %d" % len(command_queue))

        sleep(1)
