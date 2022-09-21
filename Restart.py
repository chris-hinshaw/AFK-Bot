from discord.ext.commands import Bot
from shutil import copy, move
import discord
import os
import asyncio
import hashlib
import psutil

BOT_PREFIX = ("!", ".", "?")
TOKEN = 'TOKEN'
UA_PASSWORD = 'PASSWORD'
DOWN_TIME = 30
RESTART_DELAY = 10
MAX_ACCOUNTS = 5 ##Max accounts a user can have
LOCATION = os.getcwd() + '\\'
UA_ID = 0 ##DISCORD DEV NUM
RESTART_CHANNEL_ID = ##DISCORD CHANNEL ID

client = Bot(command_prefix=BOT_PREFIX)
client.remove_command('help')


class RestartBot():
    queue = []
    crash_queue = []


def close_processes(author):
    return (
        os.system('C:\Windows\System32\cmd.exe /c C:\Windows\System32\TASKKILL.exe /F /IM ' + str(author.id) + '.exe'))


async def add_alt(ctx, file_name, username, password): ##adds an account to the discord user
    await client.change_presence(activity=discord.Game(name='Account Adder'))
    await ctx.channel.send('Adding account...')

    with open(file_name, 'a') as alts:
        alts.write(username + ' ' + password + '\n')

    await ctx.channel.send(
        'Added account to ' + ctx.message.author.mention + "'s alts."
    )

@client.command(name='help',
                aliases=['Help', 'h', 'H']) ##creates alternate methods of type the help command
async def help(ctx):
    await client.change_presence(activity=discord.Game(name='Helper'))
    embed = discord.Embed(title='Alt Restarter - Help:', color=0x0000ff)
    embed.add_field(name='[.|?|!]restart',
                    value='Restarts alts that are currently running.',
                    inline=False
                    )
    embed.add_field(name='[.|?|!]kill',
                    value='Kills alts that are currently running.',
                    inline=False
                    )
    embed.add_field(name='[.|?|!]add',
                    value='Adds an account to a users account list. If you are over the limit, a password is required when messaging the bot but if you are in a restart channel only the ' +
                    "'UA'" + ' role is required. Usage: [.|?|!]add username password [password].',
                    inline=False
                    )
    embed.add_field(
        name='[.|?|!]delete',
        value='Removes an account from a users account list. Index given by list function. Usage: [.|?|!]delete index.',
        inline=False
    )
    embed.add_field(
        name='[.|?|!]list',
        value='Lists accounts in a users account list.',
        inline=False
    )


def encrypt_string(hash_string):
    return hashlib.md5(hash_string.encode()).hexdigest()[::-1]


@client.command(name='getpass',
                aliases=['getpassword', 'gp', 'GP']) ##returns password
async def getpass(ctx):
    await ctx.message.author.send(encrypt_string(str(ctx.author.id)))


async def restart_user_alts(ctx, target):
    await client.change_presence(activity=discord.Game(name='Alt Restarter'))
    file_name = 'UserAlts\\' + str(target.id) + '.txt'

    if not os.path.isfile(str(target.id) + '.exe'):
        copy(LOCATION + 'MinecraftClient.exe', LOCATION + 'temp')
        move(
            LOCATION + 'temp\\MinecraftClient.exe',
            LOCATION + str(target.id) + '.exe'
        )

    if os.path.isfile(file_name):
        await ctx.channel.send('Logging alts...')

        if close_processes(target) == 0:
            await ctx.channel.send('Alts killed.')
            await ctx.channel.send('Waiting ' + str(DOWN_TIME) + ' seconds...')
            await asyncio.sleep(DOWN_TIME)
        else:
            await ctx.channel.send('No alts killed.')

        count = 0
        add_list = []
        first_time = True

        with open(file_name, 'r') as alts:
            for line in alts:
                info = line.split(' ')
                count += 1
                add_list.append(
                    [
                        'start /min ' + str(target.id) + '.exe ' + info[0]
                        + ' ' + info[1].rstrip() + ' cosmicpvp.me' + ' '
                        + str(target.id), info[0]])

        if count == 0:
            await ctx.channel.send('All alts removed. Use [.|?|!]add')
        else:
            for a in add_list:
                if(first_time):
                    first_time = False
                else:
                    await asyncio.sleep(RESTART_DELAY)

                os.system(a[0])
                await ctx.channel.send('Restarted ' + a[1])

            await ctx.channel.send('Restarted ' + target.mention + "'s alts.")
    else:
        await ctx.channel.send('No alts created yet. Use [.|?|!]help')


async def add_to_queue(ctx, target):
    if target.id not in RestartBot.queue:
        RestartBot.queue.append(target.id)
        await ctx.channel.send('Adding to queue...')

        while RestartBot.queue[0] != target.id:
            await asyncio.sleep(1)

        await restart_user_alts(ctx, target)
        del RestartBot.queue[0]
    else:
        await ctx.channel.send('Already in queue.')


@client.command(name='restart',
                aliases=['r', 'Restart', 'relog', 'Relog', 're'])
async def restart(ctx, user: discord.Member = None):
    if user == None:
        await add_to_queue(ctx, ctx.message.author)
    else:
        if UA_ID in [role.id for role in ctx.message.author.roles]:
            await add_to_queue(ctx, user)
        else:
            await ctx.channel.send('Insufficient permissions.')


@client.command(name='add',
                aliases=['a', 'Add', 'new', 'New', 'n'])
async def add(ctx, username, password, ua_password=None):
    file_name = 'UserAlts\\' + str(ctx.message.author.id) + '.txt'
    line_count = 0

    if not os.path.isfile(file_name):
        with open(file_name, 'a'):
            pass

    with open(file_name, 'r') as read_alts:
        line_count = len(read_alts.readlines())

    if line_count > MAX_ACCOUNTS - 1:
        if(ctx.message.guild is None and ua_password is None):
            await ctx.channel.send(
                'You are over the alt limit. Please input a password as an argument.'
            )
        elif(ctx.message.guild is None and ua_password != UA_PASSWORD):
            await ctx.channel.send('Incorrect password.')
        elif(ctx.message.guild is None):
            await add_alt(ctx, file_name, username, password)
        else:
            if UA_ID in [role.id for role in ctx.message.author.roles]:
                await add_alt(ctx, file_name, username, password)
            else:
                await ctx.channel.send('You are over the alt limit.')
    else:
        await add_alt(ctx, file_name, username, password)


async def kill_user_alts(channel, target):
    await client.change_presence(activity=discord.Game(name='Account Killer'))
    await channel.send('Logging alts...')

    if close_processes(target) == 0:
        await channel.send('Alts killed.')
    else:
        await channel.send('No alts killed.')


async def kill_all_user_alts(channel):
    await client.change_presence(activity=discord.Game(name='Account Killer'))
    await channel.send('Logging all alts...')

    console_client_processes = []

    for process in psutil.process_iter():
        name = process.name().strip('.exe')

        if name.isdigit() and len(name) == 18:
            console_client_processes.append(process)

    count = 0

    for proc in console_client_processes:
        try:
            proc.kill()
            count += 1
        except psutil.NoSuchProcess:
            pass

    await channel.send('Logged ' + str(count) + ' alts.')


@client.command(name='kill',
                aliases=['k', 'Kill', 'log', 'Log', 'die', 'Die', 'hitoff'])
async def kill(ctx, user: discord.Member = None):
    if user == None:
        await kill_user_alts(ctx.channel, ctx.message.author)
    else:
        if UA_ID in [role.id for role in ctx.message.author.roles]:
            await kill_user_alts(ctx.channel, user)
        else:
            await ctx.channel.send('Insufficient permissions.')


@client.command(name='killall',
                aliases=['ka', 'Killall', 'logall', 'Logall', 'hitoffeveryone'])
async def killall(ctx):
    if UA_ID in [role.id for role in ctx.message.author.roles]:
        await kill_all_user_alts(ctx.channel)
    else:
        await ctx.channel.send('Insufficient permissions.')


async def list_user_alts(channel, target):
    await client.change_presence(activity=discord.Game(name='Account Lister'))
    file_name = 'UserAlts\\' + str(target.id) + '.txt'

    if os.path.isfile(file_name):
        with open(file_name, 'r') as alts:
            alt_list = alts.read().splitlines()

        chunks = [alt_list[x:x + 25] for x in range(0, len(alt_list), 25)]
        count = 1

        for chunk in chunks:
            embed = discord.Embed(title='Accounts:', color=0x0000ff)

            for line in chunk:
                embed.add_field(
                    name=str(count),
                    value=line[:line.find(' ')],
                    inline=False)
                count += 1

            await channel.send(embed=embed)

        if count == 1:
            await channel.send('All alts removed. Use [.|?|!]add')
    else:
        await channel.send('No alts added. Use [.|?|!]help')


@client.command(name='list',
                aliases=['List', 'l', 'L', 'show', 'Show'])
async def list(ctx, user: discord.Member = None):
    if user is None:
        await list_user_alts(ctx.channel, ctx.message.author)
    else:
        if UA_ID in [role.id for role in ctx.message.author.roles]:
            await list_user_alts(ctx.channel, user)
        else:
            await ctx.channel.send('Insufficient permissions.')


@client.command(name='delete',
                aliases=['Delete', 'd', 'D', 'remove', 'Remove'])
async def delete(ctx, target):
    await client.change_presence(activity=discord.Game(name='Account Deleter'))
    continue_bool = True

    try:
        target_int = int(target)
    except():
        continue_bool = False
        await ctx.channel.send('Invalid argument.')

    if continue_bool:
        removed = False
        file_name = 'UserAlts\\' + str(ctx.message.author.id) + '.txt'
        lines = []

        with open(file_name, 'r') as read_alts:
            lines = read_alts.readlines()

        count = 1

        with open(file_name, 'w') as alts:
            for line in lines:
                if(count != target_int):
                    alts.write(line)
                else:
                    removed = True

                count += 1

        if removed:
            await ctx.channel.send('Alt removed.')
        else:
            await ctx.channel.send('No alt removed.')


async def restart_queue():
    await client.wait_until_ready()

    while not client.is_closed():
        try:
            lines = []
            with open('restartqueue.txt', 'r') as fl:
                lines = fl.readlines()

            with open('restartqueue.txt', 'w') as foo:
                pass

            for line in lines:
                info = line.split(' ')
                await asyncio.sleep(30)
                os.system('start /min ' + info[2].rstrip() + '.exe ' +
                          info[0] + ' ' + info[1] + ' cosmicpvp.me '
                          + info[2].rstrip()
                          )

            await asyncio.sleep(1)
        except Exception as e:
            print(e)
            await asyncio.sleep(1)


client.loop.create_task(restart_queue())
client.run(TOKEN)
