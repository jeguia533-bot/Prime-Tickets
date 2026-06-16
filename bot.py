
import os
import asyncio
import discord
from discord.ext import commands
from discord import app_commands

TOKEN = os.getenv("DISCORD_TOKEN")

GUILD_ID = 1514888484035498105

OPEN_TICKETS_CATEGORY_ID = 1516313573079388260
CLOSED_TICKETS_CATEGORY_ID = 1516313605035921478

STAFF_ROLE_ID = 1514893741876318268

TICKET_LOG_CHANNEL_ID = 1516311141192568892
TRANSCRIPT_CHANNEL_ID = 1516311170292650025
PAYMENT_LOG_CHANNEL_ID = 1516311199736664064
VOUCH_CHANNEL_ID = 1514896039914635275

PAYPAL_EMAIL = "muchie1230isthegoat@gmail.com"
CASHAPP_TAG = "$BIGC41L3"

BTC_ADDRESS = "bc1qh7lfxctrdjmelrk3f0c6j7yk3z0vuqmhvyjzw5"
ETH_ADDRESS = "0xE2D2118d2CaD51BF8122410Ced5678eE34273baD"
LTC_ADDRESS = "LU2PBE5o6fTdzKqvGvhKiN6W5uE9vWXwBa"
SOL_ADDRESS = "9CicGdB9ENPXeQ3M2m2ijVXHLnsreKVd9yjHsZsPeM7c"

EMBED_COLOR = 0x00AFFF
FOOTER = "⚡ Prime Stock • Premium Game Accounts"

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

ticket_count = 1


def is_staff(member: discord.Member) -> bool:
    return any(role.id == STAFF_ROLE_ID for role in member.roles)


async def send_log(channel_id: int, title: str, description: str):
    channel = bot.get_channel(channel_id)
    if not channel:
        return

    embed = discord.Embed(title=title, description=description, color=EMBED_COLOR)
    embed.set_footer(text=FOOTER)
    await channel.send(embed=embed)


def panel_embed():
    embed = discord.Embed(
        title="⚡ PRIME STOCK MARKETPLACE ⚡",
        description=(
            "━━━━━━━━━━━━━━━━━━\n\n"
            "🎮 **Select a category below to create an order ticket.**\n\n"
            "🤖 **Roblox**\n"
            "🚗 **Forza**\n"
            "⛏️ **Minecraft**\n"
            "🌈 **Rainbow Six Siege**\n\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "💎 Premium Game Accounts\n"
            "🔒 Secure Payments\n"
            "⚡ Fast Delivery\n"
            "⭐ Trusted Service\n\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "Select a category below to begin."
        ),
        color=EMBED_COLOR,
    )
    embed.set_footer(text=FOOTER)
    return embed


def ticket_embed(user: discord.Member, game: str, order_id: int, status: str = "🟡 Awaiting Payment", staff: str = "Not claimed"):
    embed = discord.Embed(
        title="⚡ PRIME STOCK MARKETPLACE ⚡",
        description=(
            "━━━━━━━━━━━━━━━━━━\n\n"
            "🎫 **Order Information**\n\n"
            f"👤 **Customer:** {user.mention}\n"
            f"🎮 **Category:** {game}\n"
            f"🆔 **Order ID:** `#{order_id:04d}`\n"
            f"👨‍💼 **Assigned Staff:** {staff}\n\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "📋 **Order Status**\n\n"
            f"{status}\n\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "💎 **What To Do Next**\n\n"
            "• Tell us which account you want\n"
            "• Ask any questions you have\n"
            "• Wait for staff assistance\n\n"
            "━━━━━━━━━━━━━━━━━━"
        ),
        color=EMBED_COLOR,
    )
    embed.set_footer(text="🔒 Secure Payments • Fast Delivery • Trusted Service")
    return embed


async def update_ticket_status(channel: discord.TextChannel, status: str = None, staff: str = None):
    if not channel.topic or "OrderID:" not in channel.topic:
        return

    parts = dict(part.split(":", 1) for part in channel.topic.split("|") if ":" in part)
    user_id = int(parts.get("UserID", "0"))
    order_id = int(parts.get("OrderID", "0"))
    game = parts.get("Game", "Unknown")
    old_staff = parts.get("Staff", "Not claimed")
    old_status = parts.get("Status", "🟡 Awaiting Payment")

    member = channel.guild.get_member(user_id)
    if not member:
        return

    new_status = status or old_status
    new_staff = staff or old_staff

    channel.topic = f"UserID:{user_id}|OrderID:{order_id}|Game:{game}|Status:{new_status}|Staff:{new_staff}"

    async for msg in channel.history(limit=20, oldest_first=True):
        if msg.author == bot.user and msg.embeds:
            await msg.edit(embed=ticket_embed(member, game, order_id, new_status, new_staff))
            return


class PaymentView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    async def check_staff(self, interaction: discord.Interaction):
        if not is_staff(interaction.user):
            await interaction.response.send_message("Only staff can use this.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Crypto", emoji="⚡", style=discord.ButtonStyle.primary)
    async def crypto(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.check_staff(interaction):
            return

        embed = discord.Embed(
            title="⚡ PRIME STOCK CRYPTO ⚡",
            description=(
                f"**BTC**\n`{BTC_ADDRESS}`\n\n"
                f"**ETH**\n`{ETH_ADDRESS}`\n\n"
                f"**LTC**\n`{LTC_ADDRESS}`\n\n"
                f"**SOL**\n`{SOL_ADDRESS}`\n\n"
                "━━━━━━━━━━━━━━━━━━\n\n"
                "After payment send:\n"
                "✅ Screenshot\n"
                "✅ Transaction ID"
            ),
            color=EMBED_COLOR,
        )
        embed.set_footer(text=FOOTER)
        await interaction.response.send_message(embed=embed)

    @discord.ui.button(label="PayPal", emoji="🅿️", style=discord.ButtonStyle.primary)
    async def paypal(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.check_staff(interaction):
            return

        embed = discord.Embed(
            title="⚡ PRIME STOCK PAYPAL ⚡",
            description=(
                "**PayPal Email**\n\n"
                f"`{PAYPAL_EMAIL}`\n\n"
                "━━━━━━━━━━━━━━━━━━\n\n"
                "After payment send:\n"
                "✅ Screenshot\n"
                "✅ Transaction ID"
            ),
            color=EMBED_COLOR,
        )
        embed.set_footer(text=FOOTER)
        await interaction.response.send_message(embed=embed)

    @discord.ui.button(label="Cash App", emoji="💵", style=discord.ButtonStyle.success)
    async def cashapp(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.check_staff(interaction):
            return

        embed = discord.Embed(
            title="⚡ PRIME STOCK CASH APP ⚡",
            description=(
                "**Cash App Tag**\n\n"
                f"`{CASHAPP_TAG}`\n\n"
                "━━━━━━━━━━━━━━━━━━\n\n"
                "After payment send:\n"
                "✅ Screenshot"
            ),
            color=EMBED_COLOR,
        )
        embed.set_footer(text=FOOTER)
        await interaction.response.send_message(embed=embed)

    @discord.ui.button(label="Gift Card", emoji="🎁", style=discord.ButtonStyle.secondary)
    async def giftcard(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.check_staff(interaction):
            return

        embed = discord.Embed(
            title="⚡ PRIME STOCK GIFT CARD ⚡",
            description=(
                "**Accepted:**\n\n"
                "🎁 Visa Prepaid\n"
                "🎁 Mastercard Prepaid\n"
                "🎁 American Express Prepaid\n\n"
                "━━━━━━━━━━━━━━━━━━\n\n"
                "Do **NOT** send card details until instructed by staff."
            ),
            color=EMBED_COLOR,
        )
        embed.set_footer(text=FOOTER)
        await interaction.response.send_message(embed=embed)


class ClosedTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    async def check_staff(self, interaction: discord.Interaction):
        if not is_staff(interaction.user):
            await interaction.response.send_message("Only staff can use this.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Reopen", emoji="🔓", style=discord.ButtonStyle.success)
    async def reopen(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.check_staff(interaction):
            return

        open_category = interaction.guild.get_channel(OPEN_TICKETS_CATEGORY_ID)
        await interaction.channel.edit(category=open_category, name=interaction.channel.name.replace("closed-", ""))
        await update_ticket_status(interaction.channel, "🟡 Awaiting Payment")
        await interaction.response.send_message(f"🔓 Ticket reopened by {interaction.user.mention}.")

    @discord.ui.button(label="Delete", emoji="🗑️", style=discord.ButtonStyle.danger)
    async def delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.check_staff(interaction):
            return

        await interaction.response.send_message("🗑️ Deleting ticket in 5 seconds...")
        await asyncio.sleep(5)
        await interaction.channel.delete()


class TicketManageView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    async def check_staff(self, interaction: discord.Interaction):
        if not is_staff(interaction.user):
            await interaction.response.send_message("Only staff can use this.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Payment Info", emoji="💸", style=discord.ButtonStyle.primary)
    async def payment_info(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.check_staff(interaction):
            return

        embed = discord.Embed(
            title="⚡ PRIME STOCK PAYMENTS ⚡",
            description=(
                "━━━━━━━━━━━━━━━━━━\n\n"
                "Select a payment method below.\n\n"
                "⚡ **Crypto**\n"
                "🅿️ **PayPal**\n"
                "💵 **Cash App**\n"
                "🎁 **Gift Card**\n\n"
                "━━━━━━━━━━━━━━━━━━\n\n"
                "⚠️ Do **NOT** send payment until staff confirms your order."
            ),
            color=EMBED_COLOR,
        )
        embed.set_footer(text=FOOTER)
        await interaction.response.send_message(embed=embed, view=PaymentView())

    @discord.ui.button(label="Claim", emoji="📌", style=discord.ButtonStyle.secondary)
    async def claim(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.check_staff(interaction):
            return

        await update_ticket_status(interaction.channel, staff=interaction.user.mention)
        await interaction.response.send_message(f"📌 Ticket claimed by {interaction.user.mention}.")

    @discord.ui.button(label="Paid", emoji="✅", style=discord.ButtonStyle.success)
    async def paid(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.check_staff(interaction):
            return

        await update_ticket_status(interaction.channel, "🟢 Paid")
        await interaction.response.send_message("💰 Payment Approved\n\nPayment has been verified by staff.")
        await send_log(PAYMENT_LOG_CHANNEL_ID, "💰 Payment Approved", f"Ticket: {interaction.channel.mention}\nStaff: {interaction.user.mention}")

    @discord.ui.button(label="Processing", emoji="🔨", style=discord.ButtonStyle.primary)
    async def processing(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.check_staff(interaction):
            return

        await update_ticket_status(interaction.channel, "🔨 Processing")
        await interaction.response.send_message("⚡ Your order is now being prepared.")

    @discord.ui.button(label="Delivered", emoji="📦", style=discord.ButtonStyle.success)
    async def delivered(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.check_staff(interaction):
            return

        await update_ticket_status(interaction.channel, "📦 Delivered")
        await interaction.response.send_message(
            "🎉 **Order Delivered**\n\n"
            "Please verify everything works correctly.\n\n"
            "Thank you for choosing **Prime Stock**."
        )

    @discord.ui.button(label="Request Vouch", emoji="⭐", style=discord.ButtonStyle.secondary)
    async def vouch(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.check_staff(interaction):
            return

        await update_ticket_status(interaction.channel, "⭐ Awaiting Vouch")
        await interaction.response.send_message(
            f"⭐ **PRIME STOCK FEEDBACK**\n\n"
            f"If you enjoyed your experience, please leave a vouch in:\n"
            f"<#{VOUCH_CHANNEL_ID}>\n\n"
            f"Your feedback helps us grow."
        )

    @discord.ui.button(label="Close", emoji="🔒", style=discord.ButtonStyle.danger)
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.check_staff(interaction):
            return

        await interaction.response.send_message("🔒 Closing ticket and moving it to closed tickets...")

        transcript_channel = bot.get_channel(TRANSCRIPT_CHANNEL_ID)
        if transcript_channel:
            messages = []
            async for msg in interaction.channel.history(limit=200, oldest_first=True):
                content = msg.content if msg.content else "[embed/attachment]"
                messages.append(f"{msg.created_at} | {msg.author}: {content}")

            transcript_text = "\n".join(messages) if messages else "No messages."
            file = discord.File(
                fp=__import__("io").BytesIO(transcript_text.encode("utf-8")),
                filename=f"{interaction.channel.name}-transcript.txt",
            )
            await transcript_channel.send(f"📄 Transcript for {interaction.channel.mention}", file=file)

        closed_category = interaction.guild.get_channel(CLOSED_TICKETS_CATEGORY_ID)
        new_name = interaction.channel.name
        if not new_name.startswith("closed-"):
            new_name = f"closed-{new_name}"

        await interaction.channel.edit(category=closed_category, name=new_name)
        await update_ticket_status(interaction.channel, "🔒 Closed")

        await send_log(TICKET_LOG_CHANNEL_ID, "🔒 Ticket Closed", f"Ticket: {interaction.channel.mention}\nClosed by: {interaction.user.mention}")
        await interaction.channel.send("🔒 Ticket closed.", view=ClosedTicketView())


class TicketPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    async def create_ticket(self, interaction: discord.Interaction, game: str, prefix: str):
        global ticket_count

        guild = interaction.guild
        open_category = guild.get_channel(OPEN_TICKETS_CATEGORY_ID)
        staff_role = guild.get_role(STAFF_ROLE_ID)

        if not open_category:
            await interaction.response.send_message("Open ticket category not found.", ephemeral=True)
            return
        if not staff_role:
            await interaction.response.send_message("Staff role not found.", ephemeral=True)
            return

        order_id = ticket_count
        ticket_count += 1

        channel_name = f"{prefix}-{order_id:04d}"

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            staff_role: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True, manage_channels=True, manage_messages=True),
        }

        channel = await guild.create_text_channel(
            name=channel_name,
            category=open_category,
            overwrites=overwrites,
            topic=f"UserID:{interaction.user.id}|OrderID:{order_id}|Game:{game}|Status:🟡 Awaiting Payment|Staff:Not claimed",
        )

        await channel.send(
            content=f"{interaction.user.mention} {staff_role.mention}",
            embed=ticket_embed(interaction.user, game, order_id),
            view=TicketManageView(),
        )

        await send_log(TICKET_LOG_CHANNEL_ID, "🎫 Ticket Opened", f"Customer: {interaction.user.mention}\nGame: {game}\nTicket: {channel.mention}")
        await interaction.response.send_message(f"Your ticket has been created: {channel.mention}", ephemeral=True)

    @discord.ui.button(label="Roblox", emoji="🤖", style=discord.ButtonStyle.primary)
    async def roblox(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket(interaction, "🤖 Roblox", "roblox")

    @discord.ui.button(label="Forza", emoji="🚗", style=discord.ButtonStyle.primary)
    async def forza(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket(interaction, "🚗 Forza", "forza")

    @discord.ui.button(label="Minecraft", emoji="⛏️", style=discord.ButtonStyle.success)
    async def minecraft(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket(interaction, "⛏️ Minecraft", "minecraft")

    @discord.ui.button(label="Rainbow Six Siege", emoji="🌈", style=discord.ButtonStyle.secondary)
    async def r6(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket(interaction, "🌈 Rainbow Six Siege", "r6")


@bot.event
async def on_ready():
    bot.add_view(TicketPanelView())
    bot.add_view(TicketManageView())
    bot.add_view(PaymentView())
    bot.add_view(ClosedTicketView())

    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Prime Stock"))

    try:
        synced = await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
        print(f"Synced {len(synced)} commands.")
    except Exception as e:
        print(f"Sync error: {e}")

    print(f"Logged in as {bot.user}")


@bot.tree.command(name="ticketpanel", description="Send the Prime Stock ticket panel.", guild=discord.Object(id=GUILD_ID))
async def ticketpanel(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator and not is_staff(interaction.user):
        await interaction.response.send_message("Only staff can use this.", ephemeral=True)
        return

    await interaction.channel.send(embed=panel_embed(), view=TicketPanelView())
    await interaction.response.send_message("Ticket panel sent.", ephemeral=True)


@bot.tree.command(name="ping", description="Check if Prime Stock is online.", guild=discord.Object(id=GUILD_ID))
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("⚡ Prime Stock is online.", ephemeral=True)


if not TOKEN:
    raise ValueError("Missing DISCORD_TOKEN. Add it in Railway Variables.")

bot.run(TOKEN)
