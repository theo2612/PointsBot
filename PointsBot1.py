###############################################################################
## POINTS BOT
##
## File: PointsBot.py
## Author: kaelin (tsumugles#3221)
###############################################################################

###############################################################################
## IMPORTS
##
## asyncio
##      used for async operations for bot actions (sending messages, etc.)
## 
## discord
##      the discord api........ for the discord bot. obviously. lol
##
## json
##      easy serialization of config data and additional data (such as points)
##      into a file so that it is non-volatile
###############################################################################
import asyncio
import discord
from discord.ext import commands

import json

###############################################################################
## GLOBALS
## bot - is what contains the discord bot object that can actually do stuff like
## listen for events, query for user data, send messages on channel
## config - is a dict that looks exactly like whats in the config.json
##
###############################################################################
bot = None
config = None
point_totals = {}

###############################################################################
## CONFIGURATION SAVE/LOAD
##
## I decided to wrap it in a function so that it could be potentially modularized
##  more easily in the future if the complexity of the bot grows. forward thinking!
##
## Added 7h30, Erod
################################################################################


CONFIG_FILE = "./config.json"

def load_config():
    global point_totals
    global bot
    global config
    
    config = None
    with open(CONFIG_FILE,"r") as f:
        config = json.load(f)
        
    point_totals = config["totals"]
    
    bot = commands.Bot( command_prefix = config["prefix"] )
    
def save_config():
    global point_totals
    global config
    print("saving config")
    
    config["totals"] = point_totals
    
    with open(CONFIG_FILE, "w") as f:
        json.dump( config, f, sort_keys=True )

load_config()
###############################################################################
## EVENTS 
###############################################################################
@bot.event
async def on_ready():
    print('Logged in as {0.user}'.format(bot))

###############################################################################
## COMMANDS
###############################################################################

USAGE_POINTS_CMD = """
```[Points]
Usages:
    - {0}points <user> <value> - modifies point count for <user> by <value>
    - {0}points <user> - displays point total for <user>
    - {0}points total - display list of point totals for all users```
"""

## CMD UTILITY FUNCTION: display_all_point_totals 
async def display_all_point_totals(contxt):
    """
    Displays point totals for all users
    """
    
    msg = "```Point Total (Overall):\n"
            
    if len(point_totals) < 1:
        msg += "No points have been awarded!"
    else:
        for member in point_totals:
            m = await bot.fetch_user(member)
            member_name = "{0.name}#{0.discriminator}".format(m)

            msg += "{:32s} {:d}\n".format(member_name, point_totals[member])
            
    msg += "```"
    
    await contxt.send( msg )
    
## CMD UTILITY FUNCTION: award_points
async def award_points(contxt, member_id, value):
    """
    Awards points to a specified user
    """
    
    if contxt.author.id not in config["authorized"]:
        return
        
    m = await bot.fetch_user(member_id)
    member_name = "{0.name}#{0.discriminator}".format(m)
    
    if member_id in point_totals:
        point_totals[member_id] += value
    else:
        point_totals[member_id] = value
        
    await contxt.send( "```{0} points awarded to {1}!```".format(value, member_name) )
    
## CMD UTILITY FUNCTION: display_user_point_total
async def display_user_point_total(contxt, member_id):
    """
    Displays points for a specified user
    """
    
    m = await bot.fetch_user(member_id)
    member_name = "{0.name}#{0.discriminator}".format(m)

    msg = "```Point Total (Single User):\n"
    
    if member_id in point_totals:
        msg += "{:32s} {:d}".format(member_name, point_totals[member_id])
    else:
        msg += "No points have been recorded for {0}".format(member_name)
    
    msg += "```"
    
    await contxt.send( msg )

@bot.command()
async def points( contxt, *args ):
    if len(args) < 1:
        await contxt.send(USAGE_POINTS_CMD.format(config["prefix"]))
        return
    
    if len(args) == 1:
        if args[0] == "total":
            await display_all_point_totals(contxt)
        else:
            member_id = args[0][2:-1]
            await display_user_point_total(contxt, member_id)
    else:
        member_id = args[0][2:-1]
        await award_points(contxt, member_id, int(args[1]))
    
###############################################################################
## TASKS
###############################################################################
async def backup_config():
    # delay (in seconds) to backup point totals to file
    BACKUP_DELAY = 10
    
    while True:
        await bot.wait_until_ready()
        save_config()
        await asyncio.sleep(BACKUP_DELAY)


bot.loop.create_task(backup_config())
###############################################################################
## DRIVER / RUN CODE
###############################################################################
bot.run(config["token"])