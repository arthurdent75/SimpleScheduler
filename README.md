# SimpleScheduler 4

A Home Assistant add-on to schedule switches, lights and other entities on a weekly basis, in a visual way and without coding.\
You keep all the schedules in one place and add or change them in a few clicks, even from the mobile app.

<img width="974" height="895" alt="image" src="https://github.com/user-attachments/assets/df05c07d-a485-4623-b07f-ab9044c706ce" />

<img width="1684" height="933" alt="image" src="https://github.com/user-attachments/assets/f88ac52c-4476-4ba7-a1a5-a74d39da3c58" />

<img width="689" height="639" alt="image" src="https://github.com/user-attachments/assets/28f13622-334b-4035-ac4d-e833154f780b" />

<img width="468" height="400" alt="image" src="https://github.com/user-attachments/assets/130df8d3-b846-4598-a104-835945f8f184" />


### Demo
[Here](https://htmlpreview.github.io/?https://github.com/arthurdent75/SimpleScheduler/blob/master/demo/index.html) you can find a working simulation with the most common scenarios


### Installation
Add the repository and then the add-on by clicking on the badges:\
[<img src="https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg">](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Farthurdent75%2FSimpleScheduler) \
[<img src="https://my.home-assistant.io/badges/supervisor_addon.svg">](https://my.home-assistant.io/redirect/supervisor_addon/?addon=00185a40_simplescheduler) \
If something goes wrong, you can add the repository by hand:\
*Settings > Add-ons > ADD-ON STORE (bottom right) > three dots (top right) > Repositories*\
Click *Check for updates* and you will find "Simple Scheduler" in the list.

The add-on needs a supervised installation (Home Assistant OS or Supervised): it talks to Home Assistant through the Supervisor.

### Type of scheduler
When you create a scheduler you choose its type. The type can't be changed later.
- **Daily**: the same events on the weekdays you choose. Each event can have its own days.
- **Weekly**: every day of the week has its own list of events. You can copy a day to Mon–Fri, to the weekend or to all days.
- **Recurring**: repeat an action at a fixed interval between two times (FROM hh:mm TO hh:mm EVERY n minutes). The action can be *on*, *off*, *pulse* (turn on and then off after a number of minutes) or *random pulse* (turn on and then off after a random time between a minimum and a maximum, see Random time). A pulse must turn off before midnight: a rule whose last *on* could turn off on the next day is refused.

### How to use it
Open the add-on panel and click **New scheduler**. Choose the type, give it a name, pick one or more entities and add the events.\
Every event has an action (on/off), a time and the weekdays. The timeline shows the events of the day, with sunrise, sunset and the current time.\
Click **Save**. That's it!

In the list:
- the switch on each row enables or disables the scheduler: a disabled scheduler stays there, but it is not executed until you enable it again;
- the eye icon shows or hides the details of a scheduler;
- double-click a row (or the pencil) to edit it;
- **drag the rows** from the handle to sort them as you like.

### Supported entities
| **Entity** | **ON action** | **OFF action** | **Extra features** |
|:---|:---:|:---:|:-----|
| light | ON | OFF | **Brightness (%)**<br>*e.g: set brightness to 30%* <br><br> **Brightness (absolute)**<br>*e.g: set absolute brightness to 200*<br> <br> **Color (hex)**<br>*e.g: set brightness to 75% and color to orange*<br><br> **Color temp. (&deg;K)**<br>*e.g: set brightness to 20% and color temperature to 4700&deg;K* <br> |
| cover | OPEN | CLOSE | **Percent (%)**<br>*e.g: open cover to 50%*  |
| fan | ON | OFF | **Percent (%)**<br>*e.g: Turn on fan at 25%*  |
| valve | OPEN | CLOSE | **Position (%)**<br>*e.g: Open valve at 50%*  |
| climate | ON | OFF | **Temperature**<br>*e.g: turn on the climate and set temperature to 22.5&deg;* <br><br> **Temperature Only**<br>*e.g: just set temperature to 20.7&deg;* <br><br> **Mode**<br>*e.g: cool, heat, dry, fan, etc.*  |
| humidifier | ON | OFF | **Humidity (&deg;)**<br>*e.g: turn on the (de)humidifier and set the humidity to 55%*  |
| switch | ON | OFF |  |
| button | PRESS | - |  |
| input_button | PRESS | - |  |
| vacuum | START | HOME |  |
| media_player | ON | OFF |  |
| script | RUN | STOP |  **Parameters**<br>*send parameters (JSON) to the script*  |
| scene | ON | - |  |
| camera | ON | OFF |  |
| automation | ENABLE | DISABLE |  |
| input_boolean | ON | OFF |  |

### Editing as text
The **As text** card shows the events as text (*Preview*), and you can edit them by hand (*Manual edit* > *Apply text*).\
One event per line: action, time, weekdays (1 = Mon … 7 = Sun), then the optional settings:
```
on 07:30 12345 B30
off sunset-30 1234567
on 18:00 67 C#FF9900
on 06:00 12345 T21.5 if:false
on 14:00 67 Mcool T24
on 16:30 1234567 B70 force
on sunset-15 1234567 B60 R30
```
Settings: `B30` brightness %, `BA200` absolute brightness, `C#FF9900` color, `K4700` color temperature, `P50` position, `F25` fan speed, `Mcool` climate mode (`heat`, `cool`, `heat_cool`, `auto`, `dry`, `fan_only`), `T21.5` temperature, `TO21.5` temperature only, `H55` humidity, `J{...}` script variables (always last), `R30` random time (see Random time), `if:false` (see Conditions), `force` (see Force the state).\
A recurring scheduler is a single line: `every 60 from 06:00 to 20:00 pulse 10 days 135` (`pulse 10-40` for a random time on, from 10 to 40 minutes).\
This is useful if you want to change only one event in a sequence or copy (all or just a part of)  the events to another scheduler.

### Conditions
Every scheduler can have a condition, a template checked at the time of each event.
If the field is empty, the events always run.\
Each event runs when the condition is true (the usual case) or, if you choose so, when it is false: this way you can have different times depending on the condition.\
The template **must render True or False**, so convert the states to booleans. A few examples:
```
{{ states('switch.my_switch') | bool }}
{{ not states('light.my_light') | bool }}
{{ states('binary_sensor.workday') | bool }}
{{ states('sensor.room_temperature') | float > 23.5 }}
{{ is_state('person.my_kid', 'not_home') }}
```
A template with an error is treated as false and the error is written in the log.\
Use the **Test condition** button in the editor to check it before saving.

### Force the state
An event can **force its state until the next event** of the same scheduler: tick *Force this state until the next event* when you add it (a lock icon marks it).\
Every minute SimpleScheduler checks the entities and, if one is not in the requested state, sends the action again with its extra settings.\
For example: the scheduler turns on a light at 16:30 (forced) and turns it off at 18:00 (not forced). If you turn the light off at 17:04, it is turned on again within a minute. If you turn it on at 20:00, it stays on.
- The forced period ends at the next event in the calendar, even on the next day and even if that event doesn't run because of the condition.
- If the scheduler has a condition, it is checked every minute: when it no longer matches, the event is not forced any more until the next event.
- Only on/off (open/closed, or the mode of a climate) is checked: you can still change the brightness or the temperature by hand.
- After 5 attempts on the same entity in the same period SimpleScheduler gives up, writes it in the log and sends a notification (if set in the options). This stops endless fights with another automation, or with an entity that doesn't respond.
- If two schedulers force different states on the same entity, the most recent event wins, and the log says so.
- Disabling the scheduler (also from its MQTT switch) suspends the forcing.
- It works with lights, switches, input_booleans, fans, covers, valves, climates, humidifiers, media players and automations. A forced event doesn't use the retries: the check every minute does the same job.
- In a recurring scheduler the option applies to the events of its action (the *on* events for *on*, *pulse* and *random pulse*, the *off* events for *off*).

### Random time
An event can run at a **different minute every day**, to make a house look lived-in when you are away: turn on *Random time* in the event and choose the window with the bar (the tick in the middle marks the time of the event, the band grows on both sides).\
For example, *on at sunset−15 ±30* turns on the lights at any minute from 45 minutes before sunset to 15 minutes after it.
- It works with fixed times, sunrise and sunset, for on and off events, from ±5 to ±120 minutes (in the text editor any value from `R1` to `R120`).
- The minute is drawn again every day. It doesn't change if you save the scheduler or Home Assistant reconnects during the day, so the event never runs twice or gets lost.
- The window can't reach the time (or the window) of the event before or after it on the same day, so the on and off events never swap: the editor tells you which events overlap. For sunrise and sunset the check uses today's times; if they move during the year so much that two windows touch, the random event still never runs before the event that comes before it.
- The window is cut at midnight: an event never moves to another day.
- The timelines show the window as a hatched area, the badges and the labels show `±minutes`.
- In a recurring scheduler, choose **Turn on, then off at random** and set the shortest and the longest time on with the two handles (from 1 minute to *every* − 1): every time it turns on, it stays on for a different time, and the times change every day. The *on* events keep their fixed times. The window of each *off* doesn't have to be symmetric: it is shown as `−15/+16` (minutes before and after the time in the middle).

A condition such as `{{ is_state('input_boolean.vacation', 'on') }}` lets you run the random events only when you are away.

### Groups
Click **New group** to create a group, then drag the schedulers into it. A group can be collapsed, renamed and enabled or disabled as a whole (the switch acts on every scheduler in it). Deleting a group keeps its schedulers.

### Switches in Home Assistant (MQTT)
If you want to enable and disable the schedulers from the Home Assistant frontend or from automations, turn on **Switches in Home Assistant** in the options: every scheduler gets a switch through MQTT discovery. Turning a switch off disables the scheduler, and the web page shows the change at once.\
It needs an MQTT broker and the MQTT integration in Home Assistant.
The broker is found automatically through the Supervisor (for example the Mosquitto broker add-on). To use a different one, set `mqtt_host`, `mqtt_port`, `mqtt_username` and `mqtt_password` in the add-on configuration. The settings are read every time MQTT starts: turn the option off and on to apply a change.\
The switches keep the same entity_id they had in version 3.

### Calendar view
Open it with the calendar icon at the top of the page. It shows the events of all schedulers in a typical week, Monday to Sunday, like the week view of a calendar app. 
It opens with the whole day on the screen: zoom in by dragging the hour column, with Ctrl + mouse wheel or with a pinch on a phone.


### Options
Open them with the options icon at the top of the page.
- **Retries when an entity doesn't respond**: after an action, SimpleScheduler checks the entity after 5 seconds and then every minute, sending the action again if needed (0 to 5 times, default 3). A cover or valve that is still opening or closing is not counted as wrong: it is checked again when it stops (for up to 5 minutes). Each scheduler can turn the retries off. Scenes, scripts, automations, buttons, cameras and media players are never retried.
- **Notify on error**: a notify service to call when an action fails.
- **Always show details**: show the details of every scheduler in the list.
- **Switches in Home Assistant**: see above.
- **Theme**: automatic, light or dark (see below).
- **Debug mode**: writes detailed lines to the log. Turn it off when you're done.
- **Hidden entities**: entities you never want in the list, one pattern per line, with `*` as a wildcard (for example `switch.*_led`).

### Home Assistant offline
If Home Assistant is not reachable when an event is due, the event waits and runs as soon as the connection comes back (the log says how late it ran).

### Real-time interface
The page receives every change as it happens (Server-Sent Events): a switch turned in Home Assistant, a change made in another browser, the connection to Home Assistant going up or down.

### Theme
Choose the theme in the options: **Automatic** (the default) follows the light or dark theme of your device, **Light** and **Dark** always use that theme.\
If you used the dark theme in version 3, the import sets it to Dark.

### Two words about the stored data
Every scheduler is a JSON file in the `schedulers` folder of the add-on configuration (`addon_configs/<slug>_simplescheduler` in the Samba share). The same folder holds the layout (order and groups), the options, today's sun times and the log.
This way the data survives an add-on upgrade or reinstallation, and you can back it up and restore it. In the same way, you can (accidentally?) delete it, so be aware of that.\
Scheduler files edited by hand are noticed within a minute.

### Log
Open it with the log icon at the top of the page: you can filter warnings and errors, search it and clear it. The file is `simplescheduler.log` in the same folder as the data; it rotates at 2 MB.

### Last but not least
Did SimpleScheduler save you hours of work and make your life with Home Assistant easier? If so, consider <a target="_blank" href="https://www.paypal.com/donate/?hosted_button_id=8FN58C8SM9LLW"> buying me a beer 🍺</a><br/>It's not about the money, it's about the kindness ❤️
