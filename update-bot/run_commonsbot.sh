#!/bin/sh
# This script is a shortcut for running the commons bot on tools labs with all the parameters

/data/project/wlm-de-utils/env/bin/python -m wlmbots.commons_bot -v

# The following line could be used to run commons bot with an update freqency of 8 hours
# /data/project/wlm-de-utils/env/bin/python -m wlmbots.commons_bot -v -sleep-seconds:28800
# Every six hours would be 21600, every 4 hours 14400, every 3 hours 10800
# All intervals are calculated from the time the bot starts
