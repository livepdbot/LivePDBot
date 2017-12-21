import discord, praw, asyncio, string, datetime
import users, wordlist, botcommands
from discord.ext import commands
from discord.ext.commands import Bot

#discord bot setup
commandPrefix = "!"
bot = commands.Bot(command_prefix=commandPrefix, pm_help=True)
botToken = users.BOT_TOKEN
firstStartTime = datetime.datetime.now()
bingoDict = {}
timesDict = {}
bingoWinners = {}
winnersSecret = {}
testbingoDict = {}
testtimesDict = {}
testbingoWinners = {}
testwinnersSecret = {}

#reddit instance setup
reddit = praw.Reddit(client_id=users.client_id,
                     client_secret=users.client_secret,
                     user_agent=users.user_agent,
                     username=users.username,
                     password=users.password)
botSubreddit = reddit.subreddit(users.botSubreddit)
liveSubreddit = reddit.subreddit(users.liveSubreddit)

#when the bot is fully loaded, this runs
@bot.event
async def on_ready():
    if firstStartTime.strftime("%A") == "Friday" or firstStartTime.strftime("%A") == "Saturday" and firstStartTime.strftime("%H:%M") == "21:00":
        bingoDict.clear()
        bingoWinners.clear()
        winnersSecret.clear()
    print('\nLogged into Discord as: {0} (ID: {0.id})'.format(bot.user))
    print('Logged into Reddit as: {}'.format(reddit.user.me()))
    print('Subreddits set to:\n\tBot: {}\n\tLive: {}\n'.format(botSubreddit,liveSubreddit))
    print(firstStartTime.strftime("Booted @ %H:%M on %A, %d %B %Y.\n"))
    '''print("Invite Link:\nhttps://discordapp.com/oauth2/authorize?client_id={}&scope=bot&permissions=8\n".format(
        bot.user.id))
    await bot.change_presence(game=discord.Game(name="{}".format(users.defaultStatus)))
    welcome = await bot.send_message(discord.Object(id=users.testChannel), "Bot is up.")
    await asyncio.sleep(3)
    await bot.delete_message(welcome)'''

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
    if ctx.message.author.id in users.WHITELIST or ctx.message.channel.id == users.testChannel:
        if len(gamename) >= 1:
            await bot.change_presence(game=discord.Game(name=gamename))
            await bot.say("Changed status to: `{}`".format(gamename))
        else:
            await bot.say("Needs more cowbell.")

@bot.command(pass_context=True, aliases=['sa'])
async def squareadd(ctx, square:str, dep:str):
    """Adds an item to the bingo tracker."""
    user = ctx.message.author
    if not ctx.message.channel.is_private:
        await bot.delete_message(ctx.message)
    if ctx.message.channel.id == users.testChannel:
        timenow = datetime.datetime.now()
        if square.upper() in wordlist.LIST:
            square = wordlist.CONVERT[square.upper()]
            if dep.upper() in users.DEPARTMENTS:
                if square not in bingoDict:
                    testbingoDict[square] = users.DEPARTMENTS[dep.upper()]
                    testtimesDict[square] = timenow.strftime("%I:%M %p")
                    await bot.send_message(ctx.message.channel,
                                           "{} added `{}` from `{}` to the test channel at {}.".format(user.mention, square,
                                                                                   users.DEPARTMENTS[dep.upper()],
                                                                                   timenow.strftime("%I:%M %p")))
                    print(
                        "+++\n{} added '{}' from '{}' to the test channel at {}.\n+++".format(ctx.message.author, square,
                                                                         users.DEPARTMENTS[dep.upper()],
                                                                         timenow.strftime("%H:%M")))
                else:
                    await bot.send_message(user,
                                           "`{}` was already claimed by `{}` at {}.".format(square, testbingoDict[square],
                                                                                            testtimesDict[square]))
            else:
                fdept, returnDeptList = botcommands.deptsearch(dep)
                if fdept == 0:
                    await bot.send_message(user, "Found the matching square `{}`, but no departments matching `{}`.".format(returnList,dep))
                elif fdept >= 2:
                    await bot.send_message(user, "Found the matching square (`{}`) and the following department(s): {}.".format(square, returnDeptList))
                elif fdept == 1:
                    timenow = datetime.datetime.now()
                    testbingoDict[square] = returnDeptList
                    testtimesDict[square] = timenow.strftime("%I:%M %p")
                    await bot.send_message(ctx.message.channel,
                                           "{} added `{}` from `{}` to the test channel at {}.".format(user.mention, square,
                                                                                   returnDeptList,
                                                                                   timenow.strftime("%I:%M %p")))
                    print(
                        "+++\n{} added '{}' from '{}' to the test channel at {}.\n+++".format(ctx.message.author, square,
                                                                                        returnDeptList,
                                                                                        timenow.strftime("%H:%M")))
        else:
            count, returnList = botcommands.search(square)
            if count == 0:
                await bot.send_message(user, "No squares matching `{}` were found.".format(square))
            elif count == 1 and dep.upper() in users.DEPARTMENTS:
                timenow = datetime.datetime.now()
                testbingoDict[returnList] = users.DEPARTMENTS[dep.upper()]
                testtimesDict[returnList] = timenow.strftime("%I:%M %p")
                await bot.send_message(ctx.message.channel,
                                       "{} added `{}` from `{}` to the test channel at {}.".format(user.mention, returnList,
                                                                               users.DEPARTMENTS[dep.upper()],
                                                                               timenow.strftime("%I:%M %p")))
                print(
                    "+++\n{} added '{}' from '{}' to the test channel at {}.\n+++".format(ctx.message.author, returnList,
                                                                                    users.DEPARTMENTS[dep.upper()],
                                                                                    timenow.strftime("%H:%M")))
            elif count == 1 and dep.upper() not in users.DEPARTMENTS:
                fdept, returnDeptList = botcommands.deptsearch(dep)
                if fdept == 0:
                    await bot.send_message(user, "Found the matching square `{}`, but no departments matching `{}`.".format(returnList,dep))
                elif fdept == 1:
                    timenow = datetime.datetime.now()
                    testbingoDict[returnList] = returnDeptList
                    testtimesDict[returnList] = timenow.strftime("%I:%M %p")
                    await bot.send_message(ctx.message.channel,
                                           "{} added `{}` from `{}` to the test channel at {}.".format(user.mention, returnList,
                                                                                   returnDeptList,
                                                                                   timenow.strftime("%I:%M %p")))
                    print(
                        "+++\n{} added '{}' from '{}' to the test channel at {}.\n+++".format(ctx.message.author, returnList,
                                                                                        returnDeptList,
                                                                                        timenow.strftime("%H:%M")))
                elif fdept >= 2:
                    await bot.send_message(user, "Found the matching square and the following department(s): {}.".format(returnList, returnDeptList))
            elif count >= 2:
                await bot.send_message(user, "Found the following {} square matches: {}.".format(count, returnList))
    elif ctx.message.author.id in users.WHITELIST:
        timenow = datetime.datetime.now()
        if square.upper() in wordlist.LIST:
            square = wordlist.CONVERT[square.upper()]
            if dep.upper() in users.DEPARTMENTS:
                if square not in bingoDict:
                    bingoDict[square] = users.DEPARTMENTS[dep.upper()]
                    timesDict[square] = timenow.strftime("%I:%M %p")
                    await bot.send_message(ctx.message.channel,
                                           "{} added `{}` from `{}` at {}.".format(user.mention, square,
                                                                                   users.DEPARTMENTS[dep.upper()],
                                                                                   timenow.strftime("%I:%M %p")))
                    print(
                        "+++\n{} added '{}' from '{}' to the live channel at {}.\n+++".format(ctx.message.author, square,
                                                                                              users.DEPARTMENTS[dep.upper()],
                                                                                              timenow.strftime("%H:%M")))
                else:
                    await bot.send_message(user,
                                           "`{}` was already claimed by `{}` at {}.".format(square, bingoDict[square],
                                                                                            timesDict[square]))
            else:
                fdept, foundDeptList = botcommands.deptsearch(dep)
                if fdept == 0:
                    await bot.send_message(user, "Found the matching square `{}`, but no departments matching `{}`.".format(square,dep))
                elif fdept >= 2:
                    await bot.send_message(user, "Found the matching square (`{}`) and the following department(s): {}.".format(square, returnDeptList))
                elif fdept == 1:
                    timenow = datetime.datetime.now()
                    bingoDict[square] = foundDeptList
                    timesDict[square] = timenow.strftime("%I:%M %p")
                    await bot.send_message(ctx.message.channel,
                                           "{} added `{}` from `{}` to at {}.".format(user.mention, square, foundDeptList,
                                                                                      timenow.strftime("%I:%M %p")))
                    print(
                        "+++\n{} added '{}' from '{}' to the live channel at {}.\n+++".format(ctx.message.author, square,
                                                                                              foundDeptList,
                                                                                              timenow.strftime("%H:%M")))
        else:
            count, returnList = botcommands.search(square)
            if count == 0:
                await bot.send_message(user, "No squares matching `{}` were found.".format(square))
            elif count == 1 and dep.upper() in users.DEPARTMENTS:
                timenow = datetime.datetime.now()
                bingoDict[returnList] = users.DEPARTMENTS[dep.upper()]
                timesDict[returnList] = timenow.strftime("%I:%M %p")
                await bot.send_message(ctx.message.channel,
                                       "{} added `{}` from `{}` at {}.".format(user.mention, returnList,
                                                                               users.DEPARTMENTS[dep.upper()],
                                                                               timenow.strftime("%I:%M %p")))
                print(
                    "+++\n{} added '{}' from '{}' to the live channel at {}.\n+++".format(ctx.message.author, returnList,
                                                                                    users.DEPARTMENTS[dep.upper()],
                                                                                    timenow.strftime("%H:%M")))
            elif count == 1 and dep.upper() not in users.DEPARTMENTS:
                fdept, foundDeptList = botcommands.deptsearch(dep)
                if fdept == 0:
                    await bot.send_message(user, "Found the matching square `{}`, but no departments matching `{}`.".format(returnList,dep))
                elif fdept == 1:
                    timenow = datetime.datetime.now()
                    bingoDict[returnList] = foundDeptList
                    timesDict[returnList] = timenow.strftime("%I:%M %p")
                    await bot.send_message(ctx.message.channel,
                                           "{} added `{}` from `{}` at {}.".format(user.mention, returnList,
                                                                                   foundDeptList,
                                                                                   timenow.strftime("%I:%M %p")))
                    print(
                        "+++\n{} added '{}' from '{}' to the live channel at {}.\n+++".format(ctx.message.author, returnList,
                                                                                              foundDeptList,
                                                                                              timenow.strftime("%H:%M")))
                elif fdept >= 2:
                    await bot.send_message(user, "Found the matching square and the following department(s): {}.".format(returnList, foundDeptList))
            elif count >= 2:
                await bot.send_message(user, "Found the following {} square matches: {}.".format(count, returnList))
    else:
        await bot.send_message(user, "You don't have permission to add to the tracker.")

@bot.command(pass_context=True, aliases=['find'])
async def search(ctx, word:str):
    """Searches the square list for squares matching the search term(s)."""
    user = ctx.message.author
    if not ctx.message.channel.is_private:
        await bot.delete_message(ctx.message)
    count, returnList = botcommands.search(word)
    if count == 0:
        await bot.send_message(user, "No matches found.")
    if count == 1:
        await bot.send_message(user, "Found `{}`.".format(returnList))
    elif count >= 2:
        await bot.send_message(user, "Found the following {} square matches: {}.".format(count, returnList))

@bot.command(pass_context=True, aliases=['dfind'])
async def deptsearch(ctx, dept:str):
    """Searches the department list for department(s) matching the search term."""
    user = ctx.message.author
    if not ctx.message.channel.is_private:
        await bot.delete_message(ctx.message)
    fdept, foundDeptList = botcommands.deptsearch(dept)
    if fdept == 0:
        await bot.send_message(user, "No matching department.")
    if fdept >= 1:
        await bot.send_message(user, "Found the following department(s): {}.".format(returnDeptList))

@bot.command(pass_context=True, aliases=['srm'])
async def squareremove(ctx, square:str):
    """Removes an item from the bingo tracker."""
    user = ctx.message.author
    timenow = datetime.datetime.now()
    if not ctx.message.channel.is_private:
        await bot.delete_message(ctx.message)
    if ctx.message.channel.id == users.testChannel:
        if square in testbingoDict:
            del testbingoDict[square]
            await bot.send_message(ctx.message.channel, "{} removed `{}` from the tracked list.".format(user.mention, square))
            print("---\n{} removed '{}' from the test channel tracker at {}.\n---".format(ctx.message.author, square, timenow.strftime("%H:%M")))
        else:
            square = square.upper()
            searchList = []
            foundList = []
            returnList = []
            i = 0
            count = 0
            searchList = list(testbingoDict.keys())
            while i < len(searchList):
                searchList[i] = searchList[i].upper()
                if searchList[i].find(square) != -1:
                    searchList[i] = wordlist.CONVERT[searchList[i]]
                    foundList.append(searchList[i])
                    returnList = ", ".join(foundList)
                    i = i + 1
                    count = count + 1
                else:
                    i = i + 1
            if count == 0:
                await bot.send_message(user, "`{}` is not currently being tracked.".format(square))
            if count == 1:
                del testbingoDict[returnList]
                await bot.send_message(ctx.message.channel,
                                       "{} removed `{}` from the tracked list.".format(user.mention, returnList))
                print(
                    "---\n{} removed '{}' from the test channel tracker at {}.\n---".format(ctx.message.author, returnList,
                                                                                            timenow.strftime("%H:%M")))
            elif count >= 2:
                await bot.send_message(user, "Found the following {} matches: {}.".format(count, returnList))
    elif ctx.message.author.id in users.WHITELIST:
        if square in bingoDict:
            del bingoDict[square]
            await bot.send_message(ctx.message.channel, "{} removed `{}` from the tracked list.".format(user.mention, square))
            print("---\n{} removed '{}' from the live channel tracker at {}.\n---".format(ctx.message.author, square,
                                                                                          timenow.strftime("%H:%M")))
        else:
            square = square.upper()
            searchList = []
            foundList = []
            returnList = []
            i = 0
            count = 0
            searchList = list(bingoDict.keys())
            while i < len(searchList):
                searchList[i] = searchList[i].upper()
                if searchList[i].find(square) != -1:
                    searchList[i] = wordlist.CONVERT[searchList[i]]
                    foundList.append(searchList[i])
                    returnList = ", ".join(foundList)
                    i = i + 1
                    count = count + 1
                else:
                    i = i + 1
            if count == 0:
                await bot.send_message(user, "`{}` is not currently being tracked.".format(square))
            if count == 1:
                del bingoDict[returnList]
                await bot.send_message(ctx.message.channel, "{} removed `{}` from the tracked list.".format(user.mention,returnList))
                print(
                    "---\n{} removed '{}' from the live channel tracker at {}.\n---".format(ctx.message.author, returnList,
                                                                                            timenow.strftime("%H:%M")))
            elif count >= 2:
                await bot.send_message(user, "Found the following {} matches: {}.".format(count, returnList))
    else:
        await bot.send_message(user, "You don't have permission to remove tracked squares.")

@bot.command(pass_context=True, aliases=['sl'])
async def squarelist(ctx):
    """Sends a user a PM with the current tracked items."""
    user = ctx.message.author
    if not ctx.message.channel.is_private:
        await bot.delete_message(ctx.message)
    if ctx.message.channel.id == users.testChannel:
        testsortedList = []
        testbreakList = []
        if not testbingoDict:
            await bot.send_message(user, "Nothing in the tracker yet!")
        elif testbingoDict:
            for key, value in testbingoDict.items():
                testTime = testtimesDict[key]
                testsortedList.append("{} ({})".format(key, testTime))
            testbreakList = ", ".join(testsortedList)
            await bot.send_message(user, "Current test channel squares (chronological): {}.".format(testbreakList))
    else:
        sortedList = []
        breakList = []
        if not bingoDict:
            await bot.send_message(user, "Nothing in the tracker yet!")
        elif bingoDict:
            for key, value in bingoDict.items():
                sortedList.append("{} ({})".format(key, value))
            breakList = ", ".join(sortedList)
            await bot.send_message(user, "Current squares (chronological): {}.".format(breakList))

@bot.command(pass_context=True, aliases=['break'])
@commands.cooldown(1, 30, commands.BucketType.channel)
async def breaklist(ctx):
    """Prints the current squares in alphabetic order in the current channel."""
    user = ctx.message.author
    if not ctx.message.channel.is_private:
        await bot.delete_message(ctx.message)
    if ctx.message.channel.id == users.testChannel:
        testsortedList =[]
        testbreakList = []
        if not testbingoDict:
            await bot.send_message(user, "Nothing in the tracker yet!")
        elif testbingoDict:
            for key, value in testbingoDict.items():
                testsortedList.append(key)
            testsortedList.sort()
            testbreakList = ", ".join(testsortedList)
            await bot.send_message(ctx.message.channel, "**The break list has a 30 second cooldown.**")
            await bot.send_message(ctx.message.channel, "Current test channel squares (alphabetized): {}.".format(testbreakList))
    else:
        sortedList =[]
        breakList = []
        if not bingoDict:
            await bot.send_message(user, "Nothing in the tracker yet!")
        elif bingoDict:
            for key, value in bingoDict.items():
                sortedList.append(key)
            sortedList.sort()
            breakList = ", ".join(sortedList)
            await bot.send_message(ctx.message.channel, "**The break list has a 30 second cooldown.**")
            await bot.send_message(ctx.message.channel, "Current squares (alphabetized): {}.".format(breakList))

@bot.command(pass_context=True, aliases=['tbreak'])
@commands.cooldown(1, 30, commands.BucketType.channel)
async def breaktime(ctx):
    """Prints the current squares in chronological order in the current channel."""
    user = ctx.message.author
    if not ctx.message.channel.is_private:
        await bot.delete_message(ctx.message)
    if ctx.message.channel.id == users.testChannel:
        testsortedList =[]
        testbreakList = []
        if not testbingoDict:
            await bot.send_message(user, "Nothing in the tracker yet!")
        elif testbingoDict:
            for key, value in testbingoDict.items():
                testTime = testtimesDict[key]
                testsortedList.append("{} ({})".format(key, testTime))
            #testsortedList.sort()
            testbreakList = ", ".join(testsortedList)
            await bot.send_message(ctx.message.channel, "**The break list has a 30 second cooldown.**")
            await bot.send_message(ctx.message.channel, "Current test channel squares (chronological): {}.".format(testbreakList))
    else:
        sortedList =[]
        breakList = []
        if not bingoDict:
            await bot.send_message(user, "Nothing in the tracker yet!")
        elif bingoDict:
            for key, value in bingoDict.items():
                sortedList.append("{} ({})".format(key, value))
            breakList = ", ".join(sortedList)
            await bot.send_message(ctx.message.channel, "**The break list has a 30 second cooldown.**")
            await bot.send_message(ctx.message.channel, "Current squares (chronological): {}.".format(breakList))

@bot.command(pass_context=True, aliases=['ssl','breaksorted'])
async def sortedsquarelist(ctx):
    """Sends a user a PM with the current tracked items in alphabetic order."""
    user = ctx.message.author
    if not ctx.message.channel.is_private:
        await bot.delete_message(ctx.message)
    if ctx.message.channel.id == users.testChannel:
        testsortedList = []
        testbreakList = []
        if not testbingoDict:
            await bot.send_message(user, "Nothing in the tracker yet!")
        elif testbingoDict:
            for key, value in testbingoDict.items():
                testsortedList.append(key)
            testsortedList.sort()
            testbreakList = ", ".join(testsortedList)
            await bot.send_message(user,"Current test channel squares (alphabetized): {}.".format(testbreakList))
    else:
        sortedList = []
        breakList = []
        if not bingoDict:
            await bot.send_message(user, "Nothing in the tracker yet!")
        elif bingoDict:
            for key, value in bingoDict.items():
                sortedList.append(key)
            sortedList.sort()
            breakList = ", ".join(sortedList)
            await bot.send_message(user, "Current squares (alphabetized): {}.".format(breakList))

@bot.command(pass_context=True)
async def squaresclear(ctx, confirm:str):
    """Erases all tracked items."""
    user = ctx.message.author
    if ctx.message.channel.id == users.testChannel:
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
async def start(ctx, confirm:str):
    """Clears the bingo winners and tracked squares"""
    user = ctx.message.author
    if ctx.message.author.id in users.WHITELIST:
        if confirm == "YES":
            bingoWinners.clear()
            winnersSecret.clear()
            bingoDict.clear()
            await bot.send_message(ctx.message.channel, "{} CLEARED THE BINGO WINNERS AND TRACKED SQUARES.".format(user.mention))
        elif confirm != "YES":
            await bot.send_message(ctx.message.channel,
                               "You must include the correct confirmation message to clear the bingo winners and tracked squares!")
        else:
            await bot.send_message(ctx.message.channel,
                               "You must include the correct confirmation message to clear the bingo winners and tracked squares!")
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
    if ctx.message.channel.id == users.testChannel:
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
    if ctx.message.channel.id == users.testChannel:
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
    """Erases the current bingo winners."""
    user = ctx.message.author
    if ctx.message.channel.id == users.testChannel:
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
    if ctx.message.channel.id == users.testChannel:
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
        await bot.send_message(ctx.message.channel, "{} -> `{}`: {}".format(user.mention, word,
                                                                            wordlist.LIST[word.upper()]))
    else:
        count, returnList = botcommands.search(word)
        if count == 0:
            await bot.send_message(ctx.message.channel, "`{}` is not an official square.".format(word))
        elif count == 1:
            await bot.send_message(ctx.message.channel,
                                   "{} -> `{}`: {}".format(user.mention, returnList, wordlist.LIST[returnList.upper()]))
        elif count >= 2:
            await bot.send_message(user, "Multiple matches found: {}.".format(returnList))

@bot.command(pass_context=True, aliases=['quit', 'stop'])
async def exit(ctx):
    """Shuts the bot off.  Restarts are 1am daily.  >>RESTRICTED USE<<"""
    if not ctx.message.channel.is_private:
        await bot.delete_message(ctx.message)
    if ctx.message.author.id in users.WHITELIST or ctx.message.channel == users.testChannel:
        await bot.logout()

@bot.command(pass_context=True)
async def bug(ctx, *bug : str):
    """Reports a bug to the #bugs channel in the dev Discord and creates a post on the bot subreddit."""
    user = ctx.message.author
    bug = " ".join(bug)
    bugTime = datetime.datetime.now()
    if not ctx.message.channel.is_private:
        await bot.delete_message(ctx.message)
    submission = reddit.subreddit(users.botSubreddit).submit(title="Bug Report by {}".format(user),selftext=bug,flair_id=users.bugFlair,send_replies=False)
    print(">>> Bug reported by {} at {} ({}). <<<".format(user, bugTime.strftime("%H:%M"),submission.shortlink))
    await bot.send_message(user, "I received your bug report of `{}`.  Your bug report can be found here: {}".format(bug,
                                                                                                                     submission.shortlink))
    await bot.send_message(discord.Object(id=users.bugChannel), "{} filed the bug report -> `{}` ({}).".format(user, bug,
                                                                                                               submission.shortlink))

@bot.command(pass_context=True, aliases=['feat'])
async def feature(ctx, *feat: str):
    """Sends a feature request to the #feature-request channel in the dev Discord and creates a post on the bot subreddit."""
    user = ctx.message.author
    feat = " ".join(feat)
    featTime = datetime.datetime.now()
    if not ctx.message.channel.is_private:
        await bot.delete_message(ctx.message)
    submission = reddit.subreddit(users.botSubreddit).submit(title="Feature request by {}".format(user),selftext=feat,
                                                             flair_id=users.featFlair,send_replies=False)
    print(">>> Feature requested by {} at {} ({}). <<<".format(user, featTime.strftime("%H:%M"),submission.shortlink))
    await bot.send_message(user, "I received your feature request of `{}`.  Your feature request can be found here: {}".format(feat,
                                                                                                                         submission.shortlink))
    await bot.send_message(discord.Object(id=users.featChannel), "{} filed the feature request -> `{}` ({}).".format(user,
                                                                                                                     feat, submission.shortlink))

@bot.command(pass_context=True)
async def time(ctx, square:str):
    """Returns the time a square was added to the tracker."""
    user = ctx.message.author
    if not ctx.message.channel.is_private:
        await bot.delete_message(ctx.message)
    if ctx.message.channel.id == users.testChannel:
        await bot.send_message(user, "`{}time` is not implemented on the test channel.".format(commandPrefix))
    else:
        squareUpper = square.upper()
        searchList = []
        foundList = []
        returnList = []
        i = 0
        count = 0
        searchList = list(bingoDict.keys())
        while i < len(searchList):
            searchList[i] = searchList[i].upper()
            if searchList[i].find(squareUpper) != -1:
                searchList[i] = wordlist.CONVERT[searchList[i]]
                foundList.append(searchList[i])
                returnList = ", ".join(foundList)
                i = i + 1
                count = count + 1
            else:
                i = i + 1
        if count == 0:
            await bot.send_message(user, "`{}` is not being tracked.".format(square))
        if count == 1:
            time = timesDict[returnList]
            await bot.send_message(ctx.message.channel, "`{}` was added at `{}`.".format(returnList, time))
        elif count >= 2:
            await bot.send_message(user, "Multiple matches for `{}` found.  Please be more specific.".format(square))

@bot.command(pass_context=True)
async def dev(ctx):
    """Sends the user an invite to the development discord server."""
    user = ctx.message.author
    if not ctx.message.channel.is_private:
        await bot.delete_message(ctx.message)
    await bot.send_message(user, "Development server: {}".format(users.devServerInvite))

@bot.command(pass_context=True)
async def end(ctx, thread_id:str):
    """Reports the night's final square tally to the thread specified, outputs the night's bingo callers, and clears all trackers."""
    user = ctx.message.author
    if not ctx.message.channel.is_private:
        await bot.delete_message(ctx.message)
    if ctx.message.author.id in users.WHITELIST:
        sortedList = []
        sortedSquares = []
        sortedBingo = []
        if not bingoDict:
            await bot.send_message(user, "There is nothing in the tracker to post.")
        if not bingoWinners:
            await  bot.send_message(user, "No one called bingo in Discord.")
        elif bingoDict and bingoWinners:
            for key, value in bingoDict.items():
                time = timesDict[key]
                sortedList.append("{} @ {} ({})".format(key, time, value))
            sortedSquares = ", ".join(sortedList)
            squaresSubmission = "Tonight's squares: {}.".format(sortedSquares)
            await bot.send_message(ctx.message.channel, squaresSubmission)
            sortedList.clear()
            for key, value in bingoWinners.items():
                sortedList.append("{} @ {}".format(key, value))
                sortedBingo = ", ".join(sortedList)
            winnersSubmission = "Tonight's Discord Bingo winners: {}.".format(sortedBingo)
            await bot.send_message(ctx.message.channel, winnersSubmission)
            endTime = datetime.datetime.now()
            winnerFile = open('bingowinners.txt', 'a')
            winnerFile.write(endTime.strftime("\n\n%A, %d %B %Y\n"))
            winnerFile.write(sortedBingo)
            winnerFile.close()
            sortedList.clear()
            nightlyThread = reddit.submission(id=thread_id)
            squaresComment = nightlyThread.reply(squaresSubmission)
            winnersComment = nightlyThread.reply(winnersSubmission)
            await bot.send_message(ctx.message.channel, "Thread posted at: {}.\nSquares' comment: https://www.reddit.com{}.\nWinners' comment: https://www.reddit.com{}.".format(nightlyThread.shortlink,squaresComment.permalink,winnersComment.permalink))
            print("### Thread posted at: {}.\nSquares' comment: https://www.reddit.com{}.\nWinners' comment: https://www.reddit.com{}. ###".format(nightlyThread.shortlink,squaresComment.permalink,winnersComment.permalink))
            bingoDict.clear()
            bingoWinners.clear()
    else:
        await bot.send_message(user, "You don't have permission to run the end of the night report")


bot.run(botToken)
