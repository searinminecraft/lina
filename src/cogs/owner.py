import voltage
from voltage.ext import commands

import sys

def setup(client: commands.CommandsClient) -> commands.Cog:

    owner = commands.Cog(
        name = 'Owner Only',
        description = f'Only for my lovely creator, {client.user.owner.name}.'
    )

    @commands.is_owner()
    @owner.command('loadcog', 'Loads a cog.')
    async def loadcog(ctx: commands.CommandContext, cog: str = None):
        if cog is None:
            return await ctx.reply('Please, specify a cog!')

        client.add_extension(f'cogs.{cog}')
        await ctx.reply(f'Successfully loaded cog {cog}')

    @commands.is_owner()
    @owner.command('unloadcog', 'Unloads a cog.')
    async def unloadcog(ctx: commands.CommandContext, cog: str = None):
        if cog is None:
            return await ctx.reply('Please, specify a cog!')

        if cog == 'owner':
            return await ctx.reply('Are u stupid?')

        client.remove_extension(f'cogs.{cog}')
        await ctx.reply(f'Successfully unloaded cog {cog}')

    @commands.is_owner()
    @owner.command('reloadcog', 'Reloads a cog.')
    async def reloadcog(ctx: commands.CommandContext, cog: str = None):
        if cog is None:
            return await ctx.reply('Please, specify a cog!')

        client.reload_extension(f'cogs.{cog}')
        await ctx.reply(f'Successfully reloaded cog {cog}')

    @commands.is_owner()
    @owner.command('shutdown', 'Shutdown the bot.')
    async def shutdown(ctx: commands.CommandContext):
        await ctx.reply('Shutting down.')
        sys.exit(1)

    return owner
