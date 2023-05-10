import os
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
               description="Say something out loud",)
@slash_option(
    name="string_option",
    description="String Option",
    required=True,
    opt_type=OptionType.STRING
)
async def say(ctx: SlashContext, string_option: str):
    embed = interactions.Embed(
        title=f"{ctx.author} says:",
        description=string_option,
        color=0x7CB7D3)
    await ctx.send(embeds=embed)

bot.start(token)