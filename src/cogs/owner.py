from voltage.ext.commands import (
    CommandsClient,
    Cog,
    CommandContext,
    is_owner
)

from voltage import (
    DMChannel,
    SendableEmbed
)

from stk import authentication
from stk.http import STKHTTPError
import config
import globals


def setup(client: CommandsClient) -> Cog:

    _ = Cog("Owner Only", "Only the owner can execute these.")

    @is_owner()
    @_.command(description="Reauthenticate SuperTuxKart account")
    async def reauth(ctx: CommandContext):

        msg = await ctx.reply("Waiting for server...")
        try:
            await authentication.authenticate(
                config.getConfig("username"),
                config.getConfig("password")
            )
        except STKHTTPError as e:
            return await msg.edit(
                f"Unable to reauthenticate: Server error: {e}")
        except Exception as e:
            return await msg.edit(
                f"Unable to reauthenticate: {e.__class__.__name__}: {e}")

        await msg.edit("Successfully reauthenticated.")

    @is_owner()
    @_.command(description="Switch to another STK account")
    async def switchaccount(ctx: CommandContext, username: str, password: str):
        if isinstance(ctx.channel, DMChannel):
            msg = await ctx.reply(embed=SendableEmbed(
                description=f"Attempting to log in as {username}",
                color=globals.accentcolor
            ))

            try:
                await authentication.authenticate(
                    username, password
                )

                config.setConfig("username", username)
                config.setConfig("password", password)
            except STKHTTPError as e:
                return await msg.edit(embed=SendableEmbed(
                    description=f"Unable to login! {e}",
                    color=globals.accentcolor
                ))
            except Exception as e:
                return await msg.edit(embed=SendableEmbed(
                    description=f"Internal error! {e.__class__.__name__}: {e}",
                    color=globals.accentcolor
                ))
            return await msg.edit(embed=SendableEmbed(
                description=f"Successfully logged in as {username}",
                color=globals.accentcolor
            ))
        else:
            try:
                await ctx.delete()
            except Exception:
                pass

            return await ctx.send(embed=SendableEmbed(
                description="Please run this in my DM to prevent revealing sensetive information.",
                color=globals.accentcolor
            ))

    @is_owner()
    @_.command('loadcog', 'Loads a cog.')
    async def loadcog(ctx: CommandContext, cog: str = None):
        if cog is None:
            return await ctx.reply(embed=SendableEmbed(
                description="Specify a cog.",
                color=globals.accentcolor
            ))

        client.add_extension(f'cogs.{cog}')
        await ctx.reply(embed=SendableEmbed(
            description=f'Successfully loaded cog {cog}',
            color=globals.accentcolor
        ))

    @is_owner()
    @_.command('unloadcog', 'Unloads a cog.')
    async def unloadcog(ctx: CommandContext, cog: str = None):
        if cog is None:
            return await ctx.reply(embed=SendableEmbed(
                description='Please, specify a cog!',
                color=globals.accentcolor
            ))

        if cog == 'owner':
            return await ctx.reply(embed=SendableEmbed(
                description='Are u stupid?',
                color=globals.accentcolor
            ))

        client.remove_extension(f'cogs.{cog}')
        await ctx.reply(embed=SendableEmbed(
            description=f'Successfully unloaded cog {cog}',
            color=globals.accentcolor
        ))

    @is_owner()
    @_.command('reloadcog', 'Reloads a cog.')
    async def reloadcog(ctx: CommandContext, cog: str = None):
        if cog is None:
            return await ctx.reply(embed=SendableEmbed(
                description='Please, specify a cog!',
                color=globals.accentcolor
            ))

        client.reload_extension(f'cogs.{cog}')
        await ctx.reply(embed=SendableEmbed(
            description=f'Successfully reloaded cog {cog}',
            color=globals.accentcolor
        ))

    return _
