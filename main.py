import os, json_methods, json, random

import requests
from dotenv import load_dotenv

import interactions
from interactions import slash_command, SlashContext, OptionType, slash_option, slash_default_member_permission, Color, \
    Permissions

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

bot = interactions.Client()


@interactions.listen()
async def on_startup():
    print("Bot is ready!")


@slash_command(name="s",
               description="Say something out loud.")
@slash_option(
    name="text",
    description="Type some text for it to be said out in public!",
    required=True,
    opt_type=OptionType.STRING
)
@slash_option(
    name="img",
    description="Upload an image to be said out in public!",
    required=False,
    opt_type=OptionType.ATTACHMENT
)
@slash_option(
    name="chat",
    description="What public chat do you want to send your message in? (Default is the main channel)",
    required=False,
    opt_type=OptionType.STRING
)
async def say(ctx: SlashContext, text: str, img=None, chat="main"):
    data = json_methods.open_file(ctx.guild_id)
    full_data = data[1]
    data = data[0]

    # checks if an individual is muted
    if not data["profiles"][data["individuals"][str(ctx.author.id)]["name"].lower()]["settings"]["talk_perms"]:
        await ctx.send("You sadly do not have talk permissions! If you have any questions, talk to a server admin!")
        return

    # checks if an individual does not have an existing profile
    if not str(ctx.author.id) in data["individuals"]:
        embed = interactions.Embed(
            description="You do not have a user profile! Use /create_profile to make one!",
            color=0x7CB7D3)
        await ctx.send(embeds=embed)

    # runs if an individual has an existing profile
    else:
        send_channel = bot.get_channel(data["chat"]["channel"][chat]["id"])

        # creates embed with sent message
        embed = interactions.Embed(
            description=text,
            color=Color.from_hex(data["profiles"][data["individuals"][str(ctx.author.id)]["name"].lower()]["color"]))
        image = interactions.File(file=f"images/{data['individuals'][str(ctx.author.id)]['image']}",
                                  file_name="image.png")
        embed.set_author(name=data["individuals"][str(ctx.author.id)]["name"],
                         icon_url=f"attachment://image.png")
        if img:
            embed.set_image(img.url)

        # iterates through all the profiles to send in their specific chat
        for person in data["profiles"]:
            private_channel = bot.get_channel(data["profiles"][person]["hub"])
            if not chat in data["profiles"][person]["threads"]:
                new_thread = await private_channel.create_thread(name=chat, auto_archive_duration=10080)
                if data["profiles"][person]["id"] == ctx.author.id:
                    await new_thread.send(embeds=embed, files=image)
                data["profiles"][person]["threads"][chat] = new_thread.id
                json_methods.update_file(data, ctx.guild_id, full_data)
            if not data["profiles"][person]["id"] == ctx.author.id:
                thread = bot.get_channel(data["profiles"][person]["threads"][chat])
                await thread.send(embeds=embed, files=image)
        await send_channel.send(embeds=embed, files=image)
        await ctx.send(embeds=embed, files=image)


@slash_command(name="p",
               description="Ping someone!")
@slash_option(
    name="ping",
    description='Who would you like to ping with this message? (type "everyone" for everyone)',
    required=True,
    opt_type=OptionType.STRING
)
@slash_option(
    name="chat",
    description="What public channel would you like to ping this person in?",
    required=False,
    opt_type=OptionType.STRING
)
async def ping(ctx: SlashContext, ping: str, chat="main"):
    data = json_methods.open_file(ctx.guild_id)
    full_data = data[1]
    data = data[0]

    # checks if an individual is muted
    if not data["profiles"][data["individuals"][str(ctx.author.id)]["name"].lower()]["settings"]["talk_perms"]:
        await ctx.send("You sadly do not have talk permissions! If you have any questions, talk to a server admin!")
        return

    # checks if an individual does not have an existing profile
    if not (ping in data["profiles"] or ping == "everyone"):
        await ctx.send("You did not select a valid person to ping! Try again!")
        return

    # checks if the ping is for everyone
    if ping == "everyone":
        for person in data["profiles"]:
            private_channel = bot.get_channel(data["profiles"][person]["hub"])
            if not chat in data["profiles"][person]["threads"]:
                new_thread = await private_channel.create_thread(name=chat, auto_archive_duration=10080)
                if data["profiles"][person]["id"] == ctx.author.id:
                    await new_thread.send("<@" + str(data["profiles"][person]["id"]) + ">")
                data["profiles"][person]["threads"][chat] = new_thread.id
                json_methods.update_file(data, ctx.guild_id, full_data)

            # if the profile is not the pinger, pings them in their own channel
            if not data["profiles"][person]["id"] == ctx.author.id:
                thread = bot.get_channel(data["profiles"][person]["threads"][chat])
                await thread.send(embeds="<@" + str(data["profiles"][person]["id"]) + ">")
    else:

        # pings the specific person
        thread = bot.get_channel(data["profiles"][ping]["threads"][chat.lower()])
        await thread.send("<@" + str(data["profiles"][ping]["name"]["id"]) + ">")


@slash_command(name="d",
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
    full_data = data[1]
    data = data[0]

    # checks if an individual is muted
    if not data["profiles"][data["individuals"][str(ctx.author.id)]["name"].lower()]["settings"]["talk_perms"]:
        await ctx.send("You sadly do not have talk permissions! If you have any questions, talk to a server admin!")
        return

    # checks if an individual does not have an existing profile
    if not str(ctx.author.id) in data["individuals"]:
        embed = interactions.Embed(
            description="You do not have a user profile! Use /create_profile to make one!",
            color=0x7CB7D3)
        await ctx.send(embeds=embed)
    else:
        embed = interactions.Embed(
            description=text,
            color=Color.from_hex(data["profiles"][data["individuals"][str(ctx.author.id)]["name"].lower()]["color"]))

        # checks if the specified chat is an individual
        if dm.lower() in data["chat"]["individual"]:
            image = interactions.File(file=f"images/{data['individuals'][str(ctx.author.id)]['image']}",
                                      file_name="image.png")
            embed.set_author(name=data["individuals"][str(ctx.author.id)]["name"],
                             icon_url="attachment://image.png")

            # creates a thread for the specific dm if there is not one already
            if not dm.lower() in data["profiles"][data["individuals"][str(ctx.author.id)]["name"]]["threads"]:
                self_channel = bot.get_channel(data["profiles"][data["individuals"][str(ctx.author.id)]["name"]]["dm"])
                self_thread = await self_channel.create_thread(name=dm, auto_archive_duration=10080)
                data["profiles"][data["individuals"][str(ctx.author.id)]["name"]]["threads"][
                    dm.lower()] = self_thread.id
                json_methods.update_file(data, ctx.guild_id, full_data)
                thread = bot.get_channel(
                    data["profiles"][data["individuals"][str(ctx.author.id)]["name"]]["threads"][dm.lower()])
                sent_message = await thread.send(embeds=embed, files=image)

                # ghost pings the sender so they can easily access the new chat
                if data["profiles"][data["individuals"][str(ctx.author.id)]["name"]]["settings"]["dm_ping"]:
                    ghost_ping = await sent_message.reply("<@" + str(data["profiles"][dm.lower()]["id"]) + ">")
                    await ghost_ping.delete()

            # goes through all the profiles to send the message to the other person
            for person in data["profiles"]:
                if person.lower() == dm.lower() and not person.lower() == data["individuals"][str(ctx.author.id)][
                    "name"]:
                    dm_channel = bot.get_channel(data["profiles"][person]["dm"])

                    # creates a new thread if needed for this dm
                    if not dm.lower() in data["profiles"][person]["threads"]:
                        new_thread = await dm_channel.create_thread(
                            name=data["individuals"][str(ctx.author.id)]["name"], auto_archive_duration=10080)
                        data["profiles"][person]["threads"][dm.lower()] = new_thread.id
                        json_methods.update_file(data, ctx.guild_id, full_data)
                    thread = bot.get_channel(data["profiles"][person]["threads"][dm.lower()])
                    sent_message = await thread.send(embeds=embed, files=image)

                    # ghost pings the individual to replicate real dms if desired
                    if data["profiles"][person]["settings"]["dm_ping"]:
                        ghost_ping = await sent_message.reply("<@" + str(data["profiles"][person]["id"]) + ">")
                        await ghost_ping.delete()
            await ctx.send(embeds=embed, files=image)

        # checks if the specified chat is a group chat
        elif dm.lower() in data["chat"]["group"]:
            if not data["individuals"][str(ctx.author.id)]["name"] in data["chat"]["group"][dm.lower()]["members"]:
                await ctx.send("You're not in this group!")
                return
            image = interactions.File(f"images/{data['individuals'][str(ctx.author.id)]['image']}")
            embed.set_author(name=data["individuals"][str(ctx.author.id)]["name"],
                             icon_url=f"attachment://image.png")
            if data["chat"]["group"][dm.lower()]["image"]:
                embed.set_thumbnail(data["chat"]["group"][dm.lower()]["image"])

            # creates a thread for the specific dm if there is not one already
            if not dm.lower() in data["profiles"][data["individuals"][str(ctx.author.id)]["name"]]["threads"]:
                self_channel = bot.get_channel(data["profiles"][data["individuals"][str(ctx.author.id)]["name"]]["dm"])
                self_thread = await self_channel.create_thread(name=dm, auto_archive_duration=10080)
                data["profiles"][data["individuals"][str(ctx.author.id)]["name"]]["threads"][
                    dm.lower()] = self_thread.id
                json_methods.update_file(data, ctx.guild_id, full_data)
                thread = bot.get_channel(
                    data["profiles"][data["individuals"][str(ctx.author.id)]["name"]]["threads"][dm.lower()])
                await thread.send(embeds=embed, files=image)

            # checks all profiles to send to those in the group
            for person in data["profiles"]:
                if person.lower() in data["chat"]["group"][dm.lower()]["members"] and not person.lower() == \
                                                                                          data["individuals"][
                                                                                              str(ctx.author.id)][
                                                                                              "name"]:

                    # creates a new thread if needed for this dm
                    if not dm.lower() in data["profiles"][person]["threads"]:
                        dm_channel = bot.get_channel(data["profiles"][person]["dm"])
                        new_thread = await dm_channel.create_thread(name=dm, auto_archive_duration=10080)
                        data["profiles"][person]["threads"][dm.lower()] = new_thread.id
                        json_methods.update_file(data, ctx.guild_id, full_data)
                    thread = bot.get_channel(data["profiles"][person]["threads"][dm.lower()])
                    sent_message = await thread.send(embeds=embed, files=image)

                    # ghost pings the individual to replicate real dms if desired
                    if data["profiles"][person]["settings"]["dm_ping"]:
                        ghost_ping = await sent_message.reply("<@" + str(data["profiles"][person]["id"]) + ">")
                        await ghost_ping.delete()
            await ctx.send(embeds=embed, files=image)

        # checks if the chat does not exist
        else:
            embed = interactions.Embed(
                description="This chat does not exist!",
                color=Color.from_hex(
                    data["profiles"][data["individuals"][str(ctx.author.id)]["name"].lower()]["color"]))
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
    required=False,
    opt_type=OptionType.ATTACHMENT
)
async def profile(ctx: SlashContext, name: str, avi=None):
    data = json_methods.open_file(ctx.guild_id)
    full_data = data[1]
    data = data[0]

    banned = open('banned_names.json')
    banned_names = json.load(banned)

    # if the desired name is banned
    if name in banned_names:
        await ctx.send("Sorry, you cannot name your profile this, please choose another name!")
        return

    # if there is no main channel, creates one
    if not "main" in data["chat"]["channel"]:
        # prevents people from speaking in the main channel (intended to be only talked in my profiles)
        po = interactions.PermissionOverwrite(id=ctx.guild.id, type=0, deny=Permissions.SEND_MESSAGES)
        category = await ctx.guild.create_channel(channel_type=4, name="global channels")
        data["chat"]["channel"]["public_category"] = {
            "id": category.id
        }
        channel = await ctx.guild.create_channel(channel_type=0, name="main-chat",
                                                 permission_overwrites=po,
                                                 category=data["chat"]["channel"]["public_category"]["id"])
        data["chat"]["channel"]["main"] = {
            "id": channel.id
        }
        json_methods.update_file(data, ctx.guild_id, full_data)

    # if the profile creater doesn't have a profile yet, and the name is not taken by another profile or a group chat
    if not str(ctx.author.id) in data["individuals"] and not name.lower() in data["profiles"] and not name.lower() in \
                                                                                                      data["chat"][
                                                                                                          "group"]:
        file = open('colors.json')
        values = json.load(file)

        # if there is an avatar provided, uses it
        if avi:
            image = requests.get(avi.url).content
            with open(f"images/{ctx.guild.id}a{ctx.author.id}.jpg", "wb") as handler:
                handler.write(image)

            data["individuals"][ctx.author.id] = {
                "name": name,
                "image": f"{ctx.guild.id}a{ctx.author.id}.jpg"
            }

        # if there is not an avatar provided, uses default
        else:
            data["individuals"][ctx.author.id] = {
                "name": name,
                "image": f"default.png"
            }

        # prevents everyone but this specific individual from seeing the individual channels
        po = interactions.PermissionOverwrite(id=ctx.guild.id, type=0)
        po.add_denies(interactions.Permissions.VIEW_CHANNEL)
        pa = interactions.PermissionOverwrite(id=ctx.author.id, type=1)
        pa.add_allows(interactions.Permissions.VIEW_CHANNEL)
        if not "individual_category" in data["chat"]["channel"]:
            category = await ctx.guild.create_channel(channel_type=4, name="individual channels")
            data["chat"]["channel"]["individual_category"] = {
                "id": category.id
            }

        # creates hub and dm channels
        channel = await ctx.guild.create_channel(channel_type=0, name=f"{name}-hub", permission_overwrites=[po, pa],
                                                 category=data["chat"]["channel"]["individual_category"]["id"])
        dm_channel = await ctx.guild.create_channel(channel_type=0, name=f"{name}-DM", permission_overwrites=[po, pa],
                                                    category=data["chat"]["channel"]["individual_category"]["id"])

        # adds profile information to the stored JSON file
        data["profiles"][name.lower()] = {
            "id": ctx.author.id,
            "color": random.choice(list(values.values())),
            "hub": channel.id,
            "dm": dm_channel.id,
            "threads": {},
            "journal": None,
            "settings": {
                "dm_ping": data["settings"]["dm_ping"],
                "name_change": data["settings"]["name_change"],
                "image_change": data["settings"]["image_change"],
                "color_change": data["settings"]["color_change"],
                "talk_perms": True,
            }
        }

        # creates a journal channel if enabled
        if data["settings"]["journal"]:
            journal_channel = await ctx.guild.create_channel(channel_type=0, name=f"{name}-journal",
                                                             permission_overwrites=[po, pa],
                                                             category=data["chat"]["channel"]["journal_category"]["id"])
            data["profiles"][name.lower()]["journal"] = journal_channel.id
        data["chat"]["individual"][name.lower()] = {
            "dm": dm_channel.id
        }
        json_methods.update_file(data, ctx.guild_id, full_data)
        await ctx.send("Your profile has been created!")
    else:

        # if the profile creater already has a user profile
        if str(ctx.author.id) in data["individuals"]:
            embed = interactions.Embed(
                description="You already have a user profile!",
                color=Color.from_hex(data["profiles"][data]["color"]))

        # if the name is already taken by another user
        elif name.lower() in data["profiles"]:
            embed = interactions.Embed(
                description="This name is already taken! Please choose another name.",
                color=0x7CB7D3)

        # if the name is already taken by a group chat
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
    banned = open('banned_names.json')
    banned_names = json.load(banned)

    # if the name is banned
    if name in banned_names:
        await ctx.send("Sorry, you cannot name your profile this, please choose another name!")
        return

    # if the user does not have permission to change their name
    if not data["settings"]["name_change"] or not \
    data["profiles"][data["individuals"][str(ctx.author.id)]["name"]]["settings"]["name_change"]:
        await ctx.send("Sorry, you do not have permission to change your name!")
        return

    # checks if an individual does not have an existing profile
    if not str(ctx.author.id) in data["individuals"]:
        embed = interactions.Embed(
            description="You do not have a user profile! Use /create_profile to make one!",
            color=0x7CB7D3)
        await ctx.send(embeds=embed)

    # if the name is already taken by another user
    elif name.lower() in data["profiles"]:
        embed = interactions.Embed(
            description="This name is already taken! Please choose another name.",
            color=0x7CB7D3)
        await ctx.send(embeds=embed)

    # if the name is already taken by another group
    elif name.lower() in data["chat"]["group"]:
        embed = interactions.Embed(
            description="This name is already the name of a group chat! Please choose another name.",
            color=Color.from_hex(data["profiles"][data["individuals"][str(ctx.author.id)]["name"].lower()]["color"]))
        await ctx.send(embeds=embed)

    # if the name change is allowed
    else:

        # updates all data using the old name to the new name
        old_name = data["individuals"][str(ctx.author.id)]["name"]
        data["chat"]["individual"][name] = data["chat"]["individual"][old_name]
        del data["chat"]["individual"][old_name]
        data["individuals"][str(data["profiles"][data["individuals"][str(ctx.author.id)]["name"]]["id"])]["name"] = name
        data["profiles"][name] = data["profiles"][old_name]
        del data["profiles"][old_name]

        # updates group chats with the new profile name
        for group in data["chat"]["group"]:
            if data["individuals"][str(ctx.author.id)]["name"] in data["chat"]["group"][group]["members"]:
                data["chat"]["group"][group]["members"][data["chat"]["group"][group]["members"].index(
                    data["individuals"][str(ctx.author.id)]["name"])] = name

        # updates all DM threads with the new profile name
        for prof in data["profiles"]:
            if old_name in data["profiles"][prof]["threads"]:
                data["profiles"]["threads"][name] = data["profiles"]["threads"][old_name]
                del data["profiles"]["threads"][old_name]
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
    if not data["settings"]["image_change"] or not \
    data["profiles"][data["individuals"][str(ctx.author.id)]["name"]]["settings"]["image_change"]:
        await ctx.send("Sorry, you do not have permission to change your profile's image!")
        return

    # checks if an individual does not have an existing profile
    if not str(ctx.author.id) in data["individuals"]:
        embed = interactions.Embed(
            description=f"You do not have a user profile! Use /create_profile to make one!",
            color=0x7CB7D3)
        await ctx.send(embeds=embed)
    else:
        # gets the uploaded image, saves it, then sets it as the profile picture
        image = requests.get(avi.url).content
        with open(f"images/{ctx.guild.id}a{ctx.author.id}.jpg", "wb") as handler:
            handler.write(image)
        data["individuals"][str(ctx.author.id)]["image"] = f"{ctx.guild.id}a{ctx.author.id}.jpg"
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

    # if the channel has already been assigned
    if channel_name.lower() in data["chat"]["channel"]:
        embed = interactions.Embed(
            description="This channel has already been assigned!",
            color=0x7CB7D3)
        await ctx.send(embeds=embed)

    # assigns this channel to be spoken
    else:
        data["chat"]["channel"][channel_name.lower()] = {
            "id": ctx.channel.id,
        }
        json_methods.update_file(data, ctx.guild_id, full_data)
        await ctx.send("This channel has been assigned as a public communication channel!")


@slash_command(name="create_channel",
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

    # if the channel has already been assigned
    if channel_name.lower() in data["chat"]["channel"]:
        embed = interactions.Embed(
            description="This channel name already exists!",
            color=0x7CB7D3)
        await ctx.send(embeds=embed)
    else:

        # if there is no category for public channels yet, creates it
        if not "public_category" in data["chat"]["channel"]:
            category = await ctx.guild.create_channel(channel_type=4, name="individual channels")
            data["chat"]["channel"]["public_category"] = {
                "id": category.id
            }

        # creates the new public channel
        po = interactions.PermissionOverwrite(id=ctx.guild.id, type=0)
        po.add_denies(interactions.Permissions.SEND_MESSAGES)
        channel = await ctx.guild.create_channel(channel_type=0, name=channel_name, permission_overwrites=po,
                                                 category=data["chat"]["channel"]["public_category"]["id"])
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

    # if the group name is already taken
    if group_name.lower() in data["chat"]["group"]:
        embed = interactions.Embed(
            description="This group name has already been assigned!",
            color=0x7CB7D3)
        await ctx.send(embeds=embed)

    # if the group name is a profiles name
    elif group_name.lower() in data["profiles"]:
        embed = interactions.Embed(
            description="This is already somebodys name! Please do not use it.",
            color=0x7CB7D3)
        await ctx.send(embeds=embed)
    else:

        # adds members and group thumbnail
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

    # if the profile is already in the group
    if person_name.lower() in data["chat"]["group"][channel_name.lower()]["members"]:
        embed = interactions.Embed(
            description="This profile is already in the group!",
            color=0x7CB7D3)
        await ctx.send(embeds=embed)

    # if the profile attempting to be added does not already exist
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
async def toggle_journal(ctx: SlashContext, toggle):
    data = json_methods.open_file(ctx.guild_id)
    full_data = data[1]
    data = data[0]

    # if the journal setting is currently off
    if toggle:
        if not "journal_category" in data["chat"]["channel"]:
            category = await ctx.guild.create_channel(channel_type=4, name="journals")
            data["chat"]["channel"]["journal_category"] = {
                "id": category.id
            }
        pa = interactions.PermissionOverwrite(id=ctx.author.id, type=1)
        pa.add_allows(interactions.Permissions.VIEW_CHANNEL)
        for person in data["profiles"]:
            if data["profiles"][person.lower()]["journal"] is None:
                po = interactions.PermissionOverwrite(id=ctx.guild.id, type=0)
                po.add_denies(interactions.Permissions.VIEW_CHANNEL)
                journal_channel = await ctx.guild.create_channel(channel_type=0, name=f"{person}-journal",
                                                                 permission_overwrites=[po, pa], category=
                                                                 data["chat"]["channel"]["journal_category"]["id"])
                data["profiles"][person.lower()]["journal"] = journal_channel.id
        data["settings"]["journal"] = True

    # if the journal setting is currently on
    else:
        data["settings"]["journal"] = False
    json_methods.update_file(data, ctx.guild_id, full_data)
    await ctx.send("This setting has been changed!")


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
    banned = open('banned_names.json')
    banned_names = json.load(banned)

    # if name is banned
    if name in banned_names:
        await ctx.send("Sorry, you cannot name this profile this name, please choose another name!")
        return

    # if the profile does not exist
    if not person in data["profiles"]:
        embed = interactions.Embed(
            description="This profile does not exist!",
            color=0x7CB7D3)
        await ctx.send(embeds=embed)

    # if the profile name is already taken
    elif name.lower() in data["profiles"]:
        embed = interactions.Embed(
            description="This name is already taken! Please choose another name.",
            color=0x7CB7D3)
        await ctx.send(embeds=embed)

    # if the profile name is already the name of a group chat
    elif name.lower() in data["chat"]["group"]:
        embed = interactions.Embed(
            description="This name is already the name of a group chat! Please choose another name.",
            color=0x7CB7D3)
        await ctx.send(embeds=embed)

    # if the profile name change is successful
    else:
        data["chat"]["individual"][name] = data["chat"]["individual"][person]
        del data["chat"]["individual"][person]
        data["individuals"][str(data["profiles"][person]["id"])]["name"] = name
        data["profiles"][name] = data["profiles"][person]
        del data["profiles"][person]
        for group in data["chat"]["group"]:
            if person in data["chat"]["group"][group]["members"]:
                data["chat"]["group"][group]["members"][data["chat"]["group"][group]["members"].index(person)] = name
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

    # if the profile does not exist
    if not person in data["individuals"]:
        embed = interactions.Embed(
            description="This profile does not exist!",
            color=0x7CB7D3)
        await ctx.send(embeds=embed)

    # if the profile does exist
    else:
        image = requests.get(avi.url).content
        with open(f"images/{ctx.guild.id}a{ctx.author.id}.jpg", "wb") as handler:
            handler.write(image)
        data["individuals"][str(ctx.author.id)]["image"] = f"{ctx.guild.id}a{ctx.author.id}.jpg"
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

    # if the person doesn't have permission to change their profiles color
    if not data["settings"]["color_change"] or not \
    data["profiles"][data["individuals"][str(ctx.author.id)]["name"]]["settings"]["color_change"]:
        await ctx.send("Sorry, you do not have permission to change your profile's color!")
        return

    # tries changing the color to see if its valid
    try:
        color = Color.from_hex(hex_code)
    except:
        await ctx.send("This is not a valid hex code. Please try again.")

    # changes the color if the color is valid
    else:
        data["profiles"][data["individuals"][str(ctx.author.id)]["name"].lower()]["color"] = hex_code
        json_methods.update_file(data, int(ctx.guild_id), full_data)
        await ctx.send("Your color has been changed!")


@slash_command(name="admin_change_color",
               description="Change an individuals color!")
@slash_default_member_permission(interactions.Permissions.ADMINISTRATOR)
@slash_option(
    name="hex_code",
    description="Upload a hex code for the color you want!",
    required=True,
    opt_type=OptionType.STRING
)
@slash_option(
    name="profile",
    description="Choose whos color you're changing!",
    required=True,
    opt_type=OptionType.STRING
)
async def admin_color_change(ctx: SlashContext, hex_code, profile: str):
    data = json_methods.open_file(ctx.guild_id)
    full_data = data[1]
    data = data[0]

    # tries changing the color to see if its valid
    try:
        color = Color.from_hex(hex_code)
    except:
        await ctx.send("This is not a valid hex code. Please try again.")

    # changes the color if the color is valid
    else:
        data["profiles"][data["individuals"][data["profiles"][profile]["name"]]["name"]]["color"] = hex_code
        json_methods.update_file(data, int(ctx.guild_id), full_data)
        await ctx.send("This individuals color has been changed!")


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

    # checks if the menu is valid
    try:
        testing = values[menu.lower()]
    except:
        await ctx.send("This is not a valid menu. Please try again.")
    else:

        # displays the specific menu asked for
        embed = interactions.Embed(
            description=values[menu.lower()],
            color=0x7CB7D3)
        await ctx.send(embeds=embed)


@slash_command(name="settings",
               description="Change your settings!")
@slash_option(
    name="setting",
    description="Which setting would you like to change?",
    required=False,
    opt_type=OptionType.STRING
)
@slash_option(
    name="value",
    description="What would you like to set this setting to?",
    required=False,
    opt_type=OptionType.BOOLEAN
)
async def change_settings(ctx: SlashContext, setting: str, value: bool):
    data = json_methods.open_file(ctx.guild_id)
    data = data[0]

    # if the setting is an actual setting, changes it
    if setting in data["profiles"][data["individuals"][str(ctx.author.id)]["name"]["settings"]]:
        data["profiles"][data["individuals"][str(ctx.author.id)]["name"]["settings"]] = value
        await ctx.send("This setting has been changed!")
    else:
        await ctx.send("This is not a valid setting! PLease try again!")


@slash_command(name="admin_settings",
               description="Change your settings!")
@slash_default_member_permission(interactions.Permissions.ADMINISTRATOR)
@slash_option(
    name="setting",
    description="Which setting would you like to change?",
    required=False,
    opt_type=OptionType.STRING
)
@slash_option(
    name="value",
    description="What would you like to set this setting to?",
    required=False,
    opt_type=OptionType.BOOLEAN
)
async def change_admin_settings(ctx: SlashContext, setting: str, value: bool):
    data = json_methods.open_file(ctx.guild_id)
    full_data = data[1]
    data = data[0]

    # if the setting is an actual setting, changes it
    if setting in data["settings"]:

        # if the settings is the journal and its being added, adds the journal
        if setting == "journal" and value == True:
            if not "journal_category" in data["chat"]["channel"]:
                category = await ctx.guild.create_channel(channel_type=4, name="journals")
                data["chat"]["channel"]["journal_category"] = {
                    "id": category.id
                }
            pa = interactions.PermissionOverwrite(id=ctx.author.id, type=1)
            pa.add_allows(interactions.Permissions.VIEW_CHANNEL)
            for person in data["profiles"]:

                # if the profile currently does not have a journal
                if data["profiles"][person.lower()]["journal"] == None:
                    po = interactions.PermissionOverwrite(id=ctx.guild.id, type=0)
                    po.add_denies(interactions.Permissions.VIEW_CHANNEL)
                    journal_channel = await ctx.guild.create_channel(channel_type=0, name=f"{person}-journal",
                                                                     permission_overwrites=[po, pa], category=
                                                                     data["chat"]["channel"]["journal_category"]["id"])
                    data["profiles"][person.lower()]["journal"] = journal_channel.id
        data["settings"][setting] = value
        json_methods.update_file(data, ctx.guild_id, full_data)
        await ctx.send("This setting has been changed!")
    else:
        await ctx.send("This is not a valid setting! Please try again!")


bot.start(token)
