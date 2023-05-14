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
    data = json_methods.open_file(ctx.guild_id)
    full_data = data[1]
    data = data[0]
    if not str(ctx.author.id) in data["individuals"]:
        embed = interactions.Embed(
        description="You do not have a user profile! Use /create_profile to make one!",
        color=0x7CB7D3)
        await ctx.send(embeds=embed)
    else:
        if not "main" in data["chat"]["channel"]:
            po = interactions.PermissionOverwrite(id=ctx.guild.id, type=0)
            po.add_denies(interactions.Permissions.SEND_MESSAGES)
            category = await ctx.guild.create_channel(channel_type=4, name="global channels")
            data["chat"]["channel"]["global_chats"] = {
                "id": category.id
            }
            channel = await ctx.guild.create_channel(channel_type=0, name="main_chat", permission_overwrites=po, category=data["chat"]["channel"]["global_chats"]["id"])
            data["chat"]["channel"]["main"] = {
                "id": channel.id
            }
            json_methods.update_file(data, ctx.guild_id, full_data)
        main_channel = bot.get_channel(data["chat"]["channel"]["main"]["id"])
        embed = interactions.Embed(
        description=text,
        color=0x7CB7D3)
        embed.set_author(name=data["individuals"][str(ctx.author.id)]["name"], icon_url=data["individuals"][str(ctx.author.id)]["image"])
        for person in data["profiles"]:
            if not data["profiles"][person]["id"] == ctx.author.id:
                private_channel = bot.get_channel(data["profiles"][person]["hub"])
                await private_channel.send(embeds=embed)
        await main_channel.send(embeds=embed)
        await ctx.send(embeds=embed)

@slash_command(name="dm", 
               description="Say something to someone or a group!")
@slash_option(
    name="text",
    description="Type some text for it to be said to your chosen dm!",
    required=True,
    opt_type=OptionType.STRING
)
@slash_option(
    name="dm",
    description="Indicate here who you would like to send this message to!",
    required=True,
    opt_type=OptionType.STRING
)
async def dm(ctx: SlashContext, text: str, dm: str):
    data = json_methods.open_file(ctx.guild_id)
    data = data[0]
    if not str(ctx.author.id) in data["individuals"]:
        embed = interactions.Embed(
        description="You do not have a user profile! Use /create_profile to make one!",
        color=0x7CB7D3)
        await ctx.send(embeds=embed)
    else:
        embed = interactions.Embed(
        description=text,
        color=0x7CB7D3)
        if dm.lower() in data["chat"]["individual"]:
            embed.set_author(name=data["individuals"][str(ctx.author.id)]["name"] + " (DM)", icon_url=data["individuals"][str(ctx.author.id)]["image"])
            for person in data["profiles"]:
                if person.lower() == dm.lower() and not person.lower() == data["individuals"][str(ctx.author.id)]["name"]:
                    dm_channel = bot.get_channel(data["profiles"][person]["dm"])
                    await dm_channel.send(embeds=embed)
            await ctx.send(embeds=embed)
        elif dm.lower() in data["chat"]["group"]:
            embed.set_author(name=data["individuals"][str(ctx.author.id)]["name"] + " (" + dm + ")", icon_url=data["individuals"][str(ctx.author.id)]["image"])
            for person in data["profiles"]:
                if person.lower() in data["chat"]["group"][dm.lower()]["members"] and not person.lower() == data["individuals"][str(ctx.author.id)]["name"]:
                    dm_channel = bot.get_channel(data["profiles"][person]["dm"])
                    await dm_channel.send(embeds=embed)
            await ctx.send(embeds=embed)
        else:
            embed = interactions.Embed(
            description="This chat does not exist!",
            color=0x7CB7D3)
            await ctx.send(embeds=embed)


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
    data = json_methods.open_file(ctx.guild_id)
    full_data = data[1]
    data = data[0]
    if not str(ctx.author.id) in data["individuals"] and not name.lower() in data["profiles"] and not name.lower() in data["chat"]["group"]:
        data["individuals"][ctx.author.id] = {
            "name": name,
            "image": avi.url
        }
        po = interactions.PermissionOverwrite(id=ctx.guild.id, type=0)
        po.add_denies(interactions.Permissions.VIEW_CHANNEL)
        if not "categories" in data["chat"]["channel"]:
            category = await ctx.guild.create_channel(channel_type=4, name="individual channels")
            data["chat"]["channel"]["categories"] = {
                "id": category.id
            }
        channel = await ctx.guild.create_channel(channel_type=0, name=f"{name}_hub", permission_overwrites=po, category=data["chat"]["channel"]["categories"]["id"])
        dm_channel = await ctx.guild.create_channel(channel_type=0, name=f"{name}_DM", permission_overwrites=po, category=data["chat"]["channel"]["categories"]["id"])
        data["profiles"][name.lower()] = {
            "id": ctx.author.id,
            "hub": channel.id,
            "dm": dm_channel.id,
            "journal": None
        }
        if data["settings"]["journal"]:
            journal_channel = await ctx.guild.create_channel(channel_type=0, name=f"{name}_journal", permission_overwrites=po, category=data["chat"]["channel"]["categories"]["id"])
            data["profiles"][name.lower()]["journal"] = journal_channel.id
        data["chat"]["individual"][name.lower()] = {
            "dm": dm_channel.id
        }
        json_methods.update_file(data, ctx.guild_id, full_data)
        await ctx.send("Done!")
    else:
        if str(ctx.author.id) in data["individuals"]:  
            embed = interactions.Embed(
            description="You already have a user profile!",
            color=0x7CB7D3)
        elif name.lower() in data["profiles"]:
            embed = interactions.Embed(
            description="This name is already taken! Please choose another name.",
            color=0x7CB7D3)
        else:
            embed = interactions.Embed(
            description="This name is already the name of a group chat! Please choose another name",
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
    data = json_methods.open_file(ctx.guild_id)
    full_data = data[1]
    data = data[0]
    if not str(ctx.author.id) in data["individuals"]:
        embed = interactions.Embed(
        description="You do not have a user profile! Use /create_profile to make one!",
        color=0x7CB7D3)
        await ctx.send(embeds=embed)
    elif name.lower() in data["profiles"]:
        embed = interactions.Embed(
        description="This name is already taken! Please choose another name.",
        color=0x7CB7D3)
        await ctx.send(embeds=embed)
    elif name.lower() in data["chat"]["group"]:
        embed = interactions.Embed(
        description="This name is already the name of a group chat! Please choose another name.",
        color=0x7CB7D3)
        await ctx.send(embeds=embed)
    else:  
        data["individuals"][str(ctx.author.id)]["name"] = name
        json_methods.update_file(data, ctx.guild_id, full_data)
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
    data = json_methods.open_file(ctx.guild_id)
    full_data = data[1]
    data = data[0]
    if not str(ctx.author.id) in data["individuals"]:
        embed = interactions.Embed(
        description=f"You do not have a user profile! Use /create_profile to make one!",
        color=0x7CB7D3)
        await ctx.send(embeds=embed)
    else:  
        data["individuals"][str(ctx.author.id)]["image"] = avi
        json_methods.update_file(data, int(ctx.guild_id), full_data)
        await ctx.send("Done!")

@slash_command(name="assign_channel", 
               description="Assign this channel to speak to be able to speak in!")
@slash_option(
    name="channel_name",
    description="This is the name you will give your channel when calling it!",
    required=True,
    opt_type=OptionType.STRING
)
async def channel_assign(ctx: SlashContext, channel_name: str):
    data = json_methods.open_file(ctx.guild_id)
    full_data = data[1]
    data = data[0]
    if channel_name.lower() in data["chat"]["channel"]:
        embed = interactions.Embed(
        description="This channel has already been assigned!",
        color=0x7CB7D3)
        await ctx.send(embeds=embed)
    else:  
        data["chat"]["channel"][channel_name.lower()] = {
            "id": ctx.channel.id,
            }
        json_methods.update_file(data, ctx.guild_id, full_data)
        await ctx.send("Done!")


@slash_command(name="chat_creation", 
               description="Create a new group chat with other people!")
@slash_option(
    name="channel_name",
    description="This is the name of the group.",
    required=True,
    opt_type=OptionType.STRING
)
async def group_creation(ctx: SlashContext, channel_name: str):
    data = json_methods.open_file(ctx.guild_id)
    full_data = data[1]
    data = data[0]
    if channel_name.lower() in data["chat"]["group"]:
        embed = interactions.Embed(
        description="This group name has already been assigned!",
        color=0x7CB7D3)
        await ctx.send(embeds=embed)
    elif channel_name.lower() in data["profiles"]:
        embed = interactions.Embed(
        description="This is already somebodys name! Please do not use it.",
        color=0x7CB7D3)
        await ctx.send(embeds=embed)
    else:  
        data["chat"]["group"][channel_name.lower()] = {
            "members": [data["individuals"][str(ctx.author.id)]["name"]]
            }
        json_methods.update_file(data, ctx.guild_id, full_data)
        await ctx.send("Done!")
    

@slash_command(name="chat_add_members", 
               description="Add a player to your chat!")
@slash_option(
    name="channel_name",
    description="This is the name of the group the person will be added to.",
    required=True,
    opt_type=OptionType.STRING
)
@slash_option(
    name="person_name",
    description="This is the name of the person who will be added to the group.",
    required=True,
    opt_type=OptionType.STRING
)
async def group_adding(ctx: SlashContext, channel_name: str, person_name: str):
    data = json_methods.open_file(ctx.guild_id)
    full_data = data[1]
    data = data[0]
    if person_name.lower() in data["chat"]["group"][channel_name.lower()]["members"]:
        embed = interactions.Embed(
        description="This profile is already in the group!",
        color=0x7CB7D3)
        await ctx.send(embeds=embed)
    elif not person_name.lower() in data["profiles"]:
        embed = interactions.Embed(
        description="This profile does not exist!",
        color=0x7CB7D3)
        await ctx.send(embeds=embed)
    else:  
        data["chat"]["group"][channel_name.lower()]["members"].append(person_name.lower())
        json_methods.update_file(data, ctx.guild_id, full_data)
        await ctx.send("Done!")

@slash_command(name="toggle_journal", 
               description="Toggle your preference for the journal setting!")
@slash_option(
    name="toggle",
    description="Choose whether you want to turn it on or off!",
    required=True,
    opt_type=OptionType.BOOLEAN
)
async def toggle_journal(ctx: SlashContext, toggle: bool):
    data = json_methods.open_file(ctx.guild_id)
    full_data = data[1]
    data = data[0]
    if toggle:
        data["settings"]["journal"] = True
        for person in data["profiles"]:
            po = interactions.PermissionOverwrite(id=ctx.guild.id, type=0)
            po.add_denies(interactions.Permissions.VIEW_CHANNEL)
            journal_channel = await ctx.guild.create_channel(channel_type=0, name=f"{person}_journal", permission_overwrites=po, category=data["chat"]["channel"]["categories"]["id"])
            data["profiles"][person.lower()]["journal"] = journal_channel.id
            
    else:
        data["settings"]["journal"] = False
    json_methods.update_file(data, ctx.guild_id, full_data)
    await ctx.send("Your journal settings have been updated!")

bot.start(token)