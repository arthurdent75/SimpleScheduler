**Version 2.0 (beta)**
- Rewritten from scratch in Python
- New feature: Recurring type scheduler (from - to - every)
- New MQTT Engine
- Log improvement
- Massive bugfix

**Version 0.64**
- Improvement: Set absolute value for light (#76)
- Improvement: MQTT Switches become unavailable if addon is not running
- Fix MQTT Switches duplicate with an ending 2 (#80)

**Version 0.62**
- Timezone issue (#75)
- Added some fixes to allow installation on not-supervised env (thanks to @micw)

**Version 0.61**
- Allow non admin users to view panel (#74)
- Fix "Missing translations" (#69)

**Version 0.60**
- Switch Docker image to HA Debian base
- Complete reengineering of the docker structure
- Fix "returned a non-zero code" issue in supervised installation (#65)
- Added support for VACUUM

**Version 0.50**
- New feature: Retry unavailable entities
- New feature: enable/disable schedulers in frontend (through MQTT)
- Improvement: Set fan percent speed
- Fixed bug in sorting (#61)
- Log improvement
- Several bugfixes

**Version 0.40**
- New feature: week-based scheduler
- Improvement: added dark theme
- Improvement: added Fan
- Updated UI
- Several bugfixes

**Version 0.35**
- Fix Temperature Only on multiple climate issue (#53)

**Version 0.34**
- Improvement: Change climate temperature without turning it on (#51)
- Update material icons to latest version 

**Version 0.33**
- Improvement: manage commas as separator in time list (#46)
- Improvement: Added Cover (with position) (#49)

**Version 0.32**
- Fix "too many time" visualization issue (#48)

**Version 0.31**
- Fix single quote issue (#44)
- Javascript optimization

**Version 0.30**
- Can set brightness to Lights
- Can set temperature in Climates
- Can add positive/negative offset to sunset/sunrise
- Embed style and script to avoid cache issues
- Bugfix

**Version 0.22**
- Fixed a bug in scheduler

**Version 0.21**
- Fixed visualization of UTF-8 chars (issue #11)

**Version 0.20**
- Add Name to scheduling
- Can add more entities in one scheduler
- Can add multiple time in one scheduler
- Can drag rows to sort them
- Changed edit from row to sidebar
- Little graphic rewiew
- Code improvements

**Version 0.16**
- Fix option.json issue
- Removed table sorting

**Version 0.15**
- Fix Timezone Issue

**Version 0.14**
- Fix the “permission denied” issue
- Sortable Columns
- Added status bar with scheduler engine status
- Added “debug option” to see all the error messages
- various bugfixes/improvements
