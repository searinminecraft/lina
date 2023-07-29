import voltage
from voltage.ext import commands

import sys
import json

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

    @commands.is_owner()
    @owner.command(description = 'Manually add an addon entry to database (for unknown tracks)')
    async def addAddonEntry(ctx: commands.CommandContext, id: str, name: str, uploader: str, designer: str, file: str, image: str):
        with open('data/addons.json', 'r') as f:
            data = json.load(f)


        data[id] = {
            "id": id,
            "name": name.replace("\"", ""),
            "file": file,
            "date": "0",
            "uploader": uploader,
            "designer": designer,
            "description": 'Manually added entry',
            "image": image,
            "format": "7",
            "revision": "0",
            "status": "0",
            "size": 1,
            "min-include-version": "",
            "max-include-version": "",
            "license": "",
            "image-list": "",
            "rating": "3"
        }

        with open('data/addons.json', 'w') as f:
            json.dump(data, f, indent=2)

        return await ctx.send('Successfully added entry.')

    return owner
