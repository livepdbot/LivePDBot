import discord, asyncio, string, datetime
import users, wordlist
from discord.ext import commands
from discord.ext.commands import Bot

commandPrefix = "!"
bot = commands.Bot(command_prefix=commandPrefix, pm_help=True)
botToken = users.BOT_TOKEN
firstStartTime = datetime.datetime.now()
bingoDict = {}
timesDict = {}
sortedList = []
bingoWinners = {}
winnersSecret = {}
testbingoDict = {}
testtimesDict = {}
testbingoWinners = {}
testwinnersSecret = {}
testsortedList = []


@bot.event
async def on_ready():
    print('Logged in as:\n{0} (ID: {0.id})\n'.format(bot.user))
    print(firstStartTime.strftime("Booted @ %H:%M on %d %B %Y\n"))
    print("Invite Link:\nhttps://discordapp.com/oauth2/authorize?client_id={}&scope=bot&permissions=8\n".format(
        bot.user.id))
    await bot.change_presence(game=discord.Game(name="{}".format(users.defaultStatus)))
    welcome = await bot.send_message(discord.Object(id=users.testChannel), "Bot is up.")
    await asyncio.sleep(5)
    await bot.delete_message(welcome)
    #global updatelist
    #updatelist = 0

## START COMMANDS ##

#@bot.command(pass_context=True)
#async def finduser(ctx, name:str):
    #namefromid = discord.utils.get(ctx.message.server.members, id=name).display_name
    #idfromname = discord.utils.find(lambda m: m.nick == name, ctx.message.server.members).id
    #print(namefromid)
    #print(idfromname)


# async def updatelist():
#     global updatelist
#     if updatelist == 0:
#         sortedList.clear()
#         breakList = []
#         if not bingoDict:
#             updatemessage = await bot.send_message(discord.Object(id="392187521796145162"), "Nothing in the tracker yet!")
#         elif bingoDict:
#             for key, value in bingoDict.items():
#                 sortedList.append(key)
#             sortedList.sort()
#             breakList = ", ".join(sortedList)
#             updatemessage = await bot.send_message(discord.Object(id="392187521796145162"), "Current squares: {}.".format(breakList))
#         updatelist = 1
#     else:
#         sortedList.clear()
#         breakList = []
#         for key, value in bingoDict.items():
#             sortedList.append(key)
#         sortedList.sort()
#         breakList = ", ".join(sortedList)
#         await bot.edit_message(updatemessage, breakList)

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
    if ctx.message.channel == users.testChannel:
        timenow = datetime.datetime.now()
        if square.upper() in wordlist.LIST:
            square = wordlist.CONVERT[square.upper()]
            if dep.upper() in users.DEPARTMENTS:
                if square not in bingoDict:
                    testbingoDict[square] = users.DEPARTMENTS[dep.upper()]
                    testtimesDict[square] = timenow.strftime("%I:%M %p")
                    await bot.send_message(ctx.message.channel,
                                           "{} added `{}` from `{}` at {}.".format(user.mention, square,
                                                                                   users.DEPARTMENTS[dep.upper()],
                                                                                   timenow.strftime("%I:%M %p")))
                    print(
                        "{} added '{}' from '{}' at {}.\n-------".format(ctx.message.author, square,
                                                                         users.DEPARTMENTS[dep.upper()],
                                                                         timenow.strftime("%H:%M")))
                    #updatelist()
                else:
                    await bot.send_message(user,
                                           "`{}` was already claimed by `{}` at {}.".format(square, testbingoDict[square],
                                                                                            testtimesDict[square]))
            else:
                await bot.send_message(user,
                                       '`{}` is not a valid department.  Check `!depts` for valid departments.'.format(
                                           dep))
        else:
            await bot.send_message(user,
                                   "`{}` is not a valid square. Check `!define list` for valid squares.".format(square))
    elif ctx.message.author.id in users.WHITELIST:
        timenow = datetime.datetime.now()
        if square.upper() in wordlist.LIST:
            square = wordlist.CONVERT[square.upper()]
            if dep.upper() in users.DEPARTMENTS:
                if square not in bingoDict:
                    bingoDict[square] = users.DEPARTMENTS[dep.upper()]
                    timesDict[square] = timenow.strftime("%I:%M %p")
                    await bot.send_message(ctx.message.channel, "{} added `{}` from `{}` at {}.".format(user.mention, square, users.DEPARTMENTS[dep.upper()],
                                                                              timenow.strftime("%I:%M %p")))
                    print(
                "{} added '{}' from '{}' at {}.\n-------".format(ctx.message.author, square, users.DEPARTMENTS[dep.upper()],
                                                             timenow.strftime("%H:%M")))
                    #updatelist()
                else:
                    await bot.send_message(user, "`{}` was already claimed by `{}` at {}.".format(square, bingoDict[square], timesDict[square]))
            else:
                await bot.send_message(user, '`{}` is not a valid department.  Check `!depts` for valid departments.'.format(dep))
        else:
            await bot.send_message(user, "`{}` is not a valid square. Check `!define list` for valid squares.".format(square))
    else:
        await bot.send_message(user, "You don't have permission to add to the tracker.")

@bot.command(pass_context=True, aliases=['find'])
async def search(ctx, word:str):
    """Searches the square list for squares matching the search term(s)."""
    user = ctx.message.author
    if not ctx.message.channel.is_private:
        await bot.delete_message(ctx.message)
    word = word.upper()
    searchList = []
    foundList = []
    returnList = []
    i = 0
    count = 0
    searchList = list(wordlist.LIST.keys())
    while i < len(searchList):
        if searchList[i].find(word) != -1:
            searchList[i] = wordlist.CONVERT[searchList[i]]
            foundList.append(searchList[i])
            returnList = ", ".join(foundList)
            i = i + 1
            count = count +1
        else:
            i = i + 1
    if count == 0:
        await bot.send_message(user, "No matches found.")
    elif count >= 1:
        await bot.send_message(user, "Found the following {} square matches: {}.".format(count, returnList))

@bot.command(pass_context=True, aliases=['dfind'])
async def deptsearch(ctx, dept:str):
    """Searches the department list for department(s) matching the search term."""
    user = ctx.message.author
    if not ctx.message.channel.is_private:
        await bot.delete_message(ctx.message)
    dept = dept.upper()
    deptList = []
    foundDeptList = []
    returnDeptList = []
    j = 0
    fdept = 0
    deptList = list(users.DEPARTMENTS.values())
    while j < len(deptList):
        deptListUpper = deptList[j].upper()
        if deptListUpper.find(dept) != -1:
            foundDeptList.append(deptList[j])
            returnDeptList = ", ".join(foundDeptList)
            j = j + 1
            fdept = fdept + 1
        else:
            j = j + 1
    if fdept == 0:
        await bot.send_message(user, "No matching department.")
    if fdept >= 1:
        await bot.send_message(user, "Found the following department(s): {}.".format(returnDeptList))

@bot.command(pass_context=True, aliases=['srm'])
async def squareremove(ctx, square:str):
    """Removes an item from the bingo tracker.  Usage "squareremove square" or "srm square"."""
    user = ctx.message.author
    if not ctx.message.channel.is_private:
        await bot.delete_message(ctx.message)
    if ctx.message.channel == users.testChannel:
        if square in testbingoDict:
            del testbingoDict[square]
            await bot.send_message(user, "Removed `{}` from the tracked list.".format(square))
        else:
            await bot.send_message(user, "`{}` is not currently being tracked.".format(square))
    elif ctx.message.author.id in users.WHITELIST:
        if square in bingoDict:
            del bingoDict[square]
            await bot.send_message(user, "Removed `{}` from the tracked list.".format(square))
        else:
            await bot.send_message(user, "`{}` is not currently being tracked.".format(square))
    else:
        await bot.send_message(user, "You don't have permission to remove tracked squares.")

@bot.command(pass_context=True, aliases=['sl'])
async def squarelist(ctx):
    """Sends a user a PM with the current tracked items."""
    user = ctx.message.author
    if not ctx.message.channel.is_private:
        await bot.delete_message(ctx.message)
    if ctx.message.channel == users.testChannel:
        if not testbingoDict:
            await bot.send_message(user, "Nothing in the tracker yet!")
        else:
            await bot.send_message(user, "Tonight's current squares:")
            for key, value in testbingoDict.items():
                await asyncio.sleep(1.15)
                await bot.send_message(user, "`{}` by `{}` at {}.".format(key, value, testtimesDict.get(key)))
    else:
        if not bingoDict:
            await bot.send_message(user, "Nothing in the tracker yet!")
        else:
            await bot.send_message(user, "Tonight's current squares:")
            for key, value in bingoDict.items():
                await asyncio.sleep(1.15)
                await bot.send_message(user, "`{}` by `{}` at {}.".format(key, value, timesDict.get(key)))

@bot.command(pass_context=True, aliases=['break'])
@commands.cooldown(1, 30, commands.BucketType.channel)
async def breaklist(ctx):
    """Prints the current squares in alphabetic order in the current channel."""
    user = ctx.message.author
    if not ctx.message.channel.is_private:
        await bot.delete_message(ctx.message)
    if ctx.message.channel == users.testChannel:
        testsortedList.clear()
        testbreakList = []
        if not testbingoDict:
            await bot.send_message(user, "Nothing in the tracker yet!")
        elif testbingoDict:
            for key, value in testbingoDict.items():
                testsortedList.append(key)
            testsortedList.sort()
            testbreakList = ", ".join(testsortedList)
            await bot.send_message(ctx.message.channel, "**The break list has a 30 second cooldown.**")
            await bot.send_message(ctx.message.channel, "Current squares: {}.".format(testbreakList))
    else:
        sortedList.clear()
        breakList = []
        if not bingoDict:
            await bot.send_message(user, "Nothing in the tracker yet!")
        elif bingoDict:
            for key, value in bingoDict.items():
                sortedList.append(key)
            sortedList.sort()
            breakList = ", ".join(sortedList)
            await bot.send_message(ctx.message.channel, "**The break list has a 30 second cooldown.**")
            await bot.send_message(ctx.message.channel, "Current squares: {}.".format(breakList))

@bot.command(pass_context=True, aliases=['ssl','breaksorted'])
async def sortedsquarelist(ctx):
    """Sends a user a PM with the current tracked items in alphabetic order."""
    user = ctx.message.author
    if not ctx.message.channel.is_private:
        await bot.delete_message(ctx.message)
    if ctx.message.channel == users.testChannel:
        testsortedList.clear()
        if not testbingoDict:
            await bot.send_message(user, "Nothing in the tracker yet!")
        else:
            for key in testbingoDict.items():
                testsortedList.append(key)
            testsortedList.sort()
            await bot.send_message(user, "Tonight's current squares (alphabetized):")
            for i, v in testsortedList:
                await asyncio.sleep(1.15)
                await bot.send_message(user, "`{}` by `{}` at {}.".format(i, v, testtimesDict.get(i)))
    else:
        sortedList.clear()
        if not bingoDict:
            await bot.send_message(user, "Nothing in the tracker yet!")
        else:
            for key in bingoDict.items():
                sortedList.append(key)
            sortedList.sort()
            await bot.send_message(user, "Tonight's current squares (alphabetized):")
            for i, v in sortedList:
                await asyncio.sleep(1.15)
                await bot.send_message(user, "`{}` by `{}` at {}.".format(i, v, timesDict.get(i)))

@bot.command(pass_context=True)
async def squaresclear(ctx, confirm:str):
    """Erases all tracked items.  Usage "squaresclear YES"."""
    user = ctx.message.author
    if ctx.message.channel == users.testChannel:
        if confirm == "YES":
            testbingoDict.clear()
            await bot.send_message(ctx.message.channel, "{} CLEARED THE BINGO TRACKER".format(user.mention))
        elif confirm != "YES":
            await bot.send_message(ctx.message.channel,
                               "You must include the correct confirmation message to clear the bingo tracker!")
        else:
            await bot.send_message(ctx.message.channel,
                               "You must include the correct confirmation message to clear the bingo tracker!")
    elif ctx.message.author.id in users.WHITELIST:
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
    if ctx.message.channel == users.testChannel:
        if user_id in testwinnersSecret:
            await bot.send_message(user, "You've already called bingo tonight.  Ask a mod to remove you from the list if you called it in error.")
        else:
            await bot.send_message(ctx.message.channel, "Congrats {} on Bingo!".format(user.mention))
            timenow = datetime.datetime.now()
            testbingoWinners[user.display_name] = timenow.strftime("%I:%M %p")
            testwinnersSecret[user_id] = timenow.strftime("%I:%M %p")
            print(">> {}({}) CALLED BINGO AT {} <<\n".format(user.display_name, user, timenow.strftime("%H:%M")))
    else:
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
    if ctx.message.channel == users.testChannel:
        if susp in bingoWinners:
            del bingoWinners[susp]
            susp_id = discord.utils.find(lambda m: m.nick == susp, ctx.message.server.members).id
            if susp_id in winnersSecret:
                del winnersSecret[susp_id]
            await bot.send_message(user,"`{}` was removed from the winners list.".format(susp))
        else:
            await bot.send_message(user, "`{}` was not found in the winners list.".format(susp))
    if ctx.message.author.id in users.WHITELIST:
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
    if ctx.message.channel == users.testChannel:
        if confirm == "YES":
            testbingoWinners.clear()
            testwinnersSecret.clear()
            await bot.send_message(ctx.message.channel, "{} CLEARED THE BINGO WINNERS".format(user.mention))
        elif confirm != "YES":
            await bot.send_message(ctx.message.channel,
                               "You must include the correct confirmation message to clear the bingo winners!")
        else:
            await bot.send_message(ctx.message.channel,
                               "You must include the correct confirmation message to clear the bingo winners!")
    if ctx.message.author.id in users.WHITELIST:
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
    if ctx.message.channel == users.testChannel:
        if not testbingoWinners:
            await bot.send_message(user, "No winners for {} yet!".format(firstStartTime.strftime("%d %B %Y")))
        else:
            await bot.send_message(user, "Bingo winners for {}:".format(firstStartTime.strftime("%d %B %Y")))
            for key, value in testbingoWinners.items():
                await asyncio.sleep(1.15)
                await bot.send_message(user, "{} at {}.".format(key, value))
    else:
        if not bingoWinners:
            await bot.send_message(user, "No winners for {} yet!".format(firstStartTime.strftime("%d %B %Y")))
        else:
            await bot.send_message(user, "Bingo winners for {}:".format(firstStartTime.strftime("%d %B %Y")))
            for key, value in bingoWinners.items():
                await asyncio.sleep(1.15)
                await bot.send_message(user, "{} at {}.".format(key, value))

@bot.command(pass_context=True)
async def depts(ctx):
    """Lists the abbreviations for current Live PD departments."""
    user = ctx.message.author
    if not ctx.message.channel.is_private:
        await bot.delete_message(ctx.message)
    await bot.send_message(user, "Current active departments are (not case sensitive).  Use abbreviations on the left when adding squares:")
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

@bot.command(pass_context=True, aliases=['quit', 'stop'])
async def exit(ctx):
    """Shuts the bot off.  Restarts are 1am daily.  >>RESTRICTED USE<<"""
    if not ctx.message.channel.is_private:
        await bot.delete_message(ctx.message)
    if ctx.message.author.id in users.WHITELIST or ctx.message.channel == users.testChannel:
        await bot.logout()

@bot.command(pass_context=True)
async def bug(ctx, *bug : str):
    """Reports a bug to the #bugs channel in the dev Discord."""
    user = ctx.message.author
    bug = " ".join(bug)
    bugTime = datetime.datetime.now()
    if not ctx.message.channel.is_private:
        await bot.delete_message(ctx.message)
    print("Bug reported by {} at {}.".format(user, bugTime.strftime("%H:%M")))
    await bot.send_message(user, "I received your bug report of `{}` and will pass it on to the devs.  If you feel like this is a major bug, please use https://github.com/livepdbot/LivePDBot/issues to report the issue.".format(bug))
    await bot.send_message(discord.Object(id=users.bugChannel), "{} filed the bug report -> `{}`.".format(user, bug))

@bot.command(pass_context=True, aliases=['feat'])
async def feature(ctx, *feat: str):
    """Sends a feature request to the #feature-request channel in the dev Discord."""
    user = ctx.message.author
    feat = " ".join(feat)
    featTime = datetime.datetime.now()
    if not ctx.message.channel.is_private:
        await bot.delete_message(ctx.message)
    print("Feature requested by {} at {}.".format(user, featTime.strftime("%H:%M")))
    await bot.send_message(user, "I received your feature request of `{}` and will pass it on to the devs.  If you have code to make this happen, please use https://github.com/livepdbot/LivePDBot/pulls.".format(feat))
    await bot.send_message(discord.Object(id=users.featChannel), "{} filed the feature request -> `{}`.".format(user, feat))


bot.run(botToken)