BOT_TOKEN = "Mzc3MDM4NzI1Mjg2MTk5Mjk2.DRePBQ.Cw2qrmPlsZo09dAyyg6aFvuOzjc"
defaultStatus = "Bingo Bot"
defaultChannel = "392157063502888962"
testChannel = "392120898909634561"
bugChannel = "392439244309921804"
featChannel = "392427109009850389"

#All Admins/Mods as of 17 December 2017
BizarroRick = "86799714300743680"
YouAllAreDisgraceful = "338859904062455808"
AlmaLlama6 = "386328247081893891"
SteelPenguin71 = "196376759996907521"
Vinto = "230784158853496843"
Dude = "105431077492899840"
TexanPride = "341403291466334218"

#Most active Bingo moderators
Bwana = "348629137080057878"
Fpreston = "345739121571921939"


WHITELIST = {
    BizarroRick,
    YouAllAreDisgraceful,
    AlmaLlama6,
    SteelPenguin71,
    Vinto,
    Dude,
    TexanPride,
    Bwana,
    Fpreston
}


DEPARTMENTS = {
    'RCSD': "Richland County Sheriff's Department",
    'PCSD': "Pasco County Sheriff's Department",
    'EPPD': "El Paso Police Department",
    'UHP': "Utah Highway Patrol",
    'PCSO': "Pinal County Sheriff's Office",
    'CCSO': "Clark County Sheriff's Office",
    'SCSO': "Spokane County Sheriff's Office",
    'JPD': "Jeffersonville Police Department",
    'LCSO': "Lake County Sheriff's Office",
    'STUDIO': "In Studio",
    'OTHER': "Other"
}

# @bot.command(pass_context=True, aliases=['sr'])
# async def setrole(ctx, user: str, role: str):
#     """Add a role to a user.  Usage "setrole NAME roleName"  >>RESTRICTED USE<<"""
#     if not ctx.message.channel.is_private:
#         await bot.delete_message(ctx.message)
#     if user or role is None:
#         pass
#     if ctx.message.author.id in users.WHITELIST:
#         user = discord.utils.get(ctx.message.server.members, name=user)
#         userRole = discord.utils.get(ctx.message.server.roles, name=role)
#         sroles = discord.utils.find(lambda m: m.name == role, ctx.message.server.roles)
#         checked = 0
#         if str(sroles) == str(role):
#             checked += 1
#         else:
#             checked += 0
#         if checked == 1:
#             await bot.add_roles(user, userRole)
#             tstamp = datetime.datetime.now()
#             print("{} made {} a {}.".format(ctx.message.author,user,role))
#             await bot.send_message(ctx.message.channel, "{} is now a **{}**".format(user.mention, userRole))
#     else:
#         await bot.say("{} you don't have permission to do that.".format(ctx.message.author.mention))
