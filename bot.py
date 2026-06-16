
import os
import io
import asyncio
import discord
from discord.ext import commands

TOKEN = os.getenv("DISCORD_TOKEN")

# ===== PRIME STOCK CONFIG =====
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
FOOTER_TEXT = "⚡ Prime Stock • Premium Game Accounts"

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

ticket_counter = 1
ticket_data = {}

GAME_DATA = {
    "roblox": {
        "label": "Roblox",
        "emoji": "🤖",
        "prefix": "roblox",
        "description": "Open a Roblox account order ticket."
    },
    "forza": {
        "label": "Forza",
        "emoji": "🚗",
        "prefix": "forza",
        "description": "Open a Forza account order ticket."
    },
    "minecraft": {
        "label": "Minecraft",
        "emoji": "⛏️",
        "prefix": "minecraft",
        "description": "Open a Minecraft account order ticket."
    },
    "r6": {
        "label": "Rainbow Six Siege",
        "emoji": "🌈",
        "prefix": "r6",
        "description": "Open a Rainbow Six Siege account order ticket."
    },
}


def staff_check(member: discord.Member) -> bool:
    return any(role.id == STAFF_ROLE_ID for role in member.roles)


def get_ticket_info(channel_id: int):
    return ticket_data.get(channel_id)


async def send_log(channel_id: int, embed: discord.Embed):
    channel = bot.get_channel(channel_id)
    if channel:
        await channel.send(embed=embed)


def build_order_embed(user: discord.Member, game_label: str, game_emoji: str, order_id: int,
                      status: str = "🟡 Awaiting Payment", staff: str = "Not claimed"):
    embed = discord.Embed(
        title="⚡ PRIME STOCK MARKETPLACE ⚡",
        description=(
            "━━━━━━━━━━━━━━━━━━\n\n"
            "🎫 **Order Information**\n\n"
            f"👤 **Customer:** {user.mention}\n"
            f"🎮 **Category:** {game_emoji} {game_label}\n"
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
        color=EMBED_COLOR
    )
    embed.set_footer(text="🔒 Secure Payments • Fast Delivery • Trusted Service")
    return embed


def build_panel_embed():
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
        color=EMBED_COLOR
    )
    embed.set_footer(text=FOOTER_TEXT)
    return embed


async def make_transcript(channel: discord.TextChannel):
    lines = []
    async for msg in channel.history(limit=None, oldest_first=True):
        timestamp = msg.created_at.strftime("%Y-%m-%d %H:%M:%S UTC")
        author = f"{msg.author} ({msg.author.id})"
        content = msg.content or ""
        if msg.embeds:
            content += f" [Embeds: {len(msg.embeds)}]"
        if msg.attachments:
            files = ", ".join(a.url for a in msg.attachments)
            content += f" [Attachments: {files}]"
        lines.append(f"[{timestamp}] {author}: {content}")
    data = "\n".join(lines) if lines else "No messages found."
    return io.BytesIO(data.encode("utf-8"))


async def update_main_embed(channel: discord.TextChannel, status: str = None, staff: str = None):
    info = get_ticket_info(channel.id)
    if not info:
        return

    if status:
        info["status"] = status
    if staff:
        info["staff"] = staff

    try:
        msg = await channel.fetch_message(info["main_message_id"])
        embed = build_order_embed(
            info["user"],
            info["game_label"],
            info["game_emoji"],
            info["order_id"],
            info["status"],
            info["staff"]
        )
        await msg.edit(embed=embed)
    except Exception as e:
        print(f"Failed to update embed: {e}")


class PaymentMethodView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    async def check_staff(self, interaction: discord.Interaction):
        if not staff_check(interaction.user):
            await interaction.response.send_message("Only staff can use payment buttons.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Crypto", emoji="⚡", style=discord.ButtonStyle.primary)
    async def crypto(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.check_staff(interaction):
            return

        embed = discord.Embed(
            title="⚡ PRIME STOCK CRYPTO ⚡",
            description=(
                "**BTC**\n"
                f"`{BTC_ADDRESS}`\n\n"
                "**ETH**\n"
                f"`{ETH_ADDRESS}`\n\n"
                "**LTC**\n"
                f"`{LTC_ADDRESS}`\n\n"
                "**SOL**\n"
                f"`{SOL_ADDRESS}`\n\n"
                "━━━━━━━━━━━━━━━━━━\n\n"
                "After payment send:\n"
                "✅ Screenshot\n"
                "✅ Transaction ID"
            ),
            color=EMBED_COLOR
        )
        embed.set_footer(text=FOOTER_TEXT)
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
            color=EMBED_COLOR
        )
        embed.set_footer(text=FOOTER_TEXT)
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
            color=EMBED_COLOR
        )
        embed.set_footer(text=FOOTER_TEXT)
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
            color=EMBED_COLOR
        )
        embed.set_footer(text=FOOTER_TEXT)
        await interaction.response.send_message(embed=embed)


class ClosedTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    async def check_staff(self, interaction: discord.Interaction):
        if not staff_check(interaction.user):
            await interaction.response.send_message("Only staff can use this.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Reopen", emoji="🔓", style=discord.ButtonStyle.success)
    async def reopen(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.check_staff(interaction):
            return

        info = get_ticket_info(interaction.channel.id)
        opened_category = interaction.guild.get_channel(OPEN_TICKETS_CATEGORY_ID)

        if info:
            customer = info["user"]
            overwrites = interaction.channel.overwrites
            overwrites[customer] = discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True
            )
            await interaction.channel.edit(
                category=opened_category,
                name=interaction.channel.name.replace("closed-", ""),
                overwrites=overwrites
            )

        await interaction.response.send_message(f"🔓 Ticket reopened by {interaction.user.mention}.")
        await update_main_embed(interaction.channel, status="🟡 Awaiting Payment")

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
        if not staff_check(interaction.user):
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
            color=EMBED_COLOR
        )
        embed.set_footer(text=FOOTER_TEXT)
        await interaction.response.send_message(embed=embed, view=PaymentMethodView())

    @discord.ui.button(label="Claim", emoji="📌", style=discord.ButtonStyle.secondary)
    async def claim(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.check_staff(interaction):
            return

        staff_text = interaction.user.mention
        await update_main_embed(interaction.channel, staff=staff_text)
        await interaction.response.send_message(f"📌 Ticket claimed by {interaction.user.mention}.")

    @discord.ui.button(label="Paid", emoji="✅", style=discord.ButtonStyle.success)
    async def paid(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.check_staff(interaction):
            return

        await update_main_embed(interaction.channel, status="🟢 Paid")
        await interaction.response.send_message("💰 Payment Approved\n\nPayment has been verified by staff.")

        embed = discord.Embed(
            title="💰 Payment Approved",
            description=f"Ticket: {interaction.channel.mention}\nStaff: {interaction.user.mention}",
            color=EMBED_COLOR
        )
        embed.set_footer(text=FOOTER_TEXT)
        await send_log(PAYMENT_LOG_CHANNEL_ID, embed)

    @discord.ui.button(label="Processing", emoji="🔨", style=discord.ButtonStyle.primary)
    async def processing(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.check_staff(interaction):
            return

        await update_main_embed(interaction.channel, status="🔨 Processing")
        await interaction.response.send_message("⚡ Your order is now being prepared.")

    @discord.ui.button(label="Delivered", emoji="📦", style=discord.ButtonStyle.success)
    async def delivered(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.check_staff(interaction):
            return

        await update_main_embed(interaction.channel, status="📦 Delivered")
        await interaction.response.send_message(
            "🎉 **Order Delivered**\n\n"
            "Please verify everything works correctly.\n\n"
            "Thank you for choosing **Prime Stock**."
        )

    @discord.ui.button(label="Request Vouch", emoji="⭐", style=discord.ButtonStyle.secondary)
    async def vouch(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.check_staff(interaction):
            return

        await update_main_embed(interaction.channel, status="⭐ Awaiting Vouch")
        await interaction.response.send_message(
            "⭐ **PRIME STOCK FEEDBACK**\n\n"
            f"If you enjoyed your experience, please leave a vouch in:\n"
            f"<#{VOUCH_CHANNEL_ID}>\n\n"
            "Your feedback helps us grow."
        )

    @discord.ui.button(label="Close", emoji="🔒", style=discord.ButtonStyle.danger)
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.check_staff(interaction):
            return

        await interaction.response.send_message("🔒 Closing ticket...\nSaving transcript and moving to closed category.")

        transcript_file = await make_transcript(interaction.channel)
        filename = f"transcript-{interaction.channel.name}.txt"

        transcript_channel = bot.get_channel(TRANSCRIPT_CHANNEL_ID)
        if transcript_channel:
            transcript_file.seek(0)
            await transcript_channel.send(
                content=f"📄 Transcript for {interaction.channel.mention}",
                file=discord.File(transcript_file, filename=filename)
            )

        embed = discord.Embed(
            title="🔒 Ticket Closed",
            description=f"Ticket: {interaction.channel.mention}\nClosed by: {interaction.user.mention}",
            color=EMBED_COLOR
        )
        embed.set_footer(text=FOOTER_TEXT)
        await send_log(TICKET_LOG_CHANNEL_ID, embed)

        info = get_ticket_info(interaction.channel.id)
        closed_category = interaction.guild.get_channel(CLOSED_TICKETS_CATEGORY_ID)

        overwrites = interaction.channel.overwrites
        if info:
            customer = info["user"]
            overwrites[customer] = discord.PermissionOverwrite(
                view_channel=True,
                send_messages=False,
                read_message_history=True
            )

        new_name = interaction.channel.name
        if not new_name.startswith("closed-"):
            new_name = f"closed-{new_name}"

        await interaction.channel.edit(
            category=closed_category,
            name=new_name,
            overwrites=overwrites
        )

        await update_main_embed(interaction.channel, status="🔒 Closed")
        await interaction.channel.send("🔒 Ticket has been closed.", view=ClosedTicketView())


class TicketPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    async def create_ticket(self, interaction: discord.Interaction, game_key: str):
        global ticket_counter

        guild = interaction.guild
        staff_role = guild.get_role(STAFF_ROLE_ID)
        category = guild.get_channel(OPEN_TICKETS_CATEGORY_ID)

        game = GAME_DATA[game_key]
        order_id = ticket_counter
        ticket_counter += 1

        channel_name = f"{game['prefix']}-{order_id:04d}"

        existing = [
            ch for ch in guild.text_channels
            if ch.category_id == OPEN_TICKETS_CATEGORY_ID
            and ch.overwrites_for(interaction.user).view_channel
            and ch.name.startswith(game["prefix"])
        ]

        if existing:
            await interaction.response.send_message(
                f"You already have an open {game['label']} ticket: {existing[0].mention}",
                ephemeral=True
            )
            return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True
            ),
            staff_role: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True,
                manage_channels=True,
                manage_messages=True
            ),
        }

        channel = await guild.create_text_channel(
            name=channel_name,
            category=category,
            overwrites=overwrites,
            topic=f"Prime Stock Order #{order_id:04d} | {game['label']} | Customer: {interaction.user.id}"
        )

        embed = build_order_embed(
            interaction.user,
            game["label"],
            game["emoji"],
            order_id
        )

        msg = await channel.send(
            content=f"{interaction.user.mention} {staff_role.mention}",
            embed=embed,
            view=TicketManageView()
        )

        ticket_data[channel.id] = {
            "user": interaction.user,
            "game_label": game["label"],
            "game_emoji": game["emoji"],
            "order_id": order_id,
            "status": "🟡 Awaiting Payment",
            "staff": "Not claimed",
            "main_message_id": msg.id
        }

        log_embed = discord.Embed(
            title="🎫 Ticket Opened",
            description=(
                f"Customer: {interaction.user.mention}\n"
                f"Game: {game['emoji']} {game['label']}\n"
                f"Order ID: `#{order_id:04d}`\n"
                f"Channel: {channel.mention}"
            ),
            color=EMBED_COLOR
        )
        log_embed.set_footer(text=FOOTER_TEXT)
        await send_log(TICKET_LOG_CHANNEL_ID, log_embed)

        await interaction.response.send_message(
            f"Your ticket has been created: {channel.mention}",
            ephemeral=True
        )

    @discord.ui.button(label="Roblox", emoji="🤖", style=discord.ButtonStyle.primary)
    async def roblox(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket(interaction, "roblox")

    @discord.ui.button(label="Forza", emoji="🚗", style=discord.ButtonStyle.primary)
    async def forza(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket(interaction, "forza")

    @discord.ui.button(label="Minecraft", emoji="⛏️", style=discord.ButtonStyle.success)
    async def minecraft(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket(interaction, "minecraft")

    @discord.ui.button(label="Rainbow Six Siege", emoji="🌈", style=discord.ButtonStyle.secondary)
    async def r6(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket(interaction, "r6")


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

    bot.add_view(TicketPanelView())
    bot.add_view(TicketManageView())
    bot.add_view(PaymentMethodView())
    bot.add_view(ClosedTicketView())

    activity = discord.Activity(type=discord.ActivityType.watching, name="Prime Stock")
    await bot.change_presence(activity=activity)

    guild = discord.Object(id=GUILD_ID)
    try:
        synced = await bot.tree.sync(guild=guild)
        print(f"Synced {len(synced)} slash commands.")
    except Exception as e:
        print(f"Slash command sync error: {e}")


@bot.tree.command(
    name="ticketpanel",
    description="Send the Prime Stock ticket panel.",
    guild=discord.Object(id=GUILD_ID)
)
async def ticketpanel(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator and not staff_check(interaction.user):
        await interaction.response.send_message("Only staff can send the ticket panel.", ephemeral=True)
        return

    await interaction.channel.send(embed=build_panel_embed(), view=TicketPanelView())
    await interaction.response.send_message("Ticket panel sent.", ephemeral=True)


@bot.tree.command(
    name="ping",
    description="Check if the bot is online.",
    guild=discord.Object(id=GUILD_ID)
)
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("⚡ Prime Stock is online.", ephemeral=True)


if not TOKEN:
    raise ValueError("Missing DISCORD_TOKEN environment variable.")

bot.run(TOKEN)
