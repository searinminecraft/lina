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
    @_.command(description = "Reauthenticate SuperTuxKart account")
    async def reauth(ctx: CommandContext):

        msg = await ctx.reply("Waiting for server...")
        try:
            await authentication.authenticate(
                config.getConfig("username"),
                config.getConfig("password")
            )
        except STKHTTPError as e:
            return await msg.edit(f"Unable to reauthenticate: Server error: {e}")
        except Exception as e:
            return await msg.edit(f"Unable to reauthenticate: {e.__class__.__name__}: {e}")

        await msg.edit("Successfully reauthenticated.")

    @is_owner()
    @_.command(description="Switch to another STK account")
    async def switchaccount(ctx: CommandContext, username: str, password: str):
        if isinstance(ctx.channel, DMChannel):
            msg = await ctx.reply(embed=SendableEmbed(
                description = f"Attempting to log in as {username}",
                color = globals.accentcolor
            ))

            try:
                await authentication.authenticate(
                    username, password
                )

                config.setConfig("username", username)
                config.setConfig("password", password)
            except STKHTTPError as e:
                return await msg.edit(embed=SendableEmbed(
                    description = "Unable to login! {e}",
                    color = globals.accentcolor
                ))
            except Exception as e:
                return await msg.edit(embed=SendableEmbed(
                    description = f"Internal error! {e.__class__.__name__}: {e}",
                    color = globals.accentcolor
                ))
            return await msg.edit(embed=SendableEmbed(
                description = f"Successfully logged in as {username}",
                color = globals.accentcolor
            ))
        else:
            try:
                await ctx.delete()
            except:
                pass

            return await ctx.send(embed=SendableEmbed(
                description = "Please run this in my DM to prevent revealing sensetive information.",
                color = globals.accentcolor
            ))


    return _
