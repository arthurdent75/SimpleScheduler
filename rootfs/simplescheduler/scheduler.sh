#!/usr/bin/with-contenv bashio
# ==============================================================================
#  
# Home Assistant Add-on: SimpleScheduler
#  
# ==============================================================================

bashio::log.info "Running scheduler.sh"

python3 /simplescheduler/main.py
