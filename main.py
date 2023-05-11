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
               description="Say something out loud.",)
@slash_option(
    name="text",
    description="Text",
    required=True,
    opt_type=OptionType.STRING
)
async def say(ctx: SlashContext, text: str):
    data = json_methods.open_file()
    if (not data["players"][str(ctx.author.id)]):
        embed = interactions.Embed(
        title=f"You do not have a user profile! Use /create_profile to make one!",
        description=text,
        color=0x7CB7D3)
        await ctx.send(embeds=embed)
    else:   
        embed = interactions.Embed(
        description=text,
        color=0x7CB7D3)
        embed.set_author(name=data["players"][str(ctx.author.id)]["name"], icon_url=data["players"][str(ctx.author.id)]["image"])
        await ctx.send(embeds=embed)

@slash_command(name="create_profile", 
               description="Create a profile to talk!",)
@slash_option(
    name="name",
    description="Name",
    required=True,
    opt_type=OptionType.STRING
)
@slash_option(
    name="avi",
    description="Image",
    required=True,
    opt_type=OptionType.ATTACHMENT
)
async def profile(ctx: SlashContext, name: str, avi):
    data = json_methods.open_file()
    data["players"][ctx.author.id] = {
        "name":name,
        "image":avi.url
        }
    json_methods.update_file(data)
    await ctx.send("Done!")

bot.start(token)