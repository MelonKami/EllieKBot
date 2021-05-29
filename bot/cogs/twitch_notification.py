import requests, discord, datetime, asyncio
from discord.ext import commands, tasks
from bot import utils

def create_embed(title, description: str = None, thumbnail_url: str = None, url: str = None):
    embed = discord.Embed(title=title, description=description)
    embed.set_footer(text='EllieK!')
    embed.url = url
    embed.timestamp = datetime.datetime.now()
    return embed

def game_cat(game_id):
    headers = {
        'client-id': 'uaw2j62l5svawsiomdmw0n4t0a8mwp',
        'Authorization': 'Bearer iey78jslbaw2q43fvbtqk9i2x4xfj1'
    }
    response = requests.get(f'https://api.twitch.tv/helix/games?id={game_id}', headers=headers)
    game_name = response.json()["data"][0]
    return game_name


def twitch_live_check(twitch_username):
    headers = {
        'client-id': 'uaw2j62l5svawsiomdmw0n4t0a8mwp',
        'Authorization': 'Bearer iey78jslbaw2q43fvbtqk9i2x4xfj1'
    }
    #response = requests.get(
    #'https://api.twitch.tv/helix/channels?broadcaster_id=193583334',
    #headers=headers)
    response = requests.get(
        f'https://api.twitch.tv/helix/search/channels?query={twitch_username}',
        headers=headers)
    return response


class TwitchNotif(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.twitch_status.start()

    @commands.command()
    async def streamer_remove(self, ctx, streamer_name):
        await ctx.message.delete()
        message = await ctx.send(f'Fjernet {streamer_name} i stream notification listen!')
        utils.config.config["streamers"].pop(streamer_name)
        utils.config.save_config()
        await message.delete(delay=10)

    @commands.command()
    async def streamers(self, ctx):
        embed = create_embed('Streamere i notif listen!')

        for streamer in utils.config.config["streamers"]:
            embed.add_field(name='Streamer navn', value=streamer)

        await ctx.send(embed=embed)

    @commands.command()
    async def streamer_add(self, ctx, streamer_name):
        execute = True
        await ctx.message.delete()

        def check(reaction, user):
            return user == ctx.message.author

        for streamer_name_json in utils.config.config["streamers"]:
            if streamer_name_json == streamer_name:
                execute = False
                message2 = await ctx.send('Streameren er allerede lagt til!')
                await message2.delete(delay=10)
            else:
                execute = True

        if execute:
            print('execute')
            data = twitch_live_check(streamer_name).json()["data"]
            index = 0
            for streamer_data in data[index]:
                if data[index]["display_name"] == streamer_name:
                    message = await ctx.send(embed=create_embed(f'Er det denne streameren du ønsker å legge til? {data[index]["display_name"]}', url=f'https://twitch.tv/{streamer_name}').set_image(url=data[index]["thumbnail_url"]))
                    await message.add_reaction('✔')
                    await message.add_reaction('❌')
                    reaction = await self.bot.wait_for('reaction_add', check=check)

                    if reaction[0].emoji == '✔':
                        print('added')
                        utils.config.config["streamers"][streamer_name] = False
                        message3 = await ctx.send(f'La til {streamer_name} i stream notification listen!')
                        await message3.delete(delay=10)
                    else:
                        message1 = await ctx.send('Du har mest sannsynlig gjort en feil med store og små bokstaver, prøv igjen og vær obs på dette!')
                        await message1.delete(delay=10)

                    break
                else:
                    index += 1

            await message.delete(delay=10)
            utils.config.save_config()

    @tasks.loop(seconds=30)
    async def twitch_status(self):
        guild = self.bot.get_guild(434081508173545502)
        channel = discord.utils.get(guild.text_channels, id=435717890247753729)
        streamer_nicknames = utils.config.config["streamers"]

        for streamer in streamer_nicknames:
            index = 0
            data = twitch_live_check(streamer).json()["data"]
            for streamer_data in data[index]:
                if data[index]["display_name"] == streamer:
                    if utils.config.config["streamers"][streamer] == True and data[index]["is_live"] == False:
                        utils.config.config["streamers"][streamer] = False
                        utils.config.save_config()


                    elif utils.config.config["streamers"][streamer] == False and data[index]["is_live"] == True:
                        utils.config.config["streamers"][streamer] = True
                        utils.config.save_config()



                        game_category = game_cat(data[index]["game_id"])
                        game_icon = game_category["box_art_url"]
                        game_icon = game_icon.replace('{width}', '52')
                        game_icon = game_icon.replace('{height}', '72')

                        embed = create_embed(f'🔴 {data[index]["display_name"]} er LIVE! 🔴', 'Alle sammen sjekk ut streamen!', url=f'https://twitch.tv/{streamer}').add_field(name='Tittel', value=f'**{data[index]["title"]}**').add_field(name='Kategori', value=game_category["name"], inline=False).set_author(name=data[index]["display_name"], icon_url=data[index]["thumbnail_url"]).set_thumbnail(url=game_icon)

                        await channel.send(f'@everyone {streamer} er live! Sjekk ut streamen!', embed=embed.set_image(url=data[index]["thumbnail_url"]))



                index += 1
            


def setup(bot):
    bot.add_cog(TwitchNotif(bot))
