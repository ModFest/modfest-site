import asyncio
from typing import List

from discord.ext import commands
import discord
import config
import storage_manager as storage
from data.data_classes import Event, Badge, User, Entry
from datetime import datetime

bot: commands.Bot = commands.Bot(command_prefix='+')
bot.remove_command("help")


async def start():
    await bot.start(config.bot_token)


@bot.event
async def on_ready():
    print(f"Bot Ready {bot.user.name}")
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Game(
            name="MiniFest: FallFest | ModFest.net",
            type=discord.ActivityType.playing
        )
    )


@bot.command()
@commands.has_role(config.admin_role)
async def ping(ctx):
    await ctx.send('Pong! {0}s'.format(round(bot.latency, 3)))


@bot.group(name="admin")
@commands.has_role(config.admin_role)
async def admin(ctx):
    pass


@admin.command()
async def stats(ctx: commands.Context, *args):
    if len(args) == 0:
        e: discord.embeds.Embed = discord.embeds.Embed(
            title="ModFest Stats",
            timestamp=datetime.now(),
        )
        await ctx.send(embed=e)


@admin.command()
@commands.has_role(config.admin_role)
async def create(ctx: commands.Context, *args):
    if len(args) < 1:
        return
    if args[0] == "event":
        if len(args) == 4:
            if storage.get_event(args[1]) is None:
                storage.create_event(args[1], args[2], args[3])
                await ctx.send(f"created event \"{args[1]}\" ({args[2]} - {args[3]})")
            else:
                await ctx.send(f"event {args[1]} already exists, use `+admin edit event {args[1]}` to edit.")

    if args[0] == "badge":
        if len(args) == 3:
            if storage.get_badge_by_name(args[1]) is None:
                storage.create_badge(Badge(0, args[1], args[2]))
            else:
                await ctx.send(f"badge {args[1]} already exists, use `+admin edit badge {args[1]}` to edit.")


@admin.command()
@commands.has_role(config.admin_role)
async def edit(ctx, *args):
    if len(args) < 1:
        return
    if args[0] == "event":
        if len(args) >= 2:
            e: Event = storage.get_event(args[1])
            if e is not None:
                if args[2] == "name":
                    e = storage.update_event(args[1], name=args[3])
                if args[2] == "start":
                    e = storage.update_event(args[1], start=args[3])
                if args[2] == "end":
                    e = storage.update_event(args[1], end=args[3])
                if args[2] == "state":
                    e = storage.update_event(args[1], state=args[3])

                await ctx.send(f"event {args[2]} edited, name={e.name} start={e.start} end={e.end} state={e.state}")
            else:
                await ctx.send(f"event {args[1]} does not exist, use `+admin create event {args[1]}` to create it.")

    if args[0] == "badge":
        b: Badge = storage.get_badge(int(args[1]))
        if b is None:
            await ctx.send(f"badge {args[1]} not found.")
            return
        if args[2] == "name":
            b = storage.update_badge(b.badge_id, name=args[3])
        if args[2] == "icon":
            b = storage.update_badge(b.badge_id, icon=args[3])
        if args[3] == "role":
            b = storage.update_badge(b.badge_id, role=args[3])

        await ctx.send(f"updated badge. `{b}`")


@admin.command()
@commands.has_role(config.admin_role)
async def delete(ctx, *args):
    if len(args) < 1:
        return


@admin.command()
@commands.has_role(config.admin_role)
async def badge(ctx: commands.Context, *args):
    if len(args) < 1:
        return

    if args[0] == "list":
        badges: List[Badge] = storage.get_badge_list()
        txt: str = ""
        for x in badges:
            txt += f"{x.badge_id} - \"{x.name}\"\n"
        await ctx.send(txt)
        return
    b: Badge = storage.get_badge(int(args[0]))
    if b is None:
        await ctx.send(f"badge {args[0]} not found.")
        return

    if args[1] == "give":
        msg: discord.Message = ctx.message
        if len(msg.mentions) == 1:
            u: User = storage.get_user_by_id(msg.mentions[0].id)
            storage.add_badge(u, b)
            badges = storage.get_user_badges(u)
            x = []
            for y in badges:
                x.append(y.name)
            await ctx.send(f"user `{u.format_name()}`' now has badges `{x}`")

    if args[1] == "take":
        msg: discord.Message = ctx.message
        if len(msg.mentions) == 1:
            u: User = storage.get_user_by_id(msg.mentions[0].id)
            storage.remove_badge(u, b)
            badges = storage.get_user_badges(u)
            x = []
            for y in badges:
                x.append(y.name)
            await ctx.send(f"user `{u.format_name()}`' now has badges `{x}`")


@bot.group()
async def submission(ctx):
    pass


@submission.command(name="list")
async def list_entries(ctx):
    el: List[Entry] = storage.get_entries_for_user(storage.get_user_by_id_or_default(ctx.message.author.id))
    s: str = ""
    for e in el:
        s += f"{e.name} ({storage.get_entry_id_from_name(e.name)})\n"
    await ctx.send(s)


@submission.command()
async def delete(ctx, *args):

    def check(m):
        return m.channel.id == ctx.channel.id and m.author.id == ctx.message.author.id

    if len(args) == 1:
        e: Entry = storage.get_entry(int(args[0]))
        if e:
            u: User = storage.get_user_by_id_or_default(ctx.message.author.id)
            for x in e.users:
                if u.user_id == x.user_id:
                    await ctx.send(f"Are you sure you want to delete submission \"{e.name}\"? (type YES to confirm or "
                                   f"anything else to cancel)")
                    try:
                        ans: discord.Message = await bot.wait_for("message", check=check, timeout=30)

                        if ans.content == "YES":
                            storage.delete_entry(storage.get_entry_id_from_name(e.name))
                            em: discord.Embed = discord.Embed(
                                title=f"Submission Deleted: {e.name}",
                                description=f"User {bot.get_user(u.user_id).mention} has deleted one of their entries.",
                                timestamp=datetime.utcnow()
                            )
                            await bot.get_channel(758534206628036628).send(embed=em)
                            await ctx.send(embed=e)

                    except asyncio.TimeoutError:
                        await ctx.send(f"Submission delete timed out.")
                    return
            else:
                await ctx.send(f"You are not an author of \"{e.name}\".")
        else:
            await ctx.send(f"Submission with id \"{args[0]}\" not found.")


@submission.command()
async def new(ctx):
    dm: discord.DMChannel = await ctx.message.author.create_dm()

    def check(m):
        return m.channel == dm and m.author.id == ctx.message.author.id

    try:
        await dm.send("What is your mod called?")
        await ctx.message.add_reaction("\u2705")
        name: discord.Message = await bot.wait_for("message", check=check, timeout=120)

        await dm.send("Enter your mod's description.")
        desc: discord.Message = await bot.wait_for("message", check=check, timeout=120)

        await dm.send("Enter your mod's dependencies.")
        await dm.send("\"None\" or comma separated list of mod-ids, eg: \"modfest-utilities, fabric\"")
        deps: discord.Message = await bot.wait_for("message", check=check, timeout=120)

        await dm.send("Enter the link to your mod. (Direct `.jar` file or CurseForge page)")
        link: discord.Message = await bot.wait_for("message", check=check, timeout=120)

        await dm.send("Enter a link to the source code of your mod.")
        source: discord.Message = await bot.wait_for("message", check=check, timeout=120)

        await dm.send("Enter a link to your mod's issue tracker.")
        issues: discord.Message = await bot.wait_for("message", check=check, timeout=120)

        await dm.send("Upload a screenshot for you mod.")
        screenshot: discord.Message = await bot.wait_for("message", check=check, timeout=120)

        await dm.send("Enter your team members. \n\"None\" or comma separated list of discord user ids or tags, "
                      "eg: \"719070278050906122, 97172171259904000\" or \"JoeZwet#0001, ModFest#4875\"")
        team: discord.message = await bot.wait_for("message", check=check, timeout=120)

        e: discord.Embed = discord.Embed(
            title=f"New Submission: {name.content}",
            timestamp=datetime.utcnow(),
            color=discord.Colour.from_rgb(r=251, g=135, b=34),
            description=desc.content
        )
        e.set_image(url=screenshot.attachments[0].url)
        e.add_field(
            name="Dependencies",
            value=deps.content,
            inline=True,
        )
        e.add_field(
            name="Links",
            value=f"[Mod]({link.content}), [Source]({source.content}), [Issues]({issues.content})",
            inline=True,
        )

        t = ctx.message.author.mention + ", "
        if team.content.lower() != "none":
            c: str = team.content
            c.strip()
            c.replace(" ", "")
            for x in c.split(","):
                if '#' in x:
                    print(x)
                    u = []
                    for y in bot.get_all_members():
                        if y.name.lower() == x.split("#")[0].lower() and str(y.discriminator) == x.split("#")[1]:
                            u.append(y)
                    print(u)
                    if len(u) > 0:
                        t += f"{u[0].mention}, "
                        print(u[0])
                else:
                    u = bot.get_user(int(x))
                    if u is not None:
                        t += f"{u.mention}, "
            if t.endswith(", "):
                t = t[:-2]

        if t:
            e.add_field(
                name="Authors",
                value=t,
                inline=True
            )

        await bot.get_channel(758534206628036628).send(embed=e)
        await dm.send(embed=e)

        users: List[User] = []
        users.append(storage.get_user_by_id_or_default(ctx.message.author.id))

        if team.content.lower() != "none":
            c: str = team.content
            c.strip()
            c.replace(" ", "")
            for x in c.split(","):
                if '#' in x:
                    u = []
                    for y in bot.users:
                        if y.name.lower() == x.split("#")[0].lower() and y.discriminator == x.split("#")[1]:
                            u.append(y)
                    if len(u) > 0:
                        users.append(storage.get_user_by_id_or_default(u[0].id))
                else:
                    u = bot.get_user(int(x))
                    if u is not None:
                        users.append(storage.get_user_by_id_or_default(u.id))

        storage.create_entry(
            Entry(users, name=name.content, description=desc.content, screenshot=screenshot.attachments[0].url,
                  link=link.content, source=source.content, issues=issues.content, dependencies=deps.content))
    except discord.Forbidden:
        await ctx.send("This command requires your DMs to be open.")
    except asyncio.TimeoutError:
        await dm.send("Took to long to respond.")


@bot.command()
async def profile(ctx, *args):
    if len(args) == 2:
        if args[0] == "pronouns":
            u: User = storage.get_user_by_id_or_default(ctx.message.author.id)
            u.pronouns = args[1]
            storage.update_user(u)
