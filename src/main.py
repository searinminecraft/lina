from voltage.ext.commands import (
    CommandsClient,
    HelpCommand,
    Command,
    CommandContext,
    Cog
)
from voltage import (
    SendableEmbed,
    Message,
    Server
)
from voltage.errors import VoltageException
import globals

globals.init()

from stk import authentication
from stk.http import STKHTTPError
from stk.polling import poll
from stk.onlineloop import onlineloop
from stk.addondb import updateDb
from status import statusloop
from online import updateChannels 
from log import log
import config
import asyncio
import asyncpg
import traceback
import sys
import random

class Help(HelpCommand):
    async def send_help(self, ctx: CommandContext):

        embed = SendableEmbed(
            title=f"Help for {self.client.user.name}",
            description=f"Use `{self.client.prefix}help <command>` to get help for a specific command.\n",
            icon_url=self.client.user.display_avatar.url,
            color=globals.accentcolor
        )

        text = "## No category\n"

        for command in self.client.commands.values():

            if command.cog is None:

                text += f"#### `{command.name}`\n"

        text += "\n"

        for cog in self.client.cogs.values():

            text += f"## {cog.name}\n"
            text += f"{cog.description if cog.description is not None else '(no description)'}\n\n"

            for command in cog.commands:

                text += f"* `{command.name}`\n"

            text += "\n"

        if embed.description:

            embed.description += text

        await ctx.reply(embed=embed)

    async def send_command_help(self, ctx: CommandContext, command: Command):

        embed = SendableEmbed(
            title=f"Help for command {command.name}",
            color=globals.accentcolor,
            icon_url=self.client.user.display_avatar.url
        )

        text = "## Description:\n"
        text += f"{command.description if command.description else '(no description)'}\n\n"
        text += "## Usage:\n"
        text += f"`{ctx.prefix}{command.usage}`\n\n"
        text += "## Aliases:\n"
        text += f"{', '.join(command.aliases) if command.aliases else '(no aliases)'}"

        embed.description = text

        await ctx.reply(embed=embed)

    async def send_cog_help(self, ctx: CommandContext, cog: Cog):
        embed = SendableEmbed(
            title=f"Help for cog: {cog.name}",
            color=globals.accentcolor,
            icon_url=self.client.user.display_avatar.url
        )

        text = ""
        text += "## Description\n"
        text += f"{cog.description if cog.description else '(no description)'}\n\n"

        text += "## Commands\n"
        text += ", ".join([x.name for x in cog.commands])

        embed.description = text

        await ctx.reply(embed=embed)

    async def send_not_found(self, ctx: CommandContext, target: str):
        return await ctx.reply(embed=SendableEmbed(
            description=f"Command {target} not found...",
            color=globals.accentcolor
        ))


client = globals.client = CommandsClient(
    config.getConfig('prefix'),
    help_command=Help)


@client.listen('ready')
async def on_ready():

    import os

    try:
        log(
            'Auth',
            f"Attempting to authenticate STK account {globals.username}")
        await authentication.authenticate(globals.username, globals.password)
    except STKHTTPError as e:
        log('Auth', f'Unable to authenticate: {e}')
        sys.exit(1)

    log('Auth', f'Successfully logged in as {globals.username}!')

    try:
        log("DB", f"Connecting to {config.getConfig('postgres_conn')}")
        globals.pgconn = await asyncpg.connect(
            config.getConfig('postgres_conn'))
    except Exception as e:
        log("DB", f"Unable to connect! {e.__class__.__name__}: {e}")
        sys.exit(1)
    else:
        log("DB", f"Connected to {config.getConfig('postgres_conn')}!")
        globals.prepared_select = await globals.pgconn.prepare("""
SELECT username, LOWER(country) AS country,
date, server_name, LOWER(server_country) AS server_country FROM stk_seen
WHERE username ILIKE $1 GROUP BY username FETCH FIRST 1 ROW ONLY;
""")

        globals.prepared_addc = await globals.pgconn.prepare("""
INSERT INTO stk_seen (username, date, server_name, server_country)
VALUES ($1, now() at time zone 'utc', $2, lower($3))
ON CONFLICT (username) DO UPDATE SET
date = now() at time zone 'utc', server_name = $2, server_country = lower($3);
""")

        globals.prepared_add = await globals.pgconn.prepare("""
INSERT INTO stk_seen (username, country, date, server_name, server_country)
VALUES ($1, lower($2), now() at time zone 'utc', $3, lower($4))
ON CONFLICT (username) DO UPDATE SET
country = lower($2), date = now() at time zone 'utc',
server_name = $3, server_country = lower($4);
""")
        globals.prepared_ptrack_get = await globals.pgconn.prepare(
            "SELECT id FROM lina_ptrack;")
        globals.prepared_ptrack_query = await globals.pgconn.prepare(
            "SELECT usernames FROM lina_ptrack where id = $1;")

    for file in os.listdir('src/cogs'):
        if file.endswith('.py'):
            try:
                client.add_extension(f'cogs.{file[:-3]}')
                log('Init', f"Loaded {file}")
            except Exception as e:
                log('Init',
                    f"Error loading {file}: {e.__class__.__name__}: {e}")
                log('Init', traceback.format_exc())

    splash = f"""

                ..
         .                .
       .                   .
      .      .. .c  .       '
     .      ;: .l.....       .
    .      c;....    .;'';'  ..
    :     :':col:.;lo,c,;..:xxo'        linaSTK version {globals.version}
    .     l;.'Oc.,,c:.. :.xxo:::c,      Authenticated to STK as: {globals.username}
   .      l             '   'ccc::l
   .      :     ...     ;     :c::c
   .      ,   .     .   ,     ;::cc     Username: {str(client.user)}
          :  .c.....lc.  '    l ccc     ID: {client.user.id}
    .     ;.'dddddddoollco    , ,cc
     .    cccc::ccccccc::cd   o .cc
    """

    for i in splash.splitlines():
        log("Bot", i)

    asyncio.create_task(poll())
    asyncio.create_task(onlineloop())
    asyncio.create_task(statusloop())
    asyncio.create_task(updateChannels())
    asyncio.create_task(updateDb())

    globals.addons = await globals.pgconn.fetch("SELECT * FROM addons;")


@client.listen('server_create')
async def on_join(server: Server):
    try:
        await globals.pgconn.execute(
            "INSERT INTO lina_conf (serverid) VALUES $1;", server.id)
    except Exception:
        pass

@client.listen('message')
async def on_message(message: Message):
    if message.content == client.user.mention:
        return await message.reply(embed=SendableEmbed(
            title=random.choice([
                    "Haiiiii!",
                    "Who ping?!?",
                    "Hewwo :3",
                    "You pinged me!",
                    "Hey there!",
                    "Nice to meet you!"
                ]),
            description=f"My prefix is `{client.prefix}`. Type `{client.prefix}help` to get started!",
            icon_url=client.user.display_avatar.url,
            color=globals.accentcolor
        ))

    await client.handle_commands(message)

@client.error('message')
async def on_error(error: Exception, message: Message):

    log("ErrorHandler",
        f"Exception occurred: {error.__class__.__name__}: {error}")
    traceback.print_exc()

    if isinstance(error, STKHTTPError):
        return await message.reply(embed=SendableEmbed(
            description=f"STK server returned error: {error}",
            color=globals.accentcolor
        ))

    if isinstance(error, VoltageException):
        return await message.reply(embed=SendableEmbed(
            description=f"Library returned error: {error.__class__.__name__}: {error}",
            color=globals.accentcolor
        ))

client.run(config.getConfig('token'), banner=False)
