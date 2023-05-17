import os, json_methods, json, random
from dotenv import load_dotenv

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

import interactions
from interactions import slash_command, SlashContext, OptionType, slash_option, slash_default_member_permission, Color

bot = interactions.Client()

@interactions.listen()
async def on_startup():
    print("Bot is ready!")


@slash_command(name="say", 
               description="Say something out loud.")
@slash_option(
    name="text",
    description="Type some text for it to be said out in public!",
    required=True,
    opt_type=OptionType.STRING
)
@slash_option(
    name="image",
    description="Upload an image to be said out in public!",
    required=False,
    opt_type=OptionType.ATTACHMENT
)
@slash_option(
    name="chat",
    description="What public chat do you want to send your message in? (Default is the main channel)",
    required=False,
    opt_type=OptionType.ATTACHMENT
)
async def say(ctx: SlashContext, text: str, image=None, chat="main"):
    data = json_methods.open_file(ctx.guild_id)
    data = data[0]
    if not str(ctx.author.id) in data["individuals"]:
        embed = interactions.Embed(
        description="You do not have a user profile! Use /create_profile to make one!",
        color=0x7CB7D3)
        await ctx.send(embeds=embed)
    else:
        send_channel = bot.get_channel(data["chat"]["channel"][chat]["id"])
        embed = interactions.Embed(
        description=text,
        color=Color.from_hex(data["profiles"][data["individuals"][str(ctx.author.id)]["name"].lower()]["color"]))
        embed.set_author(name=data["individuals"][str(ctx.author.id)]["name"], icon_url=data["individuals"][str(ctx.author.id)]["image"])
        if image:
            embed.set_image(image.url)
        for person in data["profiles"]:
            if not data["profiles"][person]["id"] == ctx.author.id:
                private_channel = bot.get_channel(data["profiles"][person]["hub"])
                await private_channel.send(embeds=embed)
        await send_channel.send(embeds=embed)
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
        color=Color.from_hex(data["profiles"][data["individuals"][str(ctx.author.id)]["name"].lower()]["color"]))
        if dm.lower() in data["chat"]["individual"]:
            embed.set_author(name=data["individuals"][str(ctx.author.id)]["name"] + " (DM)", icon_url=data["individuals"][str(ctx.author.id)]["image"])
            for person in data["profiles"]:
                if person.lower() == dm.lower() and not person.lower() == data["individuals"][str(ctx.author.id)]["name"]:
                    dm_channel = bot.get_channel(data["profiles"][person]["dm"])
                    await dm_channel.send(embeds=embed)
            await ctx.send(embeds=embed)
        elif dm.lower() in data["chat"]["group"]:
            if not data["individuals"][ctx.author.id]["name"] in data["chat"]["group"][dm.lower()]["members"]:
                await ctx.send("You're not in this group!")
                return
            embed.set_author(name=data["individuals"][str(ctx.author.id)]["name"] + " (" + dm + ")", icon_url=data["individuals"][str(ctx.author.id)]["image"])
            if data["chat"]["group"][dm.lower()]["image"]:
                embed.set_thumbnail(data["chat"]["group"][dm.lower()]["image"])
            for person in data["profiles"]:
                if person.lower() in data["chat"]["group"][dm.lower()]["members"] and not person.lower() == data["individuals"][str(ctx.author.id)]["name"]:
                    dm_channel = bot.get_channel(data["profiles"][person]["dm"])
                    await dm_channel.send(embeds=embed)
            await ctx.send(embeds=embed)
        else:
            embed = interactions.Embed(
            description="This chat does not exist!",
            color=Color.from_hex(data["profiles"][data["individuals"][str(ctx.author.id)]["name"].lower()]["color"]))
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
    if not "main" in data["chat"]["channel"]:
        po = interactions.PermissionOverwrite(id=ctx.guild.id, type=0)
        po.add_denies(interactions.Permissions.SEND_MESSAGES)
        category = await ctx.guild.create_channel(channel_type=4, name="global channels")
        data["chat"]["channel"]["public_category"] = {
            "id": category.id
        }
        channel = await ctx.guild.create_channel(channel_type=0, name="main-chat", permission_overwrites=po, category=data["chat"]["channel"]["public_category"]["id"])
        data["chat"]["channel"]["main"] = {
            "id": channel.id
        }
        json_methods.update_file(data, ctx.guild_id, full_data)
    if not str(ctx.author.id) in data["individuals"] and not name.lower() in data["profiles"] and not name.lower() in data["chat"]["group"]:
        file = open('colors.json')
        values = json.load(file)
        data["individuals"][ctx.author.id] = {
            "name": name,
            "image": avi.url
        }
        po = interactions.PermissionOverwrite(id=ctx.guild.id, type=0)
        po.add_denies(interactions.Permissions.VIEW_CHANNEL)
        pa = interactions.PermissionOverwrite(id=ctx.author.id, type=1)
        pa.add_allows(interactions.Permissions.VIEW_CHANNEL)
        if not "individual_category" in data["chat"]["channel"]:
            category = await ctx.guild.create_channel(channel_type=4, name="individual channels")
            data["chat"]["channel"]["individual_category"] = {
                "id": category.id
            }
        channel = await ctx.guild.create_channel(channel_type=0, name=f"{name}-hub", permission_overwrites=[po, pa], category=data["chat"]["channel"]["individual_category"]["id"])
        dm_channel = await ctx.guild.create_channel(channel_type=0, name=f"{name}-DM", permission_overwrites=[po, pa], category=data["chat"]["channel"]["individual_category"]["id"])
        data["profiles"][name.lower()] = {
            "id": ctx.author.id,
            "color": random.choice(list(values.values())),
            "hub": channel.id,
            "dm": dm_channel.id,
            "journal": None
        }
        if data["settings"]["journal"]:
            journal_channel = await ctx.guild.create_channel(channel_type=0, name=f"{name}-journal", permission_overwrites=[po, pa], category=data["chat"]["channel"]["journal_category"]["id"])
            data["profiles"][name.lower()]["journal"] = journal_channel.id
        data["chat"]["individual"][name.lower()] = {
            "dm": dm_channel.id
        }
        json_methods.update_file(data, ctx.guild_id, full_data)
        await ctx.send("Your profile has been created!")
    else:
        if str(ctx.author.id) in data["individuals"]:  
            embed = interactions.Embed(
            description="You already have a user profile!",
            color=Color.from_hex(data["profiles"][name.lower()]["color"]))
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
        color=Color.from_hex(data["profiles"][data["individuals"][str(ctx.author.id)]["name"].lower()]["color"]))
        await ctx.send(embeds=embed)
    else:  
        data["individuals"][str(ctx.author.id)]["name"] = name
        data["individuals"][str(ctx.author.id)]["name"] = name
        data["chat"]["individual"][name] = data["chat"]["individual"][str(ctx.author.id)]
        del data["chat"]["individual"][str(ctx.author.id)]
        data["profiles"][name] = data["profiles"][str(ctx.author.id)]
        del data["profiles"][str(ctx.author.id)]
        json_methods.update_file(data, ctx.guild_id, full_data)
        await ctx.send("Your name has been changed!")


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
        data["individuals"][str(ctx.author.id)]["image"] = avi.url
        json_methods.update_file(data, int(ctx.guild_id), full_data)
        await ctx.send("Your profiles picture has been changed!")

@slash_command(name="channel_assign", 
               description="Assign this channel to speak to be able to speak in!")
@slash_default_member_permission(interactions.Permissions.ADMINISTRATOR)
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
        await ctx.send("This channel has been assigned as a public communication channel!")

@slash_command(name="channel_create", 
               description="Assign this channel to speak to be able to speak in!")
@slash_default_member_permission(interactions.Permissions.ADMINISTRATOR)
@slash_option(
    name="channel_name",
    description="This is the name you will give your channel when calling it!",
    required=True,
    opt_type=OptionType.STRING
)
async def channel_create(ctx: SlashContext, channel_name: str):
    data = json_methods.open_file(ctx.guild_id)
    full_data = data[1]
    data = data[0]
    if channel_name.lower() in data["chat"]["channel"]:
        embed = interactions.Embed(
        description="This channel name already exists!",
        color=0x7CB7D3)
        await ctx.send(embeds=embed)
    else:  
        if not "public_category" in data["chat"]["channel"]:
            category = await ctx.guild.create_channel(channel_type=4, name="individual channels")
            data["chat"]["channel"]["public_category"] = {
                "id": category.id
            }
        po = interactions.PermissionOverwrite(id=ctx.guild.id, type=0)
        po.add_denies(interactions.Permissions.SEND_MESSAGES)
        channel = await ctx.guild.create_channel(channel_type=0, name=channel_name, permission_overwrites=po, category=data["chat"]["channel"]["public_category"]["id"])
        data["chat"]["channel"][channel_name.lower()] = {
            "id": channel.id,
            }
        json_methods.update_file(data, ctx.guild_id, full_data)
        await ctx.send("A channel has been created!")


@slash_command(name="group_creation", 
               description="Create a new group chat with other people!")
@slash_option(
    name="group_name",
    description="This is the name of the group.",
    required=True,
    opt_type=OptionType.STRING
)
@slash_option(
    name="group_picture",
    description="This is an image associated with your group",
    required=False,
    opt_type=OptionType.ATTACHMENT
)
async def group_creation(ctx: SlashContext, group_name: str, group_picture=None):
    data = json_methods.open_file(ctx.guild_id)
    full_data = data[1]
    data = data[0]
    if group_name.lower() in data["chat"]["group"]:
        embed = interactions.Embed(
        description="This group name has already been assigned!",
        color=0x7CB7D3)
        await ctx.send(embeds=embed)
    elif group_name.lower() in data["profiles"]:
        embed = interactions.Embed(
        description="This is already somebodys name! Please do not use it.",
        color=0x7CB7D3)
        await ctx.send(embeds=embed)
    else:  
        data["chat"]["group"][group_name.lower()] = {
            "members": [data["individuals"][str(ctx.author.id)]["name"]],
            "image": None
            }
        if group_picture:
            data["chat"]["group"][group_name.lower()]["image"] = group_picture.url
        json_methods.update_file(data, ctx.guild_id, full_data)
        await ctx.send("Your group has been created!")
    

@slash_command(name="group_add_members", 
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
        await ctx.send("This member has been added to your group!")

@slash_command(name="toggle_journal", 
               description="Toggle your preference for the journal setting!")
@slash_default_member_permission(interactions.Permissions.ADMINISTRATOR)
@slash_option(
    name="toggle",
    description="Choose whether you want to turn it on or off!",
    required=True,
    opt_type=OptionType.BOOLEAN,
)
async def toggle_journal(ctx: SlashContext, toggle: bool):
    data = json_methods.open_file(ctx.guild_id)
    full_data = data[1]
    data = data[0]
    if toggle:
        if not "journal_category" in data["chat"]["channel"]:
            category = await ctx.guild.create_channel(channel_type=4, name="journals")
            data["chat"]["channel"]["journal_category"] = {
                "id": category.id
            }
        data["settings"]["journal"] = True
        pa = interactions.PermissionOverwrite(id=ctx.author.id, type=1)
        pa.add_allows(interactions.Permissions.VIEW_CHANNEL)
        for person in data["profiles"]:
            if data["profiles"][person.lower()]["journal"] == None:
                po = interactions.PermissionOverwrite(id=ctx.guild.id, type=0)
                po.add_denies(interactions.Permissions.VIEW_CHANNEL)
                journal_channel = await ctx.guild.create_channel(channel_type=0, name=f"{person}-journal", permission_overwrites=[po, pa], category=data["chat"]["channel"]["journal_category"]["id"])
                data["profiles"][person.lower()]["journal"] = journal_channel.id
            
    else:
        data["settings"]["journal"] = False
    json_methods.update_file(data, ctx.guild_id, full_data)
    await ctx.send("Your journal settings have been updated!")

@slash_command(name="admin_change_name", 
               description="Change your name!")
@slash_default_member_permission(interactions.Permissions.ADMINISTRATOR)
@slash_option(
    name="name",
    description="Create a new name for your profile!",
    required=True,
    opt_type=OptionType.STRING
)
@slash_option(
    name="person",
    description="Choose whos avatar you're changing!",
    required=True,
    opt_type=OptionType.STRING
)
async def admin_name_change(ctx: SlashContext, name: str, person: str):
    data = json_methods.open_file(ctx.guild_id)
    full_data = data[1]
    data = data[0]
    if not person in data["individuals"]:
        embed = interactions.Embed(
        description="This profile does not exist!",
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
        data["individuals"][person]["name"] = name
        data["chat"]["individual"][name] = data["chat"]["individual"][person]
        del data["chat"]["individual"][person]
        data["profiles"][name] = data["profiles"][person]
        del data["profiles"][person]
        json_methods.update_file(data, ctx.guild_id, full_data)
        await ctx.send("This individuals profile name has been changed!") 


@slash_command(name="admin_change_avatar", 
               description="Change your avatar!")
@slash_default_member_permission(interactions.Permissions.ADMINISTRATOR)
@slash_option(
    name="avi",
    description="Upload an image for your new avatar!",
    required=True,
    opt_type=OptionType.ATTACHMENT
)
@slash_option(
    name="person",
    description="Choose whos avatar you're changing!",
    required=True,
    opt_type=OptionType.STRING
)
async def admin_image_change(ctx: SlashContext, avi, person: str):
    data = json_methods.open_file(ctx.guild_id)
    full_data = data[1]
    data = data[0]
    if not person in data["individuals"]:
        embed = interactions.Embed(
        description=f"This profile does not exist!",
        color=0x7CB7D3)
        await ctx.send(embeds=embed)
    else:  
        data["individuals"][person]["image"] = avi
        json_methods.update_file(data, int(ctx.guild_id), full_data)
        await ctx.send("This individuals profile image has been changed!")

@slash_command(name="change_color", 
               description="Change your color!")
@slash_default_member_permission(interactions.Permissions.ADMINISTRATOR)
@slash_option(
    name="hex_code",
    description="Upload a hex code for the color you want!",
    required=True,
    opt_type=OptionType.STRING
)
async def color_change(ctx: SlashContext, hex_code):
    data = json_methods.open_file(ctx.guild_id)
    full_data = data[1]
    data = data[0]
    try:
        color = Color.from_hex(hex_code)
    except:
        await ctx.send("This is not a valid hex code. Please try again.")
    else:
        data["profiles"][data["individuals"][str(ctx.author.id)]["name"].lower()]["color"] = hex_code
        json_methods.update_file(data, int(ctx.guild_id), full_data)
        await ctx.send("Your color has been changed!")

@slash_command(name="help", 
               description="Get help!")
@slash_option(
    name="menu",
    description="Which menu would you like to access?",
    required=False,
    opt_type=OptionType.STRING
)
async def help_menu(ctx: SlashContext, menu="main"):
    file = open('help_menu.json')
    values = json.load(file)
    embed = interactions.Embed(
    description=values[menu.lower()],
    color=0x7CB7D3)
    await ctx.send(embeds=embed)
    
bot.start(token)