# SimpleScheduler

A Home Assistant AddOn to schedule switches,lights and other entities on a weekly base in a visual way without coding.\
You can keep all the schedules in one place and add/change in a few clicks, even in your mobile app.

![SimpleScheduler](https://raw.githubusercontent.com/arthurdent75/SimpleScheduler/master/asset/logo.png)

### Installation
Add the repository and then the addon by clickin on the badges:\
[<img src="https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg">](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Farthurdent75%2FSimpleScheduler) \
[<img src="https://my.home-assistant.io/badges/supervisor_addon.svg">](https://my.home-assistant.io/redirect/supervisor_addon/?addon=00185a40_simplescheduler) \
If something goes wrong, you can install it manually.\
You can add the URL of this page in your "add-on store" as a new repository:\
*Settings > Add-ons > ADD-ON STORE button in bottom right corner >  three dots in top right corner > Repositories*\
Click *Check for updates* and you will find the add-on "Simple Scheduler" listed.

If you are not using a supervised installation, you can run the addon as a standalone docker.
Take a look here: [docker_install.MD](https://github.com/arthurdent75/SimpleScheduler/blob/master/asset/docker_install.MD "docker_install.MD")

### Type of scheduler

There are three kind of scheduler:
- **Daily**: you can set a ON/OFF time (or a list of them) and than you choose on which weekdays you want to enable them.
- **Weekly**: you can set a different ON/OFF time (or list of them) for every single day of the week.
- **Recurring**: you can set a recurring ON/OFF (FROM hh:mm TO hh:mm EVERY n MINUTES) and choose on which weekdays you want to enable them.

"*A picture is worth a thousand words*", so if you take a look at the screenshot it will be even more clear.

### How to use it
The add-on is very easy and intuitive (or, at least, that's what I hope)\
Once installed, open the GUI, click on the round plus button in the bottom right and choose your schedule type.\
Choose one or more entity from the dropdown, fill the ON time (in 24 hours format with leading zero, as suggested) and select the weekdays. Do the same for the OFF time and click "save".
That's it!

### Advanced Feature 
If you need more advanced feature:
- You can set multiple time in the same scheduler: just write them in the field separated by spaces.  
- You can use the words **sunrise** and **sunset** and also add an offset (in minutes) to it if you need (e.g: **sunrise+30** or **sunset-60** )
- You can set the percent brightness of a light. Write **16:30>B30** turn on the light at 30% 
- You can set the absolute brightness of a light. Write **16:30>BA30** turn on the light at 30
- You can set the temperature of a climate. Write **16:30>T22.5** to turn on the climate and set the temperature to 22.5° 
- You can set the temperature of a climate without turning it on. Write **16:30>TO22.5** to set the temperature to 22.5° 
- You can set the position of a cover. Write **16:30>P25** will set the cover at 25%  
- You can set the fan speed. Write **16:30>F25** will turn on the fan at 25%  
- Brightess/Temperature/Position/Speed only work in the "TURN ON" section (obviously)! 
- It's not mandatory to add both ON and OFF time. You can leave one of them empty if you don't need it. For example, you want to turn off a light every day at 22:00, but you don't need to turn it on.
- You can also choose to disable a schedule: the schedule will stay there, but it will not be executed until you will enable it back
- You can **drag the rows to sort them**, so you can keep them organized as you like!

Look at the picture above to see all this things in actions (and combined!).

### Frontend switch to enable/disable (with MQTT)
If you want to enable/disable schedulers in frontend and/or automation, you can achieve that through MQTT.
This feature is disabled by default, because it require a working MQTT server (broker) and Home Assistant MQTT integration.
Take a look at the [MQTT.MD](https://github.com/arthurdent75/SimpleScheduler/blob/master/asset/MQTT.MD "MQTT.MD") file to know more. 

### Retry on unavailable
By default, SimpleScheduler will retry 3 times if an entity is unavailable. The first retry attempt happens after 5 second, than every minutes. You can change the numbers of retries in the addon options.

### Hidden scheduler details
When you have a lot of schedulers the view can become messy. As a default, all the scheduler details are hidden, so you can have a clear look. 
You can toggle the visibility with the *eye* icon near the scheduler name. 
If you prefer to have all the schedule always visible, you can easily achive that by setting **details_uncovered: true** in the addon configuration

### Dark theme 
If you prefer a dark theme, you can activate it in the addon configuration by setting **dark_theme: true**

### Translation
The default text language is English. They are very few words.
If you want to translate them, you just need to take a look at the configuration section of the addon.
Rewrite the words you would like to have in your language and restart the addon.
For the weekdays, as you can easily understand, only the first two chars are used.

### Two words about the stored data
Every schedule (or row, if you prefer) is a JSON file stored in the [share/simplescheduler] folder under the SAMBA share.
This way the data can "survive" to an addon upgrade or reinstallation.
You can easily backup and restore them in case of failure. In the same way, you can (accidentally?) delete them. So be aware of that.

### Last but not least
If you want to convince me to stay up at night to work on this, just <a target="_blank" href="https://www.paypal.com/donate/?hosted_button_id=8FN58C8SM9LLW">buy me a beer 🍺</a> \
You may say that regular people needs coffee to do that. Well, I'm not a regular person.
