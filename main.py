import os, json_methods
from dotenv import load_dotenv

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

import interactions
from interactions import slash_command, SlashContext, OptionType, slash_option

bot = interactions.Client()

@interactions.listen()
async def on_startup():
    print("Bot is ready!")


@slash_command(name="speak", 
               description="Say something out loud.")
@slash_option(
    name="text",
    description="Type some text for it to be said out in public!",
    required=True,
    opt_type=OptionType.STRING
)
async def say(ctx: SlashContext, text: str):
    data = json_methods.open_file()
    if not str(ctx.author.id) in data["players"]:
        embed = interactions.Embed(
        description="You do not have a user profile! Use /create_profile to make one!",
        color=0x7CB7D3)
        await ctx.send(embeds=embed)
    else:
        channel = await interactions.get(bot, interactions.Channel, object_id=data["chat"]["main"])
        embed = interactions.Embed(
        description=text,
        color=0x7CB7D3)
        embed.set_author(name=data["players"][str(ctx.author.id)]["name"], icon_url=data["players"][str(ctx.author.id)]["image"])
        await channel.send(embeds=embed)


@slash_command(name="create_profile", 
               description="Create a profile to talk!")
@slash_option(
    name="name",
    description="Create a name for your profile!",
    required=True,
    opt_type=OptionType.STRING
)
@slash_option(
    name="avi",
    description="Upload an image for your avatar!",
    required=True,
    opt_type=OptionType.ATTACHMENT
)
async def profile(ctx: SlashContext, name: str, avi):
    if not str(ctx.author.id) in data["players"]:
        data = json_methods.open_file()
        data["players"][ctx.author.id] = {
            "name":name,
            "image":avi.url
            }
        json_methods.update_file(data)
        await ctx.send("Done!")
    else:  
        embed = interactions.Embed(
        description="You already have a user profile!",
        color=0x7CB7D3)
        await ctx.send(embeds=embed)


@slash_command(name="change_name", 
               description="Change your name!")
@slash_option(
    name="name",
    description="Create a new name for your profile!",
    required=True,
    opt_type=OptionType.STRING
)
async def name_change(ctx: SlashContext, name: str):
    data = json_methods.open_file()
    if not str(ctx.author.id) in data["players"]:
        embed = interactions.Embed(
        description="You do not have a user profile! Use /create_profile to make one!",
        color=0x7CB7D3)
        await ctx.send(embeds=embed)
    else:  
        data["players"][str(ctx.author.id)]["name"] = name
        json_methods.update_file(data)
        await ctx.send("Done!")


@slash_command(name="change_avatar", 
               description="Change your avatar!")
@slash_option(
    name="avi",
    description="Upload an image for your new avatar!",
    required=True,
    opt_type=OptionType.ATTACHMENT
)
async def image_change(ctx: SlashContext, avi):
    data = json_methods.open_file()
    if not str(ctx.author.id) in data["players"]:
        embed = interactions.Embed(
        description=f"You do not have a user profile! Use /create_profile to make one!",
        color=0x7CB7D3)
        await ctx.send(embeds=embed)
    else:  
        data["players"][str(ctx.author.id)]["image"] = avi
        json_methods.update_file(data)
        await ctx.send("Done!")

@slash_command(name="assign_channel", 
               description="Assign this channel to speak to be able to speak in!")
@slash_option(
    name="channel_name",
    description="This is the name you will give your channel when calling it!",
    required=True,
    opt_type=OptionType.STRING
)
async def channel_assign(ctx: SlashContext, name: str):
    data = json_methods.open_file()
    if name in data["chat"]:
        embed = interactions.Embed(
        description="This channel has already been assigned!",
        color=0x7CB7D3)
        await ctx.send(embeds=embed)
    else:  
        data["players"]["chat"][name] = {
            "channel":ctx.channel.id,
            }
        json_methods.update_file(data)
        await ctx.send("Done!")

bot.start(token)