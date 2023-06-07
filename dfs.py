import discord, asyncio, os
from discord.ext import commands

bot = commands.Bot(command_prefix='$', help_command=None, intents=discord.Intents.all())

config = {
    "collaboration": True # if False, only the server owner can create channels
}

@bot.event
async def on_ready():
    print(f'dfs online as {bot.user}, please bear in mind dfs is only designed for one server.')

@bot.command()
async def setup(ctx):
    await asyncio.gather(*[channel.delete() for channel in ctx.guild.channels])
    await asyncio.gather(*[category.delete() for category in ctx.guild.categories])

    await ctx.guild.create_text_channel("terminal")

@bot.event
async def on_guild_channel_create(channel):
    if isinstance(channel, discord.VoiceChannel) or channel.name == "terminal": return

    async for entry in channel.guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_create):
        if not config["collaboration"] and entry.user != channel.guild.owner: await channel.delete(); continue
        
        if isinstance(channel, discord.TextChannel):
            if channel.category:
                category_name = channel.category.name
                open(f"{category_name}/{channel.name.replace('-', '.')}", "w").close()
            else: open(f"{channel.name.replace('-', '.')}", "w").close()

        elif isinstance(channel, discord.CategoryChannel):
            os.mkdir(channel.name)

# @bot.event
# async def on_guild_channel_edit(before, after):
# for some reason on_guild_channel_edit isn't.. called?

@bot.event
async def on_guild_channel_delete(channel):
    if isinstance(channel, discord.VoiceChannel) or channel.name == "terminal": return

    if isinstance(channel, discord.TextChannel):
        if channel.category:
            category_name = channel.category.name
            os.remove(f"{category_name}/{channel.name.replace('-', '.')}")
        else: os.remove(f"{channel.name.replace('-', '.')}")
    
    elif isinstance(channel, discord.CategoryChannel):
        os.rmdir(f"{channel.name}")

async def writeChannelHistory(message, filepath):
    if message.author == bot.user: return

    filepath = f""

    if message.channel.category: filepath += f"{message.channel.category.name}/"
    filepath += f"{message.channel.name.replace('-', '.')}"

    with open(filepath, "w") as f:
        channelHandle = bot.get_channel(message.channel.id)

        messages = []
        async for message in channelHandle.history(limit=None):
            messages.append(message.content)
        messages.reverse()

        for message in messages:
            # if message.content.startswith("```") and message.content.endswith("```"): message.content = message.content[3:-3]
            f.write(f"{message}\n")

@bot.event
async def on_message(message):
    if message.channel.name == "terminal" and message.author != bot.user and not message.content.startswith('$'):
        out = os.popen(message.content).read()
        await message.channel.send("```" + out + "```" if out != "" else "```no output```")
    
    elif message.channel.name != "terminal" and message.author != bot.user and not message.content.startswith("$"):
        await writeChannelHistory(message)

    elif message.content.startswith("$"): await bot.process_commands(message)

@bot.event
async def on_message_edit(before, after):
    if after.channel.name != "terminal" and after.author != bot.user and not after.content.startswith("$"):
        await writeChannelHistory(after)

@bot.event
async def on_message_delete(message):
    if message.channel.name != "terminal" and message.author != bot.user and not message.content.startswith("$"):
        await writeChannelHistory(message)

with open("token.secret", "r") as f:
    token = f.read()

os.chdir("dfs")
bot.run(token, log_handler=None)
