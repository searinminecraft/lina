from voltage.ext.commands import (
    CommandsClient,
    CommandContext,
    Cog,
    is_owner
)
from voltage import Channel, SendableEmbed
from config import getConfig
import globals

def setup(client: CommandsClient) -> Cog:

    _ = Cog("Configuration", "Configure me to your heart's desire.")

    @is_owner
    @_.command(description = "Set-up a channel to show updating online players.")
    async def setonlinechannel(ctx: CommandContext, channel: Channel = None):
        if channel is None:
            await globals.pgconn.execute("UPDATE lina_conf SET onlinechannel = NULL WHERE serverid = $1", ctx.server.id)
            return await ctx.reply(embed=SendableEmbed(
                description = "Successfully unset online players channel.",
                color = getConfig("accentcolor")
            ))

        await globals.pgconn.execute("UPDATE lina_conf SET onlinechannel = $1 WHERE serverid = $2", channel.id, ctx.server.id)
        await ctx.reply(embed=SendableEmbed(
            description = f"Successfully set online players channel to <#{channel.id}>. It should take a few seconds before the online players list shows up.",
            color = getConfig("accentcolor")
        ))


    return _
