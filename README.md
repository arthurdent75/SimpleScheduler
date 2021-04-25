# SimpleScheduler
A Home Assistant AddOn to schedule switches and lights on a weekly base in a visual way without coding.
You can keep all the schedules in one place and add/change in a few clicks, even in your mobile app.

![SimpleScheduler](https://raw.githubusercontent.com/arthurdent75/SimpleScheduler/master/logo.png)


### Installation
You can add the URL of this page in your "add-on store" as a new repository.
(Supervisor > Add-on store > three dots in top right corner > Repository)
Click refresh and you will find the add-on "Simple Scheduler" listed.

### How to use it
The add-on is very easy and intuitive (or, at least, that's what I hope)
Once installed, open the GUI or click on the sidebar (if you choose to add to it)
Just click on the round plus button in the bottom right and add your first schedule.
Choose one or more entity from the dropdown, fill the ON time (in 24 hours format, as suggested) and select the weekdays. Do the same for the OFF time and click "save".
That's it!
You can also set multiple time in the same scheduler. Just write them in the field separated by spaces. Also, you can use the words "sunrise" and "sunset".
It's not mandatory to add both ON and OFF time. You can leave one of them empty if you don't need it.
For example, you want to turn off a light every day at 22:00, but you don't need to turn it on.
You can then edit any of the schedules with the icon at the end of the row.
You can also choose to delete it or disable it (the schedule will stay there, but it will not be executed until you enable it back)

### Translation
The default text language is English. They are very few words.
If you want to translate them, you just need to take a look at the configuration section of the addon.
Rewrite the words you would like to have in your language and restart the addon.
For the weekdays, as you can easily understand, only the first two chars are used.

### Two words about the stored data
Every schedule (or row, if you prefer) is a JSON file stored in the [share/simplescheduler] folder under the SAMBA share.
This gives the chance to the data to "survive" to an addon upgrade or reinstallation.
You can easily backup and restore them in case of failure. In the same way, you can (accidentally?) delete them. So be aware of that.

### Last but not least
If you want to convince me to stay up at night to work on this, just <a target="_blank" href="https://www.buymeacoffee.com/arthurdent75">buy me a beer 🍺</a>
You may say that regular people need coffee to do that. Well, I'm not a regular person.

###  - - - - - F A Q - - - - - F A Q - - - - - F A Q - - - - - F A Q - - - - - F A Q - - - - - F A Q - - - - - 

**I set a timer but it switchs on/off at a wrong time** \
*Be sure to set the correct timezone in Settings->General* \
*You can read the TimeZone currently used by the addon in the bottom gray row* \

**I set a timer but it doesn't switch on/off**\
*The time MUST be set in HH:MM format*\
*Be sure to input time with leading zeros (e.g:  08:30)*\
*Seconds are not allowed*\
*Also check the previous point (timezone). Maybe it works but at the wrong time!*\

**After update the addon doesn't seem to work**\
*It seems that sometimes the update process fails.*\
*Try to uninstall the addon and install it again.*\
