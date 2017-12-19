import discord, asyncio, string, datetime
import users, wordlist
from discord.ext import commands
from discord.ext.commands import Bot

commandPrefix = "!"
bot = commands.Bot(command_prefix=commandPrefix)
botToken = users.BOT_TOKEN
firstStartTime = datetime.datetime.now()
bingoDict = {}
timesDict = {}
sortedList = []
bingoWinners = {}
winnersSecret = {}


@bot.event
async def on_ready():
    print('Logged in as:\n{0} (ID: {0.id})\n'.format(bot.user))
    print(firstStartTime.strftime("Booted @ %H:%M on %d %B %Y\n"))
    print("Invite Link:\nhttps://discordapp.com/oauth2/authorize?client_id={}&scope=bot&permissions=8\n".format(
        bot.user.id))
    await bot.change_presence(game=discord.Game(name="{}".format(users.defaultStatus)))

## START COMMANDS ##

#@bot.command(pass_context=True)
#async def finduser(ctx, name:str):
    #namefromid = discord.utils.get(ctx.message.server.members, id=name).display_name
    #idfromname = discord.utils.find(lambda m: m.nick == name, ctx.message.server.members).id
    #print(namefromid)
    #print(idfromname)

@bot.command(pass_context=True)
async def timer(ctx, reason: str, timer: int):
    """Starts a timer and PMs user when done.  Reason must be in quotes."""
    user = ctx.message.author
    if not ctx.message.channel.is_private:
        await bot.delete_message(ctx.message)
    reasonStr = str(reason)
    await bot.send_message(user, "'{}' timer started.  PMing you in {} seconds.".format(reasonStr, timer))
    await asyncio.sleep(timer)
    await bot.send_message(user, "Your '{}' timer is up!".format(reasonStr))

@bot.command(pass_context=True)
async def uptime(ctx):
    """Returns when the bot last booted up."""
    user = ctx.message.author
    if not ctx.message.channel.is_private:
        await bot.delete_message(ctx.message)
    await bot.send_message(ctx.message.channel,
                              firstStartTime.strftime("I've been running since %I:%M %p on %d %B %Y."))
    await bot.send_message(ctx.message.channel, "That's {}! (Hours:Minutes:Seconds.Milliseconds)".format(datetime.datetime.now()-firstStartTime))

@bot.command(pass_context=True)
async def game(ctx, gamename):
    """Change the bot's status message."""
    user = ctx.message.author
    if not ctx.message.channel.is_private:
        await bot.delete_message(ctx.message)
    if ctx.message.author.id in users.WHITELIST or ctx.message.channel == users.testChannel:
        if len(gamename) >= 1:
            await bot.change_presence(game=discord.Game(name=gamename))
            await bot.say("Changed status to: `{}`".format(gamename))
        else:
            await bot.say("Needs more cowbell.")

@bot.command(pass_context=True, aliases=['sa'])
async def squareadd(ctx, square:str, dep:str):
    """Adds an item to the bingo tracker.  Usage "squareadd square department" or "sa square department"."""
    user = ctx.message.author
    if not ctx.message.channel.is_private:
        await bot.delete_message(ctx.message)
    if ctx.message.author.id in users.WHITELIST or ctx.message.channel == users.testChannel:
        timenow = datetime.datetime.now()
        if square.upper() in wordlist.LIST:
            square = wordlist.CONVERT[square.upper()]
            if dep.upper() in users.DEPARTMENTS:
                if square not in bingoDict:
                    bingoDict[square] = users.DEPARTMENTS[dep.upper()]
                    timesDict[square] = timenow.strftime("%I:%M %p")
                    await bot.send_message(ctx.message.channel, "Added `{}` from `{}` at {}.".format(square, users.DEPARTMENTS[dep.upper()],
                                                                              timenow.strftime("%I:%M %p")))
                    print(
                "{} added '{}' from '{}' at {}.\n-------".format(ctx.message.author, square, users.DEPARTMENTS[dep.upper()],
                                                             timenow.strftime("%H:%M")))
                else:
                    await bot.send_message(user, "`{}` was already claimed by `{}` at {}.".format(square, bingoDict[square], timesDict[square]))
            else:
                await bot.send_message(user, '`{}` is not a valid department.'.format(dep))
        else:
            await bot.send_message(user, "`{}` is not a valid square.".format(square))
    else:
        await bot.send_message(user, "You don't have permission to add to the tracker.")

@bot.command(pass_context=True, aliases=['srm'])
async def squareremove(ctx, square:str):
    """Removes an item from the bingo tracker.  Usage "squareremove square" or "srm square"."""
    user = ctx.message.author
    if not ctx.message.channel.is_private:
        await bot.delete_message(ctx.message)
    if ctx.message.author.id in users.WHITELIST or ctx.message.channel == users.testChannel:
        if square in bingoDict:
            del bingoDict[square]
            await bot.send_message(user, "Removed `{}` from the tracked list.".format(square))
        else:
            await bot.send_message(user, "`{}` is not currently being tracked.".format(square))
    else:
        await bot.send_message(user, "You don't have permission to remove tracked squares.")

@bot.command(pass_context=True, aliases=['sl','break'])
async def squarelist(ctx):
    """Sends a user a PM with the current tracked items."""
    user = ctx.message.author
    if not ctx.message.channel.is_private:
        await bot.delete_message(ctx.message)
    if not bingoDict:
        await bot.send_message(user, "Nothing in the tracker yet!")
    else:
        await bot.send_message(user, "Tonight's current squares:")
        for key, value in bingoDict.items():
            await asyncio.sleep(1.15)
            await bot.send_message(user, "`{}` by `{}` at {}.".format(key, value,timesDict.get(key)))

@bot.command(pass_context=True, aliases=['ssl','breaksorted'])
async def sortedsquarelist(ctx):
    """Sends a user a PM with the current tracked items in alphabetic order."""
    user = ctx.message.author
    if not ctx.message.channel.is_private:
        await bot.delete_message(ctx.message)
    if not bingoDict:
        await bot.send_message(user, "Nothing in the tracker yet!")
    else:
        for key in bingoDict.items():
            sortedList.append(key)
        sortedList.sort()
        for i, v in sortedList:
            await asyncio.sleep(1.15)
            await bot.send_message(user, "`{}` by `{}`".format(i,v))

@bot.command(pass_context=True)
async def squaresclear(ctx, confirm:str):
    """Erases all tracked items.  Usage "squaresclear YES"."""
    user = ctx.message.author
    if ctx.message.author.id in users.WHITELIST or ctx.message.channel == users.testChannel:
        if confirm == "YES":
            bingoDict.clear()
            await bot.send_message(ctx.message.channel, "{} CLEARED THE BINGO TRACKER".format(user.mention))
        elif confirm != "YES":
            await bot.send_message(ctx.message.channel,
                               "You must include the correct confirmation message to clear the bingo tracker!")
        else:
            await bot.send_message(ctx.message.channel,
                               "You must include the correct confirmation message to clear the bingo tracker!")
    else:
        if not ctx.message.channel.is_private:
            await bot.delete_message(ctx.message)
        await bot.send_message(user, "You don't have permission to clear the tracker.")

@bot.command(pass_context=True)
async def bingo(ctx):
    """Allows a user to call Bingo!"""
    user = ctx.message.author
    user_id = ctx.message.author.id
    if not ctx.message.channel.is_private:
        await bot.delete_message(ctx.message)
    if user_id in winnersSecret:
        await bot.send_message(user, "You've already called bingo tonight.  Ask a mod to remove you from the list if you called it in error.")
    else:
        await bot.send_message(ctx.message.channel, "Congrats {} on Bingo!".format(user.mention))
        timenow = datetime.datetime.now()
        bingoWinners[user.display_name] = timenow.strftime("%I:%M %p")
        winnersSecret[user_id] = timenow.strftime("%I:%M %p")
        print(">> {}({}) CALLED BINGO AT {} <<\n".format(user.display_name, user, timenow.strftime("%H:%M")))

@bot.command(pass_context=True)
async def rmbingo(ctx, susp:str):
    """Removes a user from the called bingo from the list using their nickname."""
    user = ctx.message.author
    if not ctx.message.channel.is_private:
        await bot.delete_message(ctx.message)
    if ctx.message.author.id in users.WHITELIST or ctx.message.channel == users.testChannel:
        if susp in bingoWinners:
            del bingoWinners[susp]
            susp_id = discord.utils.find(lambda m: m.nick == susp, ctx.message.server.members).id
            if susp_id in winnersSecret:
                del winnersSecret[susp_id]
            await bot.send_message(user,"`{}` was removed from the winners list.".format(susp))
        else:
            await bot.send_message(user, "`{}` was not found in the winners list.".format(susp))
    else:
        await bot.send_message(user, "You don't have permission to remove bingo winners.")

@bot.command(pass_context=True)
async def winnersclear(ctx, confirm:str):
    """Erases the current bingo winners.  Usage "winnersclear YES"."""
    user = ctx.message.author
    if ctx.message.author.id in users.WHITELIST or ctx.message.channel == users.testChannel:
        if confirm == "YES":
            bingoWinners.clear()
            winnersSecret.clear()
            await bot.send_message(ctx.message.channel, "{} CLEARED THE BINGO WINNERS".format(user.mention))
        elif confirm != "YES":
            await bot.send_message(ctx.message.channel,
                               "You must include the correct confirmation message to clear the bingo winners!")
        else:
            await bot.send_message(ctx.message.channel,
                               "You must include the correct confirmation message to clear the bingo winners!")
    else:
        if not ctx.message.channel.is_private:
            await bot.delete_message(ctx.message)
        await bot.send_message(user, "You don't have permission to clear the tracker.")

@bot.command(pass_context=True)
async def winners(ctx):
    """Lists the users that called bingo with times."""
    user = ctx.message.author
    if not ctx.message.channel.is_private:
        await bot.delete_message(ctx.message)
    if not bingoWinners:
        await bot.send_message(user, "No winners for {} yet!".format(firstStartTime.strftime("%d %B %Y")))
    else:
        await bot.send_message(user, "Bingo winners for {}:".format(firstStartTime.strftime("%d %B %Y")))
        #print(bingoWinners)
        for key, value in bingoWinners.items():
            await asyncio.sleep(1.15)
            await bot.send_message(user, "{} at {}.".format(key, value))

@bot.command(pass_context=True)
async def depts(ctx):
    """Lists the abbreviations for current Live PD departments."""
    user = ctx.message.author
    if not ctx.message.channel.is_private:
        await bot.delete_message(ctx.message)
    await bot.send_message(user, "Current active departments are (not case sensitive):")
    for key, value in users.DEPARTMENTS.items():
        await asyncio.sleep(1.15)
        await bot.send_message(user, "{} -> {}".format(key,value))
    await bot.send_message(user, "-- END --")

@bot.command(pass_context=True)
async def define(ctx, word:str):
    """Returns the offical Bingo definition of the square."""
    user = ctx.message.author
    if not ctx.message.channel.is_private:
        await bot.delete_message(ctx.message)
    if word == "list":
        await bot.send_message(user, "The full Bingo List can be found at http://realitytvbingo.com/bingolist")
        pass
    elif word.upper() in wordlist.LIST:
        word = wordlist.CONVERT[word.upper()]
        await bot.send_message(ctx.message.channel, "{} -> `{}`: {}".format(user.mention, word, wordlist.LIST[word.upper()]))
    else:
        await bot.send_message(ctx.message.channel, "`{}` is not an official square.".format(word))

# welcome's a user when they join the server.  only triggers on new join, not logout/login
@bot.event
async def on_member_join(member):
     await bot.send_message(member, "Welcome to the server!  Use `{}help` to get started!".format(commandPrefix))

@bot.command(pass_context=True, aliases=['quit', 'stop'])
async def exit(ctx):
    """Shuts the bot off.  Restarts are 1am daily.  >>RESTRICTED USE<<"""
    if not ctx.message.channel.is_private:
        await bot.delete_message(ctx.message)
    if ctx.message.author.id in users.WHITELIST or ctx.message.channel == users.testChannel:
        await bot.logout()

bot.run(botToken)