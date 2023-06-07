import discord, json, os
from discord.ext import commands


bot = commands.Bot(command_prefix='$', help_command=None, intents=discord.Intents.all())

config = {
    "collaboration": True
}

@bot.event
async def on_ready():
    print(f'dfs online as {bot.user}')

@bot.command()
async def setup(ctx):
    for channel in ctx.guild.channels:
        await channel.delete()
    for category in ctx.guild.categories:
        await category.delete()

    terminal = await ctx.guild.create_text_channel("terminal")

#TODO: make prettier
def makefile(channel):
    if channel.category:
        category_name = channel.category.name

        if os.path.isdir(category_name):
            with open(f"{category_name}/{channel.name.replace('-', '.')}", "w") as f: 
                f.write("")
        else:
            os.mkdir(category_name)
            with open(f"{category_name}/{channel.name.replace('-', '.')}", "w") as f: 
                f.write("")
    else:
        with open(f"{channel.name.replace('-', '.')}", "w") as f: 
            f.write("")

@bot.event
async def on_guild_channel_create(channel):
    if isinstance(channel, discord.VoiceChannel):
        print("voice channel created"); return


    if channel.name == "terminal": return
    else: 
        async for entry in channel.guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_create):
            
            if not config["collaboration"] and entry.user != channel.guild.owner: 
                await channel.delete()
            else: 
                if isinstance(channel, discord.TextChannel): makefile(channel)
                elif isinstance(channel, discord.CategoryChannel): os.mkdir(channel.name)

@bot.event
async def on_guild_channel_delete(channel):
    if isinstance(channel, discord.VoiceChannel):
        print("voice channel deleted"); return

    if channel.name == "terminal": return
    else:
        if isinstance(channel, discord.TextChannel): 
            if channel.category:
                category_name = channel.category.name
                os.remove(f"{category_name}/{channel.name.replace('-', '.')}")
            else:
                os.remove(f"{channel.name.replace('-', '.')}")
        elif isinstance(channel, discord.CategoryChannel): 
            os.rmdir(channel.name)

# on message
@bot.event
async def on_message(message):
    # if the channel name is terminal
    if message.channel.name == "terminal" and message.author != bot.user and not message.content.startswith("$"):
        await message.channel.send("```" + os.popen(message.content).read() + "```")
    elif message.channel.name != "terminal" and message.author != bot.user and not message.content.startswith("$"):
        # get all messages in the channel, loop through them, and write them to the file
        if message.channel.category:
            category_name = message.channel.category.name
            with open(f"{category_name}/{message.channel.name.replace('-', '.')}", "w") as f: 
                channel = bot.get_channel(message.channel.id)
                
                arr = []
                async for message in channel.history(limit=None):
                    arr.append(message.content)
                # invert the array
                arr.reverse()
                # write the array to the file
                for message in arr:
                    f.write(f"{message}\n")
        else:
            with open(f"{message.channel.name.replace('-', '.')}", "w") as f: 
                print(f"{message.channel.history(limit=None).flatten()[0].content}\n")

    elif message.content.startswith("$"):
        await bot.process_commands(message)

# on message edit
@bot.event
async def on_message_edit(before, after):
    if before.channel.name == "terminal" and before.author != bot.user and not before.content.startswith("$"):
        await before.channel.send("```" + os.popen(before.content).read() + "```")
    elif before.channel.name != "terminal" and before.author != bot.user and not before.content.startswith("$"):
        # get all messages in the channel after the edited message, loop through them, and write them to the file
        if before.channel.category:
            category_name = before.channel.category.name
            with open(f"{category_name}/{before.channel.name.replace('-', '.')}", "w") as f: 
                channel = bot.get_channel(before.channel.id)
                
                arr = []
                async for message in channel.history(limit=None):
                    arr.append(message.content)
                # invert the array
                arr.reverse()
                # write the array to the file
                for message in arr:
                    f.write(f"{message}\n")

# on message delete
@bot.event
async def on_message_delete(message):
    if message.channel.name != "terminal" and message.author != bot.user and not message.content.startswith("$"):
        # get all messages in the channel, loop through them, and write them to the file
        if message.channel.category:
            category_name = message.channel.category.name
            with open(f"{category_name}/{message.channel.name.replace('-', '.')}", "w") as f: 
                channel = bot.get_channel(message.channel.id)
                
                arr = []
                async for message in channel.history(limit=None):
                    arr.append(message.content)
                # invert the array
                arr.reverse()
                # write the array to the file
                for message in arr:
                    f.write(f"{message}\n")



with open("token.secret", "r") as f:
    token = f.read()

os.chdir("dfs")
bot.run(token, log_handler=None)