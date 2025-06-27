# SimpleScheduler

A Home Assistant add-on to schedule switches, lights, and other entities on a weekly base in a visual way without coding.\
You can keep all the schedules in one place and add/change them in a few clicks, even on your mobile app.

![SimpleScheduler](https://raw.githubusercontent.com/arthurdent75/SimpleScheduler/master/asset/logo.png)

### Installation
Add the repository and then the addon by clicking on the badges:\
[<img src="https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg">](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Farthurdent75%2FSimpleScheduler) \
[<img src="https://my.home-assistant.io/badges/supervisor_addon.svg">](https://my.home-assistant.io/redirect/supervisor_addon/?addon=00185a40_simplescheduler) \
If something goes wrong, you can install it manually.\
You can add the URL of this page to your "add-on store" as a new repository:\
*Settings > Add-ons > ADD-ON STORE button in bottom right corner >  three dots in top right corner > Repositories*\
Click *Check for updates* and you will find the add-on "Simple Scheduler" listed.

If you are not using a supervised installation, you can run the addon as a standalone Docker.
Take a look here: [docker_install.MD](https://github.com/arthurdent75/SimpleScheduler/blob/master/asset/docker_install.MD "docker_install.MD")

### Type of scheduler

There are three kinds of schedulers:
- **Daily**: you can set an ON/OFF time (or a list of them) and then you choose on which weekdays you want to enable them.
- **Weekly**: you can set a different ON/OFF time (or list of them) for every single day of the week.
- **Recurring**: you can set a recurring ON/OFF (FROM hh:mm TO hh:mm EVERY n MINUTES) and choose on which weekdays you want to enable them.

### How to use it
The add-on is very easy and intuitive (or, at least, that's the goal)\
Once installed, open the GUI, click on the round plus button in the top left, and choose your schedule type.\
Choose one or more entities from the dropdown, fill in the ON time (in 24-hour format with leading zero, as suggested), and select the weekdays. Do the same for the OFF time and click "save".

- You can set **multiple times** in the same scheduler: just enter them in the ON/OFF field **separated by spaces**.  
- It's not mandatory to add both ON and OFF times. You can leave one of them empty if you don't need it. For example, you want to turn off a light every day at 22:00, but you don't need to turn it on.
- You can use the words **sunrise** and **sunset** instead of *hh:mm*; if needed, you can add an offset (in minutes). Sunset and Sunrise times are recalculated every day at midnight and are reported in the status bar. Some examples: **sunrise+30** is executed 30 minutes after sunrise; **sunset-60** is executed 1 hour before sunset.
- You can **drag the rows to sort them**, so you can keep them organized as you like!
- You can also choose to **disable a schedule**: the schedule will stay there, but it will not be executed until you enable it back. You can double-click on a row to quickly enable/disable the scheduler.
- You can **organize schedulers in groups**, that can be expanded and collapsed as you like. You can open, close, drag, disable, rename, and delete them. Add a schedule to a group by dragging it over and remove it by dragging it out. If you delete a group, the schedulers inside the group will not be deleted.

## Features

| **Entity** | **ON action** | **OFF action** | **Extra features**** |
|:---|:---:|:---:|:-----|
| light | ON | OFF | **Brightness (%)**<br>*e.g: set brightness to 30%* <br>`hh:mm>B30`<br><br> **Brightness (absolute)**<br>*e.g: set absolute brightness to 200*<br> `hh:mm>BA200`<br> <br> **Color (hex)**<br>*e.g: set brightness to 75% and color to orange*<br> `hh:mm>B75\|FFA500`<br><br> **Color temp. (&deg;K)**<br>*e.g: set brightness to 20% and color temperature to 4700&deg;K* <br> `hh:mm>B20\|K4700` <br> |
| cover | OPEN | CLOSE | **Percent (%)**<br>*e.g: open cover to 50%* <br>`hh:mm>P50` |
| fan | ON | OFF | **Percent (%)**<br>*e.g: Turn on fan at 25%* <br>`hh:mm>F25` |
| valve | OPEN | CLOSE | **Position (%)**<br>*e.g: Open valve at 50%* <br>`hh:mm>P50` |
| climate | ON | OFF | **Temperature**<br>*e.g: turn on the climate and set temperature to 22.5&deg;* <br>`hh:mm>T22.5`<br><br> **Temperature Only**<br>*e.g: just set temperature to 20.7&deg;* <br>`hh:mm>TO20.7` |
| humidifier | ON | OFF | **Humidity (&deg;)**<br>*e.g: turn on the (de)humidifier and set the humidity to 55%* <br>`hh:mm>H55` |
| switch | ON | OFF |  |
| button | PRESS | - |  |
| input_button | PRESS | - |  |
| vacuum | START | HOME |  |
| media_player | ON | OFF |  |
| script | RUN | STOP |  **Parameters**<br>*send parameters (JSON) to the script* <br>`hh:mm>J{"field 1":"value 1",...,"field n":"value n",}` |
| scene | ON | - |  |
| camera | ON | OFF |  |
| automation | ENABLE | DISABLE |  |
| input_boolean | ON | OFF |  |


***Extra features (obviously) work only in the "TURN ON" section !*

### Conditions
For each scheduler, you can add a condition that will be checked.
If the condition is 'true' the action will be performed and (obviously) it won't be executed if the condition is 'false'.
The condition is a template expression you can add to the "template" field.
If the field is empty, no check will be performed and the action will always be executed. \
The template expression **must return a boolean** ('True' or 'False'). Be sure to "convert" switches, lights, and any other entity states to boolean. \
It is strongly advised to set a default with `replace("unavailable", "true")` or `replace("unavailable", "false")` to avoid errors in case the entity becomes unavailable. \
A few examples:
``` 
{{  states('switch.my_switch') | replace('unavailable', 'false') | bool }}
{{  not states('light.my_light') | replace('unavailable', 'false') | bool }}
{{  states('sensor.room_temperature') | replace('unavailable', '22') | float > 23.5   }}
{{  is_state('person.my_kid', 'not_home') | replace('unavailable', 'true') | bool  }}
{{  states('sensor.room_temperature') | replace('unavailable', '22') | float > 23.5
      and is_state('sun.sun', 'above_horizon') | replace('unavailable', 'true') | bool  }}
``` 
If the template returns '*on*', '*open*', '*home*', '*armed*', '*1*', and so on,  it will all be treated as 'False'. \
If the template expression has syntax errors it will be considered 'false', and it will be reported in the addon log.\
Use the template render utility in Developer Tools to test the condition before putting it into the scheduler.

### Failure notification 
If a schedule is not able to execute the action, it can send you a notification, using one of the notifiers available in your setup. You can activate it in the addon configuration by selecting a notifier from the **notify on error** dropdown, otherwise you must select the entry "*disabled*". Choose the native notifier "*persistent_notification*" to receive the  message in the frontend. 
This addon does not allow the addition or configuration of a notifier. This operation must be performed in Home Assistant. More info here: https://www.home-assistant.io/integrations/notify/

### Frontend switch to enable/disable (with MQTT)
If you want to enable/disable schedulers in the front end and/or automation, you can achieve that through MQTT.
This feature is disabled by default because it requires a working MQTT server (broker) and Home Assistant MQTT integration.
Take a look at the [MQTT.MD](https://github.com/arthurdent75/SimpleScheduler/blob/master/asset/MQTT.MD "MQTT.MD") file to know more. 

### Retry on unavailable
By default, SimpleScheduler will retry 3 times if an entity is unavailable. The first retry attempt happens after 5 seconds, then every minute. You can change the number of retries in the addon options. The valid range is 0 to 5.

### Hidden scheduler details
When you have a lot of schedulers the view can become messy. As a default, all the scheduler details are hidden, so you can have a clear look. 
You can toggle the visibility with the *eye* icon near the scheduler name. 
If you prefer to have the entire schedule always visible, you can easily achieve that by enabling **details_uncovered** in the addon configuration

### Dark theme 
The addon switches to dark theme accordingly to your setup

### Translation
The default text language is English. There are very few words.
If you want to translate them, you just need to take a look at the configuration section of the addon.
Rewrite the words you would like to use in your language and restart the add-on.
For the weekdays, as you can easily understand, only the first two characters are used.

### Two words about the stored data
Every schedule (or row, if you prefer) is a JSON file stored in the `/share/simplescheduler` folder under the SAMBA share.
This way the data can "survive" an addon upgrade or reinstallation.
You can easily backup and restore them in case of failure. In the same way, you can (accidentally?) delete them. So be aware of that.

### Log 
The log file is stored in the same folder where the JSON files are stored `/share/simplescheduler`
You can delete it if it becomes too large, but be sure to stop the addon first.
You can enable a verbose log by checking the box **debug mode** in the addon configuration.
When enabled, the log file can easily become very large, so be sure to keep the debug mode on only the required time.

### Last but not least
If you want to convince me to stay up at night to work on this, just <a target="_blank" href="https://www.paypal.com/donate/?hosted_button_id=8FN58C8SM9LLW">buy me a beer 🍺</a> \
You may say that regular people need coffee to do that. Well, I'm not a regular person.
