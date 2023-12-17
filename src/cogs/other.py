from voltage.ext.commands import (
    CommandsClient,
    Cog,
    CommandContext
)

from voltage import (
    SendableEmbed,
    File,
    User
)

import random
import traceback
from datetime import datetime
import globals
from log import log
from utils import convertAddonIdToName


def setup(client: CommandsClient) -> Cog:

    _ = Cog("Other", "Other stuff")

    @_.command(name="youravatariscute")
    async def simpdetector(ctx: CommandContext):

        responses = [
            "awww thanks <3",
            "searinminecraft's irl bff drew my avatar, but thanks i guess...",
            "I'm a machine. You don't have to say that!",
            "You find my avatar attractive huh?",
            "Thanks OwO",
            ":3",
            "aeasus",
            "simp detected",
            "???",
            "I don't know what to say...",
            "AAAAAAAAAAAAAAAAAAAAA",
            "I love you",
            # "$128\\sqrt{e980}$!",
            "Don't.",
            "Don't. Simp. On. A. Machine.",
            "{user} should have listened to DernisNW's advice: \"Never simp on a machine\"."
        ]

        await ctx.reply(str(random.choice(responses)).format(user=ctx.author.name))

    @_.command()
    async def youravatarsucks(ctx: CommandContext):

        responses = [
            "Understandable.",
            "WOW",
            "Why :(",
            "I'm gonna tell searinminecraft to tell his IRL best friend that you said so",
            "But searinminecraft's IRL best friend's drawings is cool...",
            "ubfjenrojnadfjo ndsgoj n",
            "...",
            "I'm just a machine anyway.",
            "None",
            "Shutting down the bot...",
            ":cry:",
            "no u!",
            "ok then why did u say my avatar is cute earlier?",
            "Error 403 - You do not have permission to say my avatar sucks.",
            "List of of people that asked: ... (end)",
            "I hate you now.",
            "~~You are now blacklisted from using the bot~~",
            "but.. but.. but.. but.. but.. but..",
            "Self destruction initiated.",
            "At least it's hand-made and not stolen like yours.",
            "I didn't ask for your opinion, human.",
            "Fsck you!",
            "See if I care",
            "It's definitely better than yours lmao.",
            "Hey, at least its not AI generated",
            "Go /sbin/fsck yourself. Oh wait, you're already fscked! HAHAHAHAHA"
        ]

        await ctx.reply(random.choice(responses))

    @_.command(description="Show bot statistics")
    async def stats(ctx: CommandContext):
        return await ctx.reply(embed=SendableEmbed(
            title="Bot statistics",
            icon_url=client.user.display_avatar.url,
            description=f"""**Bot started:** <t:{int(globals.startTime.timestamp())}:F>, <t:{int(globals.startTime.timestamp())}:R>
**Servers:** {len(client.servers)}
**Cached Users:** {len(client.users)}
**Online Players:** {len(globals.onlinePlayers)}
**Players in STK Seen Database:** {(await globals.pgconn.fetchrow('SELECT COUNT(*) FROM stk_seen;'))['count']}""",
            color=globals.accentcolor
        ))

    @_.command(description="discord moment")
    async def cryaboutit(ctx: CommandContext):
        await ctx.reply("https://media.tenor.com/Tu9uZJMOKa0AAAAC/peter-griffin-victory-dance.gif")
    
    @_.command()
    async def slodych(ctx: CommandContext):
        await ctx.reply(embed=SendableEmbed(
            description=f"Here's your СЛОДЫЧ, {ctx.author.mention}!",
            media=File(f=open("assets/slodych.png", "rb").read(), filename="slodych.png"),
            color=globals.accentcolor
        ))

    @_.command()
    async def pokemap(ctx: CommandContext):

        data = await globals.pgconn.fetchrow(
            "SELECT * FROM pokemap WHERE id = $1", ctx.author.id)

        try:
            cooldown = data["cooldown"]

            if cooldown.timestamp() < datetime.now().timestamp():
                pass
            else:
                return await ctx.reply(embed=SendableEmbed(
                    title="PokeMap",
                    description=f"Command in cooldown. You can catch another PokeMap <t:{round(cooldown.timestamp())}:R>",
                    color=globals.accentcolor
                ))
        except Exception:
            pass

        a = await globals.pgconn.fetch("SELECT id, name, image FROM addons;")

        ch = random.choice(a)

        try:
            await globals.pgconn.execute("""
            INSERT INTO pokemap (id, maps, cooldown)
            VALUES (
            $1,
            $2::text[],
            current_timestamp + '2h' ::interval
            )
            ON CONFLICT (id) DO UPDATE SET
            id = $1,
            maps = array_append(pokemap.maps, $3),
            cooldown = current_timestamp + '2h' ::interval;
            """, ctx.author.id, {ch["id"]}, ch["id"])
        except Exception as e:
            log("PokeMap", f"Could not update database! {e}")
            log("PokeMap", traceback.format_exc())

            return await ctx.reply(embed=SendableEmbed(
                title="PokeMap",
                description="A database error occurred while trying to save PokeMap data. Please contact the developer.",
                color=globals.accentcolor
            ))
        else:
            await ctx.reply(embed=SendableEmbed(
                title="PokeMap",
                description=f"""{ctx.author.mention}, you've caught a **{ch['name']}!**

`/installaddon {ch['id']}`""",
                icon_url=ch['image'],
                color=globals.accentcolor
            ))

    @_.command(name="maps",
               description="View your or someone's PokeMaps.",
               aliases=["inv"])
    async def pokemaps(ctx: CommandContext, user: User = None):
        if not user:
            user = ctx.author

        maps = await globals.pgconn.fetchrow(
            "SELECT maps FROM pokemap WHERE id = $1",
            user.id
            )

        if maps is None:
            return await ctx.reply(embed=SendableEmbed(
                title="PokeMap",
                description=f"User {user.name} does not have any PokeMaps.",
                color=globals.accentcolor
            ))

        output = ""

        for i in maps['maps']:
            output += f"* {convertAddonIdToName(i)}\n"

        return await ctx.reply(embed=SendableEmbed(
            title=f"{user.name}'s PokeMaps",
            description=output,
            icon_url=user.display_avatar.url,
            color=globals.accentcolor
        ))

    @_.command(name="isityourbirthdaytoday")
    async def bdaycheck_bot(ctx: CommandContext):
        now = datetime.now()

        if now.month == 6 and now.day == 1:
            return await ctx.reply(embed=SendableEmbed(
                title="Is it my birthday today?",
                description=f"""Yes! It's my birthday today! Wish me a happy birthday :3 🎂

linaSTK was officially born on June 1, 2023 to give everyone useful STK utilities for free, forever. (over {(now - datetime.fromtimestamp(1685612887330 / 1000)).days} days ago!)""",
                color=globals.accentcolor
            ))
        else:
            return await ctx.reply(embed=SendableEmbed(
                title="It it my birthday today?",
                description=f"""No, it's not my birthday today. But I hope you wish me happy birthday once it happens ^-^ 🎂

linaSTK was officially born on June 1, 2023 to give everyone useful STK utilities for free, forever. (over {(now - datetime.fromtimestamp(1685612887330 / 1000)).days} days ago!)""",
                color=globals.accentcolor
            ))

    @_.command()
    async def info(ctx: CommandContext):

        return await ctx.reply(embed=SendableEmbed(
            description = "# linaSTK" \
            "\n\n" \
            "**Version**\n" \
            f"{globals.version}\n" \
            "\n"
            "**Instance owned by**\n" \
            f"{client.user.owner.name}\n"
            "\n\n" \
            "# About\n" \
            "linaSTK (or lina (in all lowercase) for short) is a Revolt bot made by [searinminecraft](https://github.com/searinminecraft) and is the spiritual successor to Snakebot, a discord.py bot made by DernisNW. Her purpose is to monitor every single player activity as well as give users the ability to view rankings, search for users, etc." \
            "\n\n" \
            "# lina fanfiction\n" \
            "Lina D. Garcia is a 16 year old girl that is autistic, but she likes technical things and programming. She has white hair and green eyes, and her favorite color is orange. She usually wears her iconic orange sweater, but in some cases wears regular casual clothes, mostly being orange. Lots of people have a crush on her, but she does not have interest in relationship, yet.\n\n" \
            "She got interest in SuperTuxKart when she was using Artix Linux, and decided to try out a game called SuperTuxKart. She loved it, especially with addons and online play. But she wanted to dive deep into the API, so she got her Python console opened up and started experimenting with it.",
            color=globals.accentcolor
        ))

    return _
