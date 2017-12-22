# Import statements
import discord
import praw
import asyncio
import sqlite3
import users
import wordlist
import botcommands
import time
from discord import errors
from datetime import datetime
from discord.ext import commands
from discord.ext.commands import Bot
from discord.ext.commands import errors as er

# discord bot setup
commandPrefix = "!"
bot = commands.Bot(command_prefix=commandPrefix, pm_help=True)
startTime = datetime.fromtimestamp(time.time())
bingoDict = {}
timesDict = {}
bingoWinners = {}
winnersSecret = {}
testbingoDict = {}
testtimesDict = {}
testbingoWinners = {}
testwinnersSecret = {}


# reddit instance setup
reddit = praw.Reddit(client_id=users.client_id,
                     client_secret=users.client_secret,
                     user_agent=users.user_agent,
                     username=users.username,
                     password=users.password)
botSubreddit = reddit.subreddit(users.botSubreddit)
liveSubreddit = reddit.subreddit(users.liveSubreddit)


# SQLite3 setup
connection = sqlite3.connect('tracker.db')
cursor = connection.cursor()


# when the bot is fully loaded, this runs
@bot.event
async def on_ready():
    print('\nLogged into Discord as: {0} (ID: {0.id})'.format(bot.user))
    print('Logged into Reddit as: {}'.format(reddit.user.me()))
    print('Subreddits set to:\n\tBot: {}\n\tLive: {}\n'.format(botSubreddit,liveSubreddit))
    print(startTime.strftime("Booted @ %H:%M on %A, %d %B %Y.\n"))
    await bot.change_presence(game=discord.Game(name="{}".format(users.defaultStatus)))
    cursor.execute("DROP TABLE IF EXISTS squares")
    connection.commit()
    cursor.execute("CREATE TABLE IF NOT EXISTS squares(square TEXT, department TEXT, time TEXT)")
    connection.commit()
    cursor.execute("DROP TABLE IF EXISTS testsquares")
    connection.commit()
    cursor.execute("CREATE TABLE IF NOT EXISTS testsquares(square TEXT, department TEXT, time TEXT)")
    connection.commit()
    cursor.execute("DROP TABLE IF EXISTS winners")
    connection.commit()
    cursor.execute("CREATE TABLE IF NOT EXISTS winners(name TEXT, id TEXT, time TEXT)")
    connection.commit()
    cursor.execute("DROP TABLE IF EXISTS testwinners")
    connection.commit()
    cursor.execute("CREATE TABLE IF NOT EXISTS testwinners(name TEXT, id TEXT, time TEXT)")
    connection.commit()
    print("Table creation completed.")
    '''print("Invite Link:\nhttps://discordapp.com/oauth2/authorize?client_id={}&scope=bot&permissions=8\n".format(
        bot.user.id))
    welcome = await bot.send_message(discord.Object(id=users.testChannel), "Bot is up.")
    await asyncio.sleep(3)
    await bot.delete_message(welcome)'''
    print("Completed Setup!")


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
    await bot.send_message(ctx.message.channel, startTime.strftime("Booted @ %H:%M on %A, %d %B %Y"))
    await bot.send_message(ctx.message.channel, "That's {}! (Hours:Minutes:Seconds.Milliseconds)".format(datetime.now()-startTime))


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
    # squares(square TEXT, department TEXT, time TEXT)
    user = ctx.message.author
    timeNow = datetime.now()
    squareUpper = square.upper()
    depUpper = dep.upper()
    counter = 0
    if not ctx.message.channel.is_private:
        await bot.delete_message(ctx.message)
    if ctx.message.channel.id == users.testChannel:
        print("test channel: {}".format(ctx.message.content))
        if squareUpper in wordlist.LIST:
            convertedSquare = wordlist.CONVERT[squareUpper]
            cursor.execute("SELECT * FROM testsquares")
            for row in cursor.fetchall():
                if row[0] == convertedSquare:
                    counter += 1
                else:
                    counter += 0
            if counter == 1:
                cursor.execute("SELECT * FROM testsquares WHERE square=?", (convertedSquare,))
                for row in cursor.fetchall():
                    dept = row[1]
                    time = row[2]
                await bot.send_message(user, "`{}` has already been claimed by `{}` at {}.".format(convertedSquare, dept, time))
            else:
                if depUpper in users.DEPARTMENTS:
                    convertedDep = users.DEPARTMENTS[depUpper]
                    cursor.execute("INSERT INTO testsquares (square, department, time) VALUES(?, ?, ?)",(convertedSquare, convertedDep, timeNow.strftime("%I:%M %p")))
                    print("+++\n{} added '{}' from '{}' to the test channel at {}.\n+++".format(ctx.message.author,convertedSquare,convertedDep,timeNow.strftime("%H:%M")))
                    connection.commit()
                    await bot.send_message(ctx.message.channel, "{} added `{}` from `{}` to the test channel at {}.".format(user.mention, convertedSquare, convertedDep, timeNow.strftime("%I:%M %p")))
                else:
                    fdept, returnDeptList = botcommands.deptsearch(depUpper)
                    if fdept == 0:
                        await bot.send_message(user, "Found the matching square `{}`, but no departments matching `{}`.".format(convertedSquare, dep))
                    elif fdept >= 2:
                        await bot.send_message(user, "Found the matching square `{}` and the following department(s): {}.".format(convertedSquare, returnDeptList))
                    elif fdept == 1:
                        cursor.execute("INSERT INTO testsquares (square, department, time) VALUES(?, ?, ?)", (convertedSquare, returnDeptList, timeNow.strftime("%I:%M %p")))
                        connection.commit()
                        await bot.send_message(ctx.message.channel,"{} added `{}` from `{}` to the test channel at {}.".format(user.mention, convertedSquare, returnDeptList, timeNow.strftime("%I:%M %p")))
                        print("+++\n{} added '{}' from '{}' to the test channel at {}.\n+++".format(ctx.message.author, convertedSquare ,returnDeptList, timeNow.strftime("%H:%M")))
        else:
            count, convertedSquare = botcommands.search(squareUpper)
            if count == 0:
                await bot.send_message(user, "No squares matching `{}` were found.".format(square))
            elif count == 1:
                cursor.execute("SELECT * FROM testsquares")
                for row in cursor.fetchall():
                    if row[0] == convertedSquare:
                        counter += 1
                    else:
                        counter += 0
                if counter == 1:
                    cursor.execute("SELECT * FROM testsquares WHERE square=?", (convertedSquare,))
                    for row in cursor.fetchall():
                        dept = row[1]
                        time = row[2]
                    await bot.send_message(user, "`{}` has already been claimed by `{}` at {}.".format(convertedSquare, dept, time))
                else:
                    if depUpper in users.DEPARTMENTS:
                        convertedDep = users.DEPARTMENTS[depUpper]
                        cursor.execute("INSERT INTO testsquares (square, department, time) VALUES(?, ?, ?)",(convertedSquare, convertedDep, timeNow.strftime("%I:%M %p")))
                        connection.commit()
                        await bot.send_message(ctx.message.channel, "{} added `{}` from `{}` to the test channel at {}.".format(user.mention, convertedSquare, convertedDep, timeNow.strftime("%I:%M %p")))
                        print("+++\n{} added '{}' from '{}' to the test channel at {}.\n+++".format(ctx.message.author,convertedSquare,convertedDep,timeNow.strftime("%H:%M")))
                    else:
                        fdept, returnDeptList = botcommands.deptsearch(depUpper)
                        if fdept == 0:
                            await bot.send_message(user, "Found the matching square `{}`, but no departments matching `{}`.".format(convertedSquare, dep))
                        elif fdept >= 2:
                            await bot.send_message(user, "Found the matching square `{}` and the following department(s): {}.".format(convertedSquare, returnDeptList))
                        elif fdept == 1:
                            cursor.execute("INSERT INTO testsquares (square, department, time) VALUES(?, ?, ?)", (convertedSquare, returnDeptList, timeNow.strftime("%I:%M %p")))
                            connection.commit()
                            await bot.send_message(ctx.message.channel,"{} added `{}` from `{}` to the test channel at {}.".format(user.mention, convertedSquare, returnDeptList, timeNow.strftime("%I:%M %p")))
                            print("+++\n{} added '{}' from '{}' to the test channel at {}.\n+++".format(ctx.message.author, convertedSquare ,returnDeptList, timeNow.strftime("%H:%M")))
            else:
                await bot.send_message(user, "There were {} matches for the square ({}) you used: {}".format(count,square,convertedSquare))
    elif ctx.message.author.id in users.WHITELIST:
        if squareUpper in wordlist.LIST:
            convertedSquare = wordlist.CONVERT[squareUpper]
            cursor.execute("SELECT * FROM squares")
            for row in cursor.fetchall():
                if row[0] == convertedSquare:
                    counter += 1
                else:
                    counter += 0
            if counter == 1:
                cursor.execute("SELECT * FROM squares WHERE square=?", (convertedSquare,))
                for row in cursor.fetchall():
                    dept = row[1]
                    time = row[2]
                await bot.send_message(user,
                                       "`{}` has already been claimed by `{}` at {}.".format(convertedSquare, dept,time))
            else:
                if depUpper in users.DEPARTMENTS:
                    convertedDep = users.DEPARTMENTS[depUpper]
                    cursor.execute("INSERT INTO squares (square, department, time) VALUES(?, ?, ?)",
                                   (convertedSquare, convertedDep, timeNow.strftime("%I:%M %p")))
                    print("+++\n{} added '{}' from '{}' to the live channel at {}.\n+++".format(ctx.message.author,convertedSquare,convertedDep,timeNow.strftime("%H:%M")))
                    connection.commit()
                    await bot.send_message(ctx.message.channel,
                                           "{} added `{}` from `{}` at {}.".format(user.mention,convertedSquare,convertedDep,timeNow.strftime("%I:%M %p")))
                else:
                    fdept, returnDeptList = botcommands.deptsearch(depUpper)
                    if fdept == 0:
                        await bot.send_message(user,"Found the matching square `{}`, but no departments matching `{}`.".format(convertedSquare, dep))
                    elif fdept >= 2:
                        await bot.send_message(user,"Found the matching square `{}` and the following department(s): {}.".format(convertedSquare, returnDeptList))
                    elif fdept == 1:
                        cursor.execute("INSERT INTO squares (square, department, time) VALUES(?, ?, ?)",(convertedSquare, returnDeptList, timeNow.strftime("%I:%M %p")))
                        connection.commit()
                        await bot.send_message(ctx.message.channel,"{} added `{}` from `{}` at {}.".format(user.mention,convertedSquare,returnDeptList,timeNow.strftime("%I:%M %p")))
                        print("+++\n{} added '{}' from '{}' to the live channel at {}.\n+++".format(ctx.message.author,convertedSquare,returnDeptList,timeNow.strftime("%H:%M")))
        else:
            count, convertedSquare = botcommands.search(squareUpper)
            if count == 0:
                await bot.send_message(user, "No squares matching `{}` were found.".format(square))
            elif count == 1:
                cursor.execute("SELECT * FROM squares")
                for row in cursor.fetchall():
                    if row[0] == convertedSquare:
                        counter += 1
                    else:
                        counter += 0
                if counter == 1:
                    cursor.execute("SELECT * FROM squares WHERE square=?", (convertedSquare,))
                    for row in cursor.fetchall():
                        dept = row[1]
                        time = row[2]
                    await bot.send_message(user,"`{}` has already been claimed by `{}` at {}.".format(convertedSquare, dept,time))
                else:
                    if depUpper in users.DEPARTMENTS:
                        convertedDep = users.DEPARTMENTS[depUpper]
                        cursor.execute("INSERT INTO squares (square, department, time) VALUES(?, ?, ?)",(convertedSquare, convertedDep, timeNow.strftime("%I:%M %p")))
                        connection.commit()
                        await bot.send_message(ctx.message.channel, "{} added `{}` from `{}` at {}.".format(user.mention,convertedSquare,convertedDep,timeNow.strftime("%I:%M %p")))
                    else:
                        fdept, returnDeptList = botcommands.deptsearch(depUpper)
                        if fdept == 0:
                            await bot.send_message(user,"Found the matching square `{}`, but no departments matching `{}`.".format(convertedSquare, dep))
                        elif fdept >= 2:
                            await bot.send_message(user,"Found the matching square `{}` and the following department(s): {}.".format(convertedSquare, returnDeptList))
                        elif fdept == 1:
                            cursor.execute("INSERT INTO squares (square, department, time) VALUES(?, ?, ?)",(convertedSquare, returnDeptList, timeNow.strftime("%I:%M %p")))
                            connection.commit()
                            await bot.send_message(ctx.message.channel,"{} added `{}` from `{}` at {}.".format(user.mention, convertedSquare, returnDeptList,timeNow.strftime("%I:%M %p")))
                            print("+++\n{} added '{}' from '{}' to the live channel at {}.\n+++".format(ctx.message.author, convertedSquare, returnDeptList, timeNow.strftime("%H:%M")))
            else:
                print("something went wrong.")


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
    # squares(square TEXT, department TEXT, time TEXT)
    user = ctx.message.author
    timeNow = datetime.now()
    squareUpper = square.upper()
    thisList = []
    currentList = []
    counter = 0
    if not ctx.message.channel.is_private:
        await bot.delete_message(ctx.message)
    if ctx.message.channel.id == users.testChannel:
        cursor.execute("SELECT * FROM testsquares")
        for row in cursor.fetchall():
            thisList.append(row[0])
            if row[0] == square.capitalize():
                counter += 1
            else:
                counter += 0
        thatList = ", ".join(thisList)
        if counter == 1:
            cursor.execute("DELETE FROM testsquares WHERE square=?", (thatList,))
            connection.commit()
            await bot.send_message(ctx.message.channel, "{} removed `{}` from the tracked squares list.".format(user.mention, thatList))
            print("---\n{} removed '{}' from the test channel tracker at {}.\n---".format(ctx.message.author, thatList, timeNow.strftime("%H:%M")))
        elif counter >= 2:
            await bot.send_message(user, "Multiple matches found in the tracker: {}.".format(thatList))
        else:
            sleeper = await bot.send_message(ctx.message.channel, "Nothing found in the tracker.  Attempting deeper search.")
            # Woo false loading time
            await asyncio.sleep(3)
            await bot.delete_message(sleeper)
            squareUpper = square.upper()
            searchList = []
            foundList = []
            returnList = []
            importList = []
            i = 0
            count = 0
            cursor.execute("SELECT * FROM testsquares")
            for row in cursor.fetchall():
                print(row[0])
                importList.append(row[0])
            searchedList = ", ".join(importList)
            print(importList[0])
            while i < len(importList):
                print(importList[i].upper())
                importListUpper = importList[i].upper()
                if importListUpper.find(squareUpper) != -1:
                    searchedList = wordlist.CONVERT[importListUpper]
                    foundList.append(searchedList)
                    returnList = ", ".join(foundList)
                    i += 1
                    count += 1
                else:
                    i += 1
            if count == 0:
                await bot.send_message(user, "`{}` is not currently being tracked.".format(square))
            if count == 1:
                cursor.execute("DELETE FROM testsquares WHERE square=?", (returnList, ))
                connection.commit()
                await bot.send_message(ctx.message.channel,"{} removed `{}` from the tracked list.".format(user.mention, returnList))
                print("---\n{} removed '{}' from the test channel tracker at {}.\n---".format(ctx.message.author, returnList,timeNow.strftime("%H:%M")))
            elif count >= 2:
                await bot.send_message(user, "Found the following {} matches: {}.".format(count, returnList))
    elif ctx.message.author.id in users.WHITELIST:
        cursor.execute("SELECT * FROM squares")
        for row in cursor.fetchall():
            thisList.append(row[0])
            if row[0] == square.capitalize():
                counter += 1
            else:
                counter += 0
        thatList = ", ".join(thisList)
        if counter == 1:
            cursor.execute("DELETE FROM squares WHERE square=?", (thatList,))
            connection.commit()
            await bot.send_message(ctx.message.channel, "{} removed `{}` from the tracked squares list.".format(user.mention, thatList))
            print("---\n{} removed '{}' from the live channel tracker at {}.\n---".format(ctx.message.author, thatList, timeNow.strftime("%H:%M")))
        elif counter >= 2:
            await bot.send_message(user, "Multiple matches found in the tracker: {}.".format(thatList))
        else:
            sleeper = await bot.send_message(ctx.message.channel, "Nothing found in the tracker.  Attempting deeper search...")
            # Woo false loading time
            await asyncio.sleep(3)
            await bot.delete_message(sleeper)
            squareUpper = square.upper()
            searchList = []
            foundList = []
            returnList = []
            importList = []
            i = 0
            count = 0
            cursor.execute("SELECT * FROM squares")
            for row in cursor.fetchall():
                print(row[0])
                importList.append(row[0])
            searchedList = ", ".join(importList)
            print(importList[0])
            while i < len(importList):
                print(importList[i].upper())
                importListUpper = importList[i].upper()
                if importListUpper.find(squareUpper) != -1:
                    searchedList = wordlist.CONVERT[importListUpper]
                    foundList.append(searchedList)
                    returnList = ", ".join(foundList)
                    i += 1
                    count += 1
                else:
                    i += 1
            if count == 0:
                await bot.send_message(user, "`{}` is not currently being tracked.".format(square))
            if count == 1:
                cursor.execute("DELETE FROM squares WHERE square=?", (returnList, ))
                connection.commit()
                await bot.send_message(ctx.message.channel,"{} removed `{}` from the tracked list.".format(user.mention, returnList))
                print("---\n{} removed '{}' from the live channel tracker at {}.\n---".format(ctx.message.author, returnList,timeNow.strftime("%H:%M")))
            elif count >= 2:
                await bot.send_message(user, "Found the following {} matches: {}.".format(count, returnList))
    else:
        await bot.send_message(user, "You don't have permission to remove tracked squares.")


@bot.command(pass_context=True, aliases=['sl'])
async def squarelist(ctx):
    """Sends a user a PM with the current tracked items."""
    # squares(square TEXT, department TEXT, time TEXT)
    user = ctx.message.author
    thisList = []
    counter = 0
    testbreakList = []
    if not ctx.message.channel.is_private:
        await bot.delete_message(ctx.message)
    if ctx.message.channel.id == users.testChannel:
        cursor.execute("SELECT * FROM testsquares")
        for row in cursor.fetchall():
            thisList.append("{} ({})".format(row[0], row[2]))
            if len(row[0]) > 0:
                counter += 1
            else:
                counter += 0
        if counter == 0:
            await bot.send_message(user, "Nothing in the tracker yet!")
        else:
            testbreakList = ", ".join(thisList)
            await bot.send_message(user, "Current test channel squares (chronological): {}.".format(testbreakList))
    else:
        cursor.execute("SELECT * FROM squares")
        for row in cursor.fetchall():
            thisList.append("{} ({})".format(row[0], row[2]))
            if len(row[0]) > 0:
                counter += 1
            else:
                counter += 0
        if counter == 0:
            await bot.send_message(user, "Nothing in the tracker yet!")
        else:
            testbreakList = ", ".join(thisList)
            await bot.send_message(user, "Current squares (chronological): {}.".format(testbreakList))


@bot.command(pass_context=True, aliases=['ssl'])
async def sortedsquarelist(ctx):
    """Sends a user a PM with the current tracked items in alphabetic order."""
    # squares(square TEXT, department TEXT, time TEXT)
    user = ctx.message.author
    thisList = []
    counter = 0
    testbreakList = []
    if not ctx.message.channel.is_private:
        await bot.delete_message(ctx.message)
    if ctx.message.channel.id == users.testChannel:
        cursor.execute("SELECT * FROM testsquares")
        for row in cursor.fetchall():
            thisList.append("{} ({})".format(row[0], row[2]))
            if len(row[0]) > 0:
                counter += 1
            else:
                counter += 0
        thisList.sort()
        if counter == 0:
            await bot.send_message(user, "Nothing in the tracker yet!")
        else:
            testbreakList = ", ".join(thisList)
            await bot.send_message(user, "Current test channel squares (alphabetical): {}.".format(testbreakList))
    else:
        cursor.execute("SELECT * FROM squares")
        for row in cursor.fetchall():
            thisList.append("{} ({})".format(row[0], row[2]))
            if len(row[0]) > 0:
                counter += 1
            else:
                counter += 0
        thisList.sort()
        if counter == 0:
            await bot.send_message(user, "Nothing in the tracker yet!")
        else:
            testbreakList = ", ".join(thisList)
            await bot.send_message(user, "Current squares (alphabetic): {}.".format(testbreakList))


@bot.command(pass_context=True, aliases=['break'])
@commands.cooldown(1, 30, commands.BucketType.channel)
async def breaklist(ctx):
    """Prints the current squares in alphabetic order in the current channel."""
    # squares(square TEXT, department TEXT, time TEXT)
    user = ctx.message.author
    thisList = []
    counter = 0
    testbreakList = []
    if not ctx.message.channel.is_private:
        await bot.delete_message(ctx.message)
    if ctx.message.channel.id == users.testChannel:
        cursor.execute("SELECT * FROM testsquares")
        for row in cursor.fetchall():
            thisList.append("{} ({})".format(row[0], row[2]))
            if len(row[0]) > 0:
                counter += 1
            else:
                counter += 0
        thisList.sort()
        if counter == 0:
            await bot.send_message(user, "Nothing in the tracker yet!")
        else:
            testbreakList = ", ".join(thisList)
            await bot.send_message(ctx.message.channel, "**The break list has a 30 second cooldown.**")
            await bot.send_message(ctx.message.channel, "Current test channel squares (alphabetized): {}.".format(testbreakList))
    else:
        cursor.execute("SELECT * FROM squares")
        for row in cursor.fetchall():
            thisList.append("{} ({})".format(row[0], row[2]))
            if len(row[0]) > 0:
                counter += 1
            else:
                counter += 0
        thisList.sort()
        if counter == 0:
            await bot.send_message(user, "Nothing in the tracker yet!")
        else:
            testbreakList = ", ".join(thisList)
            await bot.send_message(ctx.message.channel, "**The break list has a 30 second cooldown.**")
            await bot.send_message(ctx.message.channel, "Current squares (alphabetized): {}.".format(testbreakList))


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
    counter = 0
    if not ctx.message.channel.is_private:
        await bot.delete_message(ctx.message)
    if ctx.message.channel.id == users.testChannel:
        cursor.execute("SELECT * FROM testwinners")
        for row in cursor.fetchall():
            if row[1] == user_id:
                counter += 1
            else:
                counter += 0
        if counter > 0:
            cursor.execute("SELECT * FROM testwinners where id=?", (user_id, ))
            for row in cursor.fetchall():
                time = row[2]
            await bot.send_message(user, "You've already called bingo tonight @ {}.  Ask a mod to remove you from the list if you called it in error.".format(time))
        else:
            await bot.send_message(ctx.message.channel, "Congrats {} on Bingo!".format(user.mention))
            timenow = datetime.now()
            # testwinners(name TEXT, id TEXT, time TEXT)
            cursor.execute("INSERT INTO testwinners (name, id, time) VALUES(?, ?, ?)", (user.display_name, user_id, timenow.strftime("%I:%M %p")))
            connection.commit()
            print(">> {}({}) CALLED BINGO AT {} <<\n".format(user.display_name, user, timenow.strftime("%H:%M")))
    else:
        cursor.execute("SELECT * FROM winners")
        for row in cursor.fetchall():
            if row[1] == user_id:
                counter += 1
            else:
                counter += 0
        if counter > 0:
            cursor.execute("SELECT * FROM winners where id=?", (user_id,))
            for row in cursor.fetchall():
                time = row[2]
            await bot.send_message(user,
                                   "You've already called bingo tonight @ {}.  Ask a mod to remove you from the list if you called it in error.".format(
                                       time))
        else:
            await bot.send_message(ctx.message.channel, "Congrats {} on Bingo!".format(user.mention))
            timenow = datetime.now()
            # testwinners(name TEXT, id TEXT, time TEXT)
            cursor.execute("INSERT INTO winners (name, id, time) VALUES(?, ?, ?)",
                           (user.display_name, user_id, timenow.strftime("%I:%M %p")))
            connection.commit()
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
    thatList = []
    winnerCounter = 0
    if not ctx.message.channel.is_private:
        await bot.delete_message(ctx.message)
    if ctx.message.channel.id == users.testChannel:
        winners = cursor.execute("SELECT * FROM testwinners")
        # winners(name TEXT, id TEXT, time TEXT)
        for row in winners.fetchall():
            thatList.append("{} @ {}".format(row[0], row[2]))
            if len(row[0]) > 0:
                winnerCounter += 1
            else:
                winnerCounter += 0
        sortedWinners = ", ".join(thatList)
        if winnerCounter ==0:
            await bot.send_message(user, "No winners for {} yet!".format(startTime.strftime("%Y %B %d")))
        else:
            await bot.send_message(user, "Bingo winners for {}: {}".format(startTime.strftime("%Y %B %d"),sortedWinners))
    else:
        winners = cursor.execute("SELECT * FROM winners")
        # winners(name TEXT, id TEXT, time TEXT)
        for row in winners.fetchall():
            thatList.append("{} @ {}".format(row[0], row[2]))
            if len(row[0]) > 0:
                winnerCounter += 1
            else:
                winnerCounter += 0
        sortedWinners = ", ".join(thatList)
        if winnerCounter == 0:
            await bot.send_message(user, "No winners for {} yet!".format(startTime.strftime("%Y %B %d")))
        else:
            await bot.send_message(user,
                                   "Bingo winners for {}: {}".format(startTime.strftime("%Y %B %d"), sortedWinners))


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
        cursor.close()
        connection.close()
        await bot.logout()


@bot.command(pass_context=True)
async def bug(ctx, *bug : str):
    """Reports a bug to the #bugs channel in the dev Discord and creates a post on the bot subreddit."""
    user = ctx.message.author
    bug = " ".join(bug)
    bugTime = datetime.now()
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
    featTime = datetime.now()
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
    squareUpper = square.upper()
    searchList = []
    foundList = []
    returnList = []
    importList = []
    i = 0
    count = 0
    if ctx.message.channel.id == users.testChannel:
        cursor.execute("SELECT * FROM testsquares")
        for row in cursor.fetchall():
            importList.append(row[0])
        searchedList = ", ".join(importList)
        while i < len(importList):
            importListUpper = importList[i].upper()
            if importListUpper.find(squareUpper) != -1:
                searchedList = wordlist.CONVERT[importListUpper]
                foundList.append(searchedList)
                returnList = ", ".join(foundList)
                i += 1
                count += 1
            else:
                i += 1
            if count == 0:
                await bot.send_message(user, "`{}` is not being tracked.".format(square))
            if count == 1:
                cursor.execute("SELECT * FROM testsquares WHERE square=?",(returnList,))
                for row in cursor.fetchall():
                    timeNow = row[2]
                timemsg = await bot.send_message(ctx.message.channel, "`{}` was added at `{}`.".format(returnList, timeNow))
                await asyncio.sleep(5)
                await bot.delete_message(timemsg)
            elif count >= 2:
                await bot.send_message(user, "Multiple matches for `{}` found.  Please be more specific.".format(square))
    else:

        cursor.execute("SELECT * FROM squares")
        for row in cursor.fetchall():
            importList.append(row[0])
        searchedList = ", ".join(importList)
        while i < len(importList):
            importListUpper = importList[i].upper()
            if importListUpper.find(squareUpper) != -1:
                searchedList = wordlist.CONVERT[importListUpper]
                foundList.append(searchedList)
                returnList = ", ".join(foundList)
                i += 1
                count += 1
            else:
                i += 1
            if count == 0:
                await bot.send_message(user, "`{}` is not being tracked.".format(square))
            if count == 1:
                cursor.execute("SELECT * FROM squares WHERE square=?",(returnList,))
                for row in cursor.fetchall():
                    timeNow = row[2]
                timemsg = await bot.send_message(ctx.message.channel, "`{}` was added at `{}`.".format(returnList, timeNow))
                await asyncio.sleep(5)
                await bot.delete_message(timemsg)
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
        bingoCounter = 0
        winnerCounter = 0
        thisList = []
        thatList = []
        sortedList = []
        sortedSquares = []
        sortedBingo = []
        bingos = cursor.execute("SELECT * FROM squares")
        # squares(square TEXT, department TEXT, time TEXT)
        for row in bingos.fetchall():
            thisList.append("{} @ {} ({})".format(row[0], row[2], row[1]))
            if len(row[0]) > 0:
                bingoCounter += 1
            else:
                bingoCounter += 0
        winners = cursor.execute("SELECT * FROM winners")
        # winners(name TEXT, id TEXT, time TEXT)
        for row in winners.fetchall():
            thatList.append("{} @ {}".format(row[0], row[2]))
            if len(row[0]) > 0:
                winnerCounter += 1
            else:
                winnerCounter += 0
        if bingoCounter == 0:
            await bot.send_message(user, "There is nothing in the tracker to post.")
        if winnerCounter == 0:
            await  bot.send_message(user, "No one called bingo in Discord.")
        elif bingoCounter >= 1 and winnerCounter >= 1:
            sortedSquares = ", ".join(thisList)
            squaresSubmission = "Tonight's squares: {}.".format(sortedSquares)
            await bot.send_message(ctx.message.channel, squaresSubmission)
            sortedList.clear()
            sortedBingo = ", ".join(thatList)
            winnersSubmission = "Tonight's Discord Bingo winners: {}.".format(sortedBingo)
            await bot.send_message(ctx.message.channel, winnersSubmission)
            endTime = datetime.now()
            winnerFile = open('bingowinners.txt', 'a')
            winnerFile.write(endTime.strftime("\n\n%A, %d %B %Y\n"))
            winnerFile.write(sortedBingo)
            winnerFile.close()
            sortedList.clear()
            nightlyThread = reddit.submission(id=thread_id)
            squaresComment = nightlyThread.reply(squaresSubmission)
            reddit.comment(id=squaresComment).disable_inbox_replies()
            winnersComment = nightlyThread.reply(winnersSubmission)
            reddit.comment(id=winnersComment).disable_inbox_replies()
            await bot.send_message(ctx.message.channel, "Thread posted in: {}.\nSquares' comment: https://www.reddit.com{}.\nWinners' comment: https://www.reddit.com{}.".format(nightlyThread.shortlink,squaresComment.permalink,winnersComment.permalink))
            print("### Thread posted at: {}.\nSquares' comment: https://www.reddit.com{}.\nWinners' comment: https://www.reddit.com{}. ###".format(nightlyThread.shortlink,squaresComment.permalink,winnersComment.permalink))
            cursor.execute("DROP TABLE squares")
            connection.commit()
            cursor.execute("CREATE TABLE IF NOT EXISTS squares(square TEXT, department TEXT, time TEXT)")
            connection.commit()
            cursor.execute("DROP TABLE winners")
            connection.commit()
            cursor.execute("CREATE TABLE IF NOT EXISTS squares(square TEXT, department TEXT, time TEXT)")
            connection.commit()
    else:
        await bot.send_message(user, "You don't have permission to run the end of the night report")


'''@bot.event
async def on_command_error(error, ctx):
    channel = ctx.message.channel
    user = ctx.message.author
    if isinstance(error, commands.MissingRequiredArgument):
        if not channel.is_private:
            await bot.delete_message(ctx.message)
        await bot.send_message(user, "You missed a required argument.  The command you sent was: `{}`.".format(ctx.message.content))
        raise error
    elif isinstance(error, errors.NotFound):
        if not channel.is_private:
            await bot.delete_message(ctx.message)
        await bot.send_message(user, "Something bad happened and I don't know what.")
        raise error
    elif isinstance(error, er.CommandOnCooldown):
        if not channel.is_private:
            await bot.delete_message(ctx.message)
        raise error
        errormsg = await bot.send_message(ctx.message.channel, "That command is still on cooldown.  Try again in {:.2f} seconds.".format(error.retry_after))
        await asyncio.sleep(error.retry_after)
        await bot.delete_message(errormsg)
    else:
        if not channel.is_private:
            await bot.delete_message(ctx.message)
        await bot.send_message(user, "You did something wrong.  The command you sent was: `{}`.".format(ctx.message.content))
        raise error
        print(error)'''


bot.run(users.BOT_TOKEN)
