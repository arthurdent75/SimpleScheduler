**Version 3.2.2**
- Fixes "Unable to scroll on large lists" (#205)
- Fixes "Entity dropdown does not show all the entities, unless you use the filter" (#201)
- Changing the name retireval logic to avoid "Unable to obtain entities names" (#206)
- Removing armv7 support as Home Assistant deprecate it

**Version 3.2.1**
- Fixes "Restarting MQTT thread..." (#199)

**Version 3.2**
- Fixes crashes in scheduler on timeout (#193)
- Add support for drag on mobile (#192)
- Drag only by handle icon
- Added support for double click on mobile
- Optimized scheduler routine
- Fixes Scheduler thread crashes when using unsupported times separator (#198)
- Manage wrong id filename

**Version 3.1**
- New feature: "excluded entities" in config (#149)
- New feature: added group recap when closed (#187)
- New feature: autoswitch to dark theme (#190)
- Resizable sidebar
- Improved error log
- Many bugfixes in frontend (including: #188,#189)

**Version 3.0**
- New feature: arrange scheduler in group
- New feature: call script with parameters
- New feature: add support for INPUT_BUTTON
- Update addon base image with multi-architecture support
- Faster download: reduced image size by 85%
- Threading architecture
- Update paho-mqtt version
- No need to restart add-on to enable/disable MQTT
- A lot of bugfix

**Version 2.6**
- New feature: add support for BUTTON
- New feature: double click on row to enable/disable scheduler (#165)
- New feature: notification on failure (#134)
- Improvement: entity dropboxes are now searchable 
- Improvement: Reduced backup size (#139,#137,#85)
- Fix "returned a non-zero code" during install on some devices (#158)
- Fix "Crash on dot instead of colon" (#177)
- Fix vacuum start and stop

**Version 2.5**
- New feature: add template conditions
- New feature: support valve (#146) 
- Fix crash due to new mqtt library (#151)
- Improved documentation (including #152)
- Fix few bugs in frontend

**Version 2.2.1**
- Fix "Simple Scheduler no longer switching on lamps with brightness" (#142)

**Version 2.2**
- New feature: add parameters for RGB/CT lights (#138)
- New feature: support humidifiers (#135) 

**Version 2.11**
- Fix "Allow non admin users to view panel" (#74)
 
**Version 2.1**
- Fix "Corrupted JSON files crash the addon" (#123)
- Fix "Setting hours to 24 crash the addon" (#124) 

**Version 2.0.50 (beta)**
- Fix MQTT Switches unavailable on restart (#111)
- Fix error if entity is null (#110) 

**Version 2.0.48 (beta)**
- create json folder if missing
- enable flask logs

**Version 2.0 (beta)**
- Rewritten from scratch in Python
- Complete reengineering of the docker structure
- New feature: Configuration moved to frontend (you need to set option again!)
- New feature: Recurring type scheduler (from - to - every)
- New feature: Added "Do not retry" flag
- New feature: Added "Clone" button
- New MQTT Engine
- Auto respawn processes (frontend and scheduler) in case of crash
- Full UTF-8 support in scheduler name (include regional, mathematical, symbols and emoji)
- Log moved to frontend
- Log improvement (more clear and more detalied)
- Improvement of "Max Retry" option behavior
- Avoid queuing of some domains (script, scene, ecc)
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
