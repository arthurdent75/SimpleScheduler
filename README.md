
# SimpleScheduler

A Home Assistant AddOn to schedule switches, lights and other entities on a weekly base in a visual way without coding.\
You can keep all the schedules in one place and add/change them in a few clicks, even in your mobile app.

![SimpleScheduler](https://raw.githubusercontent.com/arthurdent75/SimpleScheduler/master/asset/logo.png)

### Installation
Add the repository and then the addon by clicking on the badges:\
[<img src="https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg">](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Farthurdent75%2FSimpleScheduler) \
[<img src="https://my.home-assistant.io/badges/supervisor_addon.svg">](https://my.home-assistant.io/redirect/supervisor_addon/?addon=00185a40_simplescheduler) \
If something goes wrong, you can install it manually.\
You can add the URL of this page in your "add-on store" as a new repository:\
*Settings > Add-ons > ADD-ON STORE button in bottom right corner >  three dots in top right corner > Repositories*\
Click *Check for updates* and you will find the add-on "Simple Scheduler" listed.

If you are not using a supervised installation, you can run the addon as a standalone docker.
Take a look here: [docker_install.MD](https://github.com/arthurdent75/SimpleScheduler/blob/master/asset/docker_install.MD "docker_install.MD")

### Type of scheduler

There are three kinds of schedulers:
- **Daily**: you can set an ON/OFF time (or a list of them) and then you choose on which weekdays you want to enable them.
- **Weekly**: you can set a different ON/OFF time (or list of them) for every single day of the week.
- **Recurring**: you can set a recurring ON/OFF (FROM hh:mm TO hh:mm EVERY n MINUTES) and choose on which weekdays you want to enable them.

"*A picture is worth a thousand words*", so if you take a look at the screenshot it will be even more clear.

### How to use it
The add-on is very easy and intuitive (or, at least, that's what I hope)\
Once installed, open the GUI, click on the plus button in the top left and choose your schedule type.\
Choose one or more entities from the dropdown, fill in the ON time (in 24-hour format with leading zero, as suggested) and select the weekdays. Do the same for the OFF time and click "save".
That's it!

### Advanced Features 
If you need more advanced features:
- You can set multiple times in the same scheduler: just write them in the field separated by spaces.  
- You can use the words **sunrise** and **sunset** and also add an offset (in minutes) to it if you need (e.g: **sunrise+30** or **sunset-60** )
- You can set the percent brightness of a light. Write **16:30>B30** to turn on the light at 30% 
- You can set the absolute brightness of a light. Write **16:30>BA30** to turn on the light at 30
- You can set the color of a RGB light. Write **16:30>B30|FF0077** to turn on the light at 30% and set the color to FF0077 (6 digits HEX)
- You can set the temperature of a CCT light. Write **16:30>B30|K4700** to turn on the light at 30% and set it to 4700°K
- You can set the temperature of a climate. Write **16:30>T22.5** to turn on the climate and set the temperature to 22.5° 
- You can set the temperature of a climate without turning it on. Write **16:30>TO22.5** to set the temperature to 22.5°
- You can set the humidity of a (de)humidifier. Write **16:30>H65** to set the humidity to 65% 
- You can set the position of a cover. Write **16:30>P25** to set the cover at 25%  
- You can set the fan speed. Write **16:30>F25** to turn on the fan at 25%
- You can set the valve position. Write **16:30>P25** to set the valve position at 25%  
- Brightness/Temperature/Position/Speed only works in the "TURN ON" section (obviously)! 
- It's not mandatory to add both ON and OFF time. You can leave one of them empty if you don't need it. For example, you want to turn off a light every day at 22:00, but you don't need to turn it on.
- You can also choose to disable a schedule: the schedule will stay there, but it will not be executed until you will enable it back
- Double click on a row to enable/disable the scheduler
- You can **drag the rows to sort them**, so you can keep them organized as you like!

Look at the picture above to see all these things in action (and combined!).

### Conditions
For each scheduler, you can add a condition that will be **checked at the time of the execution**.
If the condition is 'true' the action will be performed and (obviously) it won't be executed if the condition is 'false'.
The condition is a template expression that you can add in the "template" field. \
The condition is evaluated at every triggering time written in the scheduler before the execution. \
If the field is empty, no check will be performed and the action will always be executed. \
If you fill the field, two additional time fields will apper. This allows you to set on/off times when condition result is true and different on/off times when condition result is false. \
The template expression **must return a boolean** ('True' or 'False'). \
So be sure to "convert" switches, lights, and any other entity states to boolean. A few examples:
``` 
{{  states('switch.my_switch') | bool }}
{{  not states('light.my_light') | bool }}
{{  states('binary_sensor.workday) | bool }}
{{  states('sensor.room_temperature') | float > 23.5   }}
{{  is_state('person.my_kid', 'not_home')  }}
{{  states('sensor.room_temperature') | float > 23.5 and is_state('sun.sun', 'above_horizon')  }}
``` 
If the template returns 'on', 'open', 'home', 'armed', '1' and so on,  they all will all be treated as 'False'. \
If the template expression has syntax errors it will be considered 'false', and it will be reported in the addon log.\
Use the template editor utility in Developer Tools to test the condition before putting it into the scheduler.

### Frontend switch to enable/disable (with MQTT)
If you want to enable/disable schedulers in frontend and/or automation, you can achieve that through MQTT.
This feature is disabled by default because it requires a working MQTT server (broker) and Home Assistant MQTT integration.
Take a look at the [MQTT.MD](https://github.com/arthurdent75/SimpleScheduler/blob/master/asset/MQTT.MD "MQTT.MD") file to know more. 

### Retry on unavailable
By default, SimpleScheduler will retry 3 times if an entity is unavailable. The first retry attempt happens after 5 seconds, then every minute. You can change the number of retries in the addon options. The valid range is 0 to 5.

### Hidden scheduler details
When you have a lot of schedulers the view can become messy. As a default, all the scheduler details are hidden, so you can have a clear look. 
You can toggle the visibility with the *eye* icon near the scheduler name. 
If you prefer to have the entire schedule always visible, you can easily achieve that by enabling **details_uncovered** in the addon configuration

### Dark theme 
If you prefer a dark theme, you can activate it in the addon configuration by checking the option **dark_theme**

### Failure notification 
If a schedule was not able to execute the action, it can send you a notification, using one of the notifier available in your setup. You can activate it in the addon configuration by selecting a notifier from the **notify on error** dropdown, otherwise you must select the entry "*disabled*". Choose the native notifier "*persistent_notification*" to receive the  message in frontend. 
This addon does not allow the addition or configuration of a notifier. This operation must be performed in Home Assistant. More info here: https://www.home-assistant.io/integrations/notify/

### Translation
The default text language is English. They are very few words.
If you want to translate them, you just need to take a look at the configuration section of the addon.
Rewrite the words you would like to have in your language and restart the addon.
For the weekdays, as you can easily understand, only the first two chars are used.

### Two words about the stored data
Every schedule (or row, if you prefer) is a JSON file stored in the [share/simplescheduler] folder under the SAMBA share.
This way the data can "survive" an addon upgrade or reinstallation.
You can easily backup and restore them in case of failure. In the same way, you can (accidentally?) delete them. So be aware of that.

### Log 
The log file is stored in the same folder where the JSON files are stored [share/simplescheduler] 
You can delete it if it become too large, but be sure to stop the addon first.
You can enable a verbose log by checking the box **debug mode** in the addon configuration.
When enabled, the log file can easily become very large, so be sure to keep the debug mode on only the required time.

### Last but not least
If you want to convince me to stay up at night to work on this, just <a target="_blank" href="https://www.paypal.com/donate/?hosted_button_id=8FN58C8SM9LLW">buy me a beer 🍺</a> \
You may say that regular people need coffee to do that. Well, I'm not a regular person.

