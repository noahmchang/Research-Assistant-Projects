import interactions
import asyncio
import os
bot = interactions.Client(token='REPLACE WITH TOKEN')

global waiting_list
waiting_list = []

public_button = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY,
    label="Public",
    custom_id="public"
)
private_button = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY,
    label="Private",
    custom_id="private"
)

def get_categories(ctx):
    for channel in ctx.guild.channels:
        if channel.name == "ASK HERE":
            ask_here_cat_id = channel.id
        elif channel.name == "ACTIVE QUESTIONS":
            public_cat_id = channel.id
        elif channel.name == "TUTORING":
            private_cat_id = channel.id
        elif channel.name == "ANSWERED QUESTIONS":
            answered_cat_id = channel.id
    return(ask_here_cat_id, public_cat_id, private_cat_id, answered_cat_id)

def tutor_check(ctx):
    for role in ctx.guild.roles:
        if role.name == "Tutor":
            tutor_role_id = role.id
    return (tutor_role_id in ctx.author.roles)

def get_relevant_roles(ctx):
    for role in ctx.guild.roles:
        if role.name == "Tutor":
            tutor_role_id = role.id
        elif role.name in ["@everyone","everyone"]:
            everyone_id = role.id
        elif role.name == "Student":
            student_id = role.id
        elif role.name == "Active Tutor":
            active_tutor_id = role.id
    return (tutor_role_id,everyone_id,student_id,active_tutor_id)

@bot.command(
    name="resolve",
    description="Use this command to close a channel.",
)

async def resolve(ctx):
    ask_here_cat_id, public_cat_id, private_cat_id, answered_cat_id = get_categories(ctx)
    # Fail if this isn't an open question
    if ctx.channel.parent_id == ask_here_cat_id:
        await ctx.send("You can't resolve a channel that isn't open yet!", ephemeral=True)
        return
    # Fail if the commander doesn't have the relevant permissions
    if (ctx.user.id != ctx.channel.topic) and not tutor_check(ctx):
        await ctx.send("You're not the author of this question!", ephemeral=True)
        return
    #Delete message history if this was a private channel
    if ctx.channel.parent_id == private_cat_id:
        await ctx.defer()
        try:
            await ctx.channel.purge(bulk=True,amount=50,check=lambda m: m.type not in {1, 2})
        except:
            print("Got upset while deleting messages! Hope I got them all!")
        await asyncio.sleep(5)
    # Try cooling down again
    tutor_role_id,everyone_id,student_id,active_tutor_id = get_relevant_roles(ctx)
    await ctx.channel.modify(parent_id=answered_cat_id,permission_overwrites=[interactions.api.models.misc.Overwrite(id=int(tutor_role_id),type=0,allow='0',deny='1024'),interactions.api.models.misc.Overwrite(id=int(student_id),type=0,allow='0',deny='1024'),interactions.api.models.misc.Overwrite(id=int(ctx.author.user.id),type=1,allow='0',deny='1024'),interactions.api.models.misc.Overwrite(id=int(everyone_id),type=0,allow='0',deny='1024')])
    await asyncio.sleep(600)

    await ctx.channel.modify(parent_id=ask_here_cat_id,topic='Claim this channel by typing a question!',name='👋ask-here',permission_overwrites=[interactions.api.models.misc.Overwrite(id=int(tutor_role_id),type=0,allow='1024',deny='2048'),interactions.api.models.misc.Overwrite(id=int(student_id),type=0,allow='1024',deny='2048'),interactions.api.models.misc.Overwrite(id=int(ctx.author.user.id),type=1,allow='1024',deny='2048'),interactions.api.models.misc.Overwrite(id=int(everyone_id),type=0,allow='0',deny='1024')])
    await ctx.send("""Have questions or need help with a problem or specific topic? Ask here and be patient for a response. Remember to: \n • Ask your question straight away, rather than asking \'can anyone help\' \n • **Include a screenshot or copy/paste the problem statement from Canvas** \n • If opening a private channel, include your code. **Do not include your code if opening a public channel.**\n • Include your IDLE and Gradescope output.\n • Format your code in a python codeblock with backticks, like this: https://i.imgur.com/ANnBqNQ.png \n • Remember to close the channel with `/resolve` when you're done.""", components=[public_button,private_button])
    
@bot.component("public")
async def public_button_response(ctx):
    ask_here_cat_id, public_cat_id, private_cat_id, answered_cat_id = get_categories(ctx)
    # Fail if this is already an open question
    if str(ctx.channel.parent_id) != str(ask_here_cat_id):
        await ctx.send("You can't open a question that's already opened!", ephemeral=True)
        return
    # Update category
    await ctx.defer()
    await ctx.channel.modify(parent_id=public_cat_id)
    await ctx.channel.modify(topic=str(ctx.author.user.id))
    if str(ctx.author.nick) != "None":
        await ctx.channel.modify(name=("💬"+str(ctx.author.nick)+"s-question"))
    else:
        await ctx.channel.modify(name=("💬"+str(ctx.author.user.username)+"s-question"))
    tutor_role_id,everyone_id,student_id,active_tutor_id = get_relevant_roles(ctx)
    await ctx.channel.modify(permission_overwrites=[interactions.api.models.misc.Overwrite(id=int(tutor_role_id),type=0,allow='1024',deny='0'),interactions.api.models.misc.Overwrite(id=int(everyone_id),type=0,deny='1024',allow='0'),interactions.api.models.misc.Overwrite(id=int(student_id),type=0,allow='1024',deny='0')])

    await ctx.send("Public Thread Claimed!", ephemeral=True)


@bot.component("private")
async def private_button_response(ctx):
    ask_here_cat_id, public_cat_id, private_cat_id, answered_cat_id = get_categories(ctx)
    # Fail if this is already an open question
    if str(ctx.channel.parent_id) != str(ask_here_cat_id):
        await ctx.send("You can't open a question that's already opened!", ephemeral=True)
        return
    # Update category and permissions
    await ctx.defer()
    await ctx.channel.modify(parent_id=private_cat_id)
    await ctx.channel.modify(topic=str(ctx.author.user.id))
    print(ctx.author.nick)
    if str(ctx.author.nick) != "None":
        await ctx.channel.modify(name=("💬"+str(ctx.author.nick)+"s-question"))
    else:
        await ctx.channel.modify(name=("💬"+str(ctx.author.user.username)+"s-question"))
    tutor_role_id,everyone_id,student_id,active_tutor_id = get_relevant_roles(ctx)
    await ctx.channel.modify(permission_overwrites=[interactions.api.models.misc.Overwrite(id=int(tutor_role_id),type=0,allow='1024',deny='0'),interactions.api.models.misc.Overwrite(id=int(everyone_id),type=0,deny='1024',allow='0'),interactions.api.models.misc.Overwrite(id=int(ctx.author.user.id),type=1,allow='1024',deny='0')])

    await ctx.send("Private Thread Claimed!", ephemeral=True)

@bot.command(name="register",description="Use this command to get in line for a tutor.")

async def register(ctx):
    tutor_role_id,everyone_id,student_id,active_tutor_id = get_relevant_roles(ctx)
    waiting_list.append(ctx.author)
    await ctx.send("You are in line! Your position is currently: {pos}. Sit tight! You'll be pinged when an <@&{tutor_id}> is ready for you.".format(pos=len(waiting_list),tutor_id=active_tutor_id))

@bot.command(name="next",description="Lets tutors notify the next student in line that they are ready.")

async def next(ctx):
    tutor_role_id,everyone_id,student_id,active_tutor_id = get_relevant_roles(ctx)
    if not tutor_check(ctx):
        await ctx.send("Only Tutors can use this command!", ephemeral=True)
        return
    if waiting_list == []:
        await ctx.send("There's no one in line right now! You can relax. ;)", ephemeral=True)
        return
    next_in_line = waiting_list[0]
    del waiting_list[0]
    await ctx.send("<@{next_id}>, the active tutor is ready for you! Join the waiting room voice channel, and they'll drag you into a private voice channel.".format(next_id=next_in_line.user.id))

@bot.command(name="signin",description="Lets tutors sign into their tutoring shift.")

async def signin(ctx):
    tutor_role_id,everyone_id,student_id,active_tutor_id = get_relevant_roles(ctx)
    if not tutor_check(ctx):
        await ctx.send("Only Tutors can use this command!", ephemeral=True)
        return
    if active_tutor_id in ctx.author.roles:
        await ctx.send("You're already signed in!", ephemeral=True)
        return
    await ctx.author.add_role(active_tutor_id)
    await ctx.send("Signed in!", ephemeral=True)

@bot.command(name="signout",description="Lets tutors sign out of their tutoring shift.")

async def signout(ctx):
    tutor_role_id,everyone_id,student_id,active_tutor_id = get_relevant_roles(ctx)
    if not tutor_check(ctx):
        await ctx.send("Only Tutors can use this command!", ephemeral=True)
        return
    if active_tutor_id not in ctx.author.roles:
        await ctx.send("You're already signed out!", ephemeral=True)
        return
    await ctx.author.remove_role(active_tutor_id)
    await ctx.send("Signed out!", ephemeral=True)

@bot.command(name="forceresolve",description="An admin command used to set up new Ask Here channels.")

async def forceresolve(ctx):
    tutor_role_id,everyone_id,student_id,active_tutor_id = get_relevant_roles(ctx)
    if not tutor_check(ctx):
        await ctx.send("Only Admins can use this command!", ephemeral=True)
        return
    # Update category and permissions
    ask_here_cat_id, public_cat_id, private_cat_id, answered_cat_id = get_categories(ctx)
    await ctx.channel.modify(parent_id=ask_here_cat_id,topic='Claim this channel by typing a question!',name='👋ask-here',permission_overwrites=[interactions.api.models.misc.Overwrite(id=int(tutor_role_id),type=0,allow='1024',deny='2048'),interactions.api.models.misc.Overwrite(id=int(student_id),type=0,allow='1024',deny='2048'),interactions.api.models.misc.Overwrite(id=int(ctx.author.user.id),type=1,allow='1024',deny='2048'),interactions.api.models.misc.Overwrite(id=int(everyone_id),type=0,allow='0',deny='1024')])
    await ctx.send("""Have questions or need help with a problem or specific topic? Ask here and be patient for a response. Remember to: \n • Ask your question straight away, rather than asking \'can anyone help\' \n • **Include a screenshot or copy/paste the problem statement from Canvas** \n • If opening a private channel, include your code. **Do not include your code if opening a public channel.**\n • Include your IDLE and Gradescope output.\n • Format your code in a python codeblock with backticks, like this: https://i.imgur.com/ANnBqNQ.png \n • Remember to close the channel with `/resolve` when you're done.""", components=[public_button,private_button])
    

# @bot.command(name="getinfo",description="foo")

# async def getinfo(ctx):
#     print(ctx.channel.permission_overwrites)
#     print(ctx.channel.permissions)
#     for channel in ctx.guild.channels:
#         if channel.name == "ASK HERE":
#             print(channel.name,channel.permissions)
#         elif channel.name == "ACTIVE QUESTIONS":
#             print(channel.name,channel.permissions)
#         elif channel.name == "TUTORING":
#             print(channel.name,channel.permissions)
#         elif channel.name == "ANSWERED QUESTIONS":
#             print(channel.name,channel.permissions)
#     await ctx.send("Info Sent!", ephemeral=True)
#     for role in ctx.guild.roles:
#         print(role,role.id)

bot.start()



