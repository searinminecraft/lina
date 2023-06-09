import voltage
from voltage.ext import commands
import subprocess
import random
import asyncio
import time
from dotenv import load_dotenv, dotenv_values

load_dotenv()

accent = dotenv_values()['accent']

def setup(client) -> commands.Cog:
    misc = commands.Cog(
        'Miscellaneous',
        'Random stuff :yed:'
    )
    
    @misc.command()
    async def version(ctx: commands.CommandContext):
        """Version reporter"""
        await ctx.send(embed=voltage.SendableEmbed(
            title = client.user.name,
            description = f'{client.user.name} is powered by Voltage. Version {voltage.__version__}',
            color = accent,
            icon_url = client.user.display_avatar.url
    ))

    @misc.command('neofetch', 'Outputs the neofetch of where the bot is running.', ['btw'])
    async def neofetch(ctx: commands.CommandContext):
        output = subprocess.run(['neofetch', '--stdout'], stdout=subprocess.PIPE).stdout.decode('utf-8')

        embed = voltage.SendableEmbed(
            title = 'neofetch',
            description = f"""```
{output}
```""",
            color = accent
        )

        await ctx.send(embeds=[embed])


    return misc
