from voltage.ext.commands import (
    CommandsClient,
    Cog,
    CommandContext
)

from voltage import (
    SendableEmbed
)

import random
import globals

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
            #"$128\\sqrt{e980}$!",
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
            "ok then why did u say my avatar is cute earlier? %$",
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

    @_.command(description = "Show bot statistics")
    async def stats(ctx: CommandContext):
        return await ctx.reply(embed=SendableEmbed(
            title = "Bot statistics",
            icon_url = client.user.display_avatar.url,
            description = f"""**Bot started:** <t:{int(globals.startTime.timestamp())}:F>, <t:{int(globals.startTime.timestamp())}:R>
**Servers:** {len(client.servers)}
**Cached Users:** {len(client.users)}
**Online Players:** {len(globals.onlinePlayers)}
**Players in STK Seen Database:** {(await globals.pgconn.fetchrow('SELECT COUNT(*) FROM stk_seen;'))['count']}""",
            color = globals.accentcolor
        ))

    @_.command(description = "discord moment")
    async def cryaboutit(ctx: CommandContext):
        await ctx.reply("https://media.tenor.com/Tu9uZJMOKa0AAAAC/peter-griffin-victory-dance.gif")

    return _
