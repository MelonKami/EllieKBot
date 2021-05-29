import discord, datetime, os
from discord.ext import commands, tasks
from bot import utils
from termcolor import colored

print(colored('----STARTER DISCORD BOT----', 'green'))
startup_time = datetime.datetime.now()
print(startup_time.strftime('Tid: %H:%M:%S'))
print()

#Bot code

prefix = '!'

intents = discord.Intents.default()
bot = commands.Bot(command_prefix=prefix, case_insensitive=True, intents=intents)
bot.remove_command('help')

def format_filename(extension):
    formatet_name = f'{extension}'
    return formatet_name.replace('.py', '')    

@tasks.loop(hours=6)
async def reload_extension():
    print('Reloading cogs')
    for extension in os.listdir('bot/cogs'):
        if extension != '__pycache__':
            try:
                bot.reload_extension(f'bot.cogs.{format_filename(extension)}')
            except:
                bot.load_extension(f'bot.cogs.{format_filename(extension)}')

@bot.event
async def on_ready():
    print(colored('----BOTTEN HAR STARTET----', 'green'))
    bot_ready_time = datetime.datetime.now()
    print(bot_ready_time.strftime('Tid: %H:%M:%S'))
    time = bot_ready_time - startup_time
    if time > datetime.timedelta(seconds=10):
        color = 'red'
    else:
        color = 'green'
    print(colored('Start opp tid:', 'green'), colored(time, color))
    print()
    print()
    print('Logget inn som {0.user}'.format(bot))
    print()

    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='twitch.tv/EllieK!'))
    reload_extension.start()

with open('token.txt', 'r') as File:
    token = File.read()

def run():
    bot.run(token)