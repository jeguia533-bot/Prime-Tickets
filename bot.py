
import os
import io
import asyncio
import discord
from discord.ext import commands

TOKEN = os.getenv("DISCORD_TOKEN")

# ================= CONFIG =================
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

# ================= BOT SETUP =================
intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

ticket_count = 1


# ================= HELPERS =================
def is_staff(member: discord.Member) -> bool:
    if member.guild.owner_id == member.id:
        return True

    if member.guild_permissions.administrator:
        return True

    staff_role = member.guild.get_role(STAFF_ROLE_ID)

    if any(role.id == STAFF_ROLE_ID for role in member.roles):
        return True

    if staff_role and member.top_role > staff_role:
        return True

    return False


async def send_log(channel_id: int, title: str, description: str):
    channel = bot.get_channel(channel_id)
    if not channel:
        return

    embed = discord.Embed(title=title, description=description, color=EMBED_COLOR)
    embed.set_footer(text=FOOTER)
    await channel.send(embed=embed)


async def make_transcript(channel: discord.TextChannel):
    lines = []

    async for msg in channel.history(limit=300, oldest_first=True):
        content = msg.content if msg.content else ""
        if msg.embeds:
            content += f" [Embeds: {len(msg.embeds)}]"
        if msg.attachments:
            attachment_urls = ", ".join(a.url for a in msg.attachments)
            content += f" [Attachments: {attachment_urls}]"

        lines.append(f"{msg.created_at} | {msg.author}: {content}")

    transcript = "\n".join(lines) if lines else "No messages."
    return discord.File(
        fp=io.BytesIO(transcript.encode("utf-8")),
        filename=f"{channel.name}-transcript.txt"
    )


def parse_topic(topic: str):
    data = {}
    if not topic:
        return data

    for part in topic.split("|"):
        if ":" in part:
            key, value = part.split(":", 1)
            data[key] = value

    return data


def build_topic(user_id: int, ticket_id: int, ticket_type: str, status: str, staff: str):
    return f"UserID:{user_id}|TicketID:{ticket_id}|Type:{ticket_type}|Status:{status}|Staff:{staff}"


async def update_ticket_embed(channel: discord.TextChannel, status: str = None, staff: str = None):
    data = parse_topic(channel.topic)

    user_id = int(data.get("UserID", "0"))
    ticket_id = int(data.get("TicketID", "0"))
    ticket_type = data.get("Type", "Unknown")
    current_status = data.get("Status", "🟡 Awaiting Payment")
    current_staff = data.get("Staff", "Not claimed")

    member = channel.guild.get_member(user_id)
    if not member:
        return

    new_status = status or current_status
    new_staff = staff or current_staff

    await channel.edit(topic=build_topic(user_id, ticket_id, ticket_type, new_status, new_staff))

    async for msg in channel.history(limit=25, oldest_first=True):
        if msg.author == bot.user and msg.embeds:
            if ticket_type.startswith("ORDER:"):
                game = ticket_type.replace("ORDER:", "")
                await msg.edit(embed=order_ticket_embed(member, game, ticket_id, new_status, new_staff))
            elif ticket_type == "SUPPORT":
                await msg.edit(embed=support_ticket_embed(member, ticket_id, new_status, new_staff))
            elif ticket_type == "PARTNERSHIP":
                await msg.edit(embed=partnership_ticket_embed(member, ticket_id, new_status, new_staff))
            elif ticket_type == "BOOSTING":
                await msg.edit(embed=boosting_ticket_embed(member, ticket_id, new_status, new_staff))
            return


# ================= EMBEDS =================
def order_panel_embed():
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


def support_panel_embed():
    embed = discord.Embed(
        title="⚡ PRIME STOCK SUPPORT ⚡",
        description=(
            "━━━━━━━━━━━━━━━━━━\n\n"
            "Need help or want to work with us?\n\n"
            "🤝 **Partnership**\n"
            "Open a ticket for partner requests, collabs, or business offers.\n\n"
            "❓ **Support**\n"
            "Open a ticket for questions, order help, or general assistance.\n\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "Select an option below to begin."
        ),
        color=EMBED_COLOR,
    )
    embed.set_footer(text=FOOTER)
    return embed



def boosting_panel_embed():
    embed = discord.Embed(
        title="⚡ PRIME STOCK BOOSTING REQUESTS ⚡",
        description=(
            "━━━━━━━━━━━━━━━━━━\n\n"
            "Need a custom boosting request?\n\n"
            "🚀 **Boosting Request**\n"
            "Open a ticket for custom boosting orders, questions, or special requests.\n\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "Select the button below to begin."
        ),
        color=EMBED_COLOR,
    )
    embed.set_footer(text=FOOTER)
    return embed


def order_ticket_embed(user: discord.Member, game: str, ticket_id: int, status="🟡 Awaiting Payment", staff="Not claimed"):
    embed = discord.Embed(
        title="⚡ PRIME STOCK MARKETPLACE ⚡",
        description=(
            "━━━━━━━━━━━━━━━━━━\n\n"
            "🎫 **Order Information**\n\n"
            f"👤 **Customer:** {user.mention}\n"
            f"🎮 **Category:** {game}\n"
            f"🆔 **Order ID:** `#{ticket_id:04d}`\n"
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


def support_ticket_embed(user: discord.Member, ticket_id: int, status="🟡 Awaiting Staff", staff="Not claimed"):
    embed = discord.Embed(
        title="⚡ PRIME STOCK SUPPORT TICKET ⚡",
        description=(
            "━━━━━━━━━━━━━━━━━━\n\n"
            "❓ **Welcome to Prime Stock Support**\n\n"
            f"👤 **Customer:** {user.mention}\n"
            f"🆔 **Ticket ID:** `#{ticket_id:04d}`\n"
            f"👨‍💼 **Assigned Staff:** {staff}\n\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "📋 **Ticket Status**\n\n"
            f"{status}\n\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "Please describe your issue or question in detail.\n\n"
            "**Examples:**\n"
            "• Order assistance\n"
            "• Account questions\n"
            "• Server issues\n"
            "• General support\n\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "A member of our team will assist you shortly."
        ),
        color=EMBED_COLOR,
    )
    embed.set_footer(text=FOOTER)
    return embed


def partnership_ticket_embed(user: discord.Member, ticket_id: int, status="🟡 Awaiting Review", staff="Not claimed"):
    embed = discord.Embed(
        title="⚡ PRIME STOCK PARTNERSHIP REQUEST ⚡",
        description=(
            "━━━━━━━━━━━━━━━━━━\n\n"
            "🤝 **Welcome to Prime Stock Partnership Requests**\n\n"
            f"👤 **Customer:** {user.mention}\n"
            f"🆔 **Ticket ID:** `#{ticket_id:04d}`\n"
            f"👨‍💼 **Assigned Staff:** {staff}\n\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "📋 **Request Status**\n\n"
            f"{status}\n\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "Please provide:\n\n"
            "• Server Name\n"
            "• Member Count\n"
            "• Partnership Proposal\n"
            "• Any Additional Information\n\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "A member of our team will review your request shortly."
        ),
        color=EMBED_COLOR,
    )
    embed.set_footer(text=FOOTER)
    return embed



def boosting_ticket_embed(user: discord.Member, ticket_id: int, status="🟡 Awaiting Staff", staff="Not claimed"):
    embed = discord.Embed(
        title="⚡ PRIME STOCK BOOSTING REQUEST ⚡",
        description=(
            "━━━━━━━━━━━━━━━━━━\n\n"
            "🚀 **Welcome to Prime Stock Boosting Requests**\n\n"
            f"👤 **Customer:** {user.mention}\n"
            f"🆔 **Ticket ID:** `#{ticket_id:04d}`\n"
            f"👨‍💼 **Assigned Staff:** {staff}\n\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "📋 **Request Status**\n\n"
            f"{status}\n\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "Please describe what you need in detail.\n\n"
            "**Include:**\n"
            "• Game Name\n"
            "• What service/boost you need\n"
            "• Current progress/stats if needed\n"
            "• Any special notes\n\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "A member of our team will assist you shortly."
        ),
        color=EMBED_COLOR,
    )
    embed.set_footer(text=FOOTER)
    return embed


# ================= PAYMENT VIEW =================
class PaymentView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    async def staff_only(self, interaction: discord.Interaction):
        if not is_staff(interaction.user):
            await interaction.response.send_message("Only staff can use this.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Crypto", emoji="⚡", style=discord.ButtonStyle.primary, custom_id="prime_payment_crypto")
    async def crypto(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.staff_only(interaction):
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

    @discord.ui.button(label="PayPal", emoji="🅿️", style=discord.ButtonStyle.primary, custom_id="prime_payment_paypal")
    async def paypal(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.staff_only(interaction):
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

    @discord.ui.button(label="Cash App", emoji="💵", style=discord.ButtonStyle.success, custom_id="prime_payment_cashapp")
    async def cashapp(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.staff_only(interaction):
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

    @discord.ui.button(label="Gift Card", emoji="🎁", style=discord.ButtonStyle.secondary, custom_id="prime_payment_giftcard")
    async def giftcard(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.staff_only(interaction):
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


# ================= ORDER TICKET STAFF BUTTONS =================
class OrderTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    async def staff_only(self, interaction: discord.Interaction):
        if not is_staff(interaction.user):
            await interaction.response.send_message("Only staff can use this.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Payment Info", emoji="💸", style=discord.ButtonStyle.primary, custom_id="prime_order_payment_info")
    async def payment_info(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.staff_only(interaction):
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

    @discord.ui.button(label="Claim", emoji="📌", style=discord.ButtonStyle.secondary, custom_id="prime_order_claim")
    async def claim(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.staff_only(interaction):
            return
        await update_ticket_embed(interaction.channel, staff=interaction.user.mention)
        await interaction.response.send_message(f"📌 Ticket claimed by {interaction.user.mention}.")

    @discord.ui.button(label="Paid", emoji="✅", style=discord.ButtonStyle.success, custom_id="prime_order_paid")
    async def paid(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.staff_only(interaction):
            return
        await update_ticket_embed(interaction.channel, status="🟢 Paid")
        await interaction.response.send_message("💰 Payment Approved\n\nPayment has been verified by staff.")
        await send_log(PAYMENT_LOG_CHANNEL_ID, "💰 Payment Approved", f"Ticket: {interaction.channel.mention}\nStaff: {interaction.user.mention}")

    @discord.ui.button(label="Processing", emoji="🔨", style=discord.ButtonStyle.primary, custom_id="prime_order_processing")
    async def processing(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.staff_only(interaction):
            return
        await update_ticket_embed(interaction.channel, status="🔨 Processing")
        await interaction.response.send_message("⚡ Your order is now being prepared.")

    @discord.ui.button(label="Delivered", emoji="📦", style=discord.ButtonStyle.success, custom_id="prime_order_delivered")
    async def delivered(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.staff_only(interaction):
            return
        await update_ticket_embed(interaction.channel, status="📦 Delivered")
        await interaction.response.send_message(
            "🎉 **Order Delivered**\n\n"
            "Please verify everything works correctly.\n\n"
            "Thank you for choosing **Prime Stock**."
        )

    @discord.ui.button(label="Request Vouch", emoji="⭐", style=discord.ButtonStyle.secondary, custom_id="prime_order_vouch")
    async def vouch(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.staff_only(interaction):
            return
        await update_ticket_embed(interaction.channel, status="⭐ Awaiting Vouch")
        await interaction.response.send_message(
            f"⭐ **PRIME STOCK FEEDBACK**\n\n"
            f"If you enjoyed your experience, please leave a vouch in:\n"
            f"<#{VOUCH_CHANNEL_ID}>\n\n"
            f"Your feedback helps us grow."
        )

    @discord.ui.button(label="Close", emoji="🔒", style=discord.ButtonStyle.danger, custom_id="prime_order_close")
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.staff_only(interaction):
            return
        await close_ticket(interaction)


# ================= SUPPORT TICKET STAFF BUTTONS =================
class SupportTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    async def staff_only(self, interaction: discord.Interaction):
        if not is_staff(interaction.user):
            await interaction.response.send_message("Only staff can use this.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Claim", emoji="📌", style=discord.ButtonStyle.secondary, custom_id="prime_support_claim")
    async def claim(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.staff_only(interaction):
            return
        await update_ticket_embed(interaction.channel, staff=interaction.user.mention)
        await interaction.response.send_message(f"📌 Ticket claimed by {interaction.user.mention}.")

    @discord.ui.button(label="Close", emoji="🔒", style=discord.ButtonStyle.danger, custom_id="prime_support_close")
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.staff_only(interaction):
            return
        await close_ticket(interaction)


class ClosedTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    async def staff_only(self, interaction: discord.Interaction):
        if not is_staff(interaction.user):
            await interaction.response.send_message("Only staff can use this.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Reopen", emoji="🔓", style=discord.ButtonStyle.success, custom_id="prime_closed_reopen")
    async def reopen(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.staff_only(interaction):
            return

        open_category = interaction.guild.get_channel(OPEN_TICKETS_CATEGORY_ID)
        new_name = interaction.channel.name.replace("closed-", "")

        await interaction.channel.edit(category=open_category, name=new_name)
        await update_ticket_embed(interaction.channel, status="🟡 Reopened")
        await interaction.response.send_message(f"🔓 Ticket reopened by {interaction.user.mention}.")

    @discord.ui.button(label="Delete", emoji="🗑️", style=discord.ButtonStyle.danger, custom_id="prime_closed_delete")
    async def delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.staff_only(interaction):
            return

        await interaction.response.send_message("🗑️ Deleting ticket in 5 seconds...")
        await asyncio.sleep(5)
        await interaction.channel.delete()


# ================= CLOSE FUNCTION =================
async def close_ticket(interaction: discord.Interaction):
    await interaction.response.send_message("🔒 Closing ticket and moving it to closed tickets...")

    transcript_channel = bot.get_channel(TRANSCRIPT_CHANNEL_ID)
    if transcript_channel:
        file = await make_transcript(interaction.channel)
        await transcript_channel.send(f"📄 Transcript for {interaction.channel.mention}", file=file)

    closed_category = interaction.guild.get_channel(CLOSED_TICKETS_CATEGORY_ID)

    new_name = interaction.channel.name
    if not new_name.startswith("closed-"):
        new_name = f"closed-{new_name}"

    await interaction.channel.edit(category=closed_category, name=new_name)
    await update_ticket_embed(interaction.channel, status="🔒 Closed")

    await send_log(TICKET_LOG_CHANNEL_ID, "🔒 Ticket Closed", f"Ticket: {interaction.channel.mention}\nClosed by: {interaction.user.mention}")
    await interaction.channel.send("🔒 Ticket closed.", view=ClosedTicketView())


# ================= PANEL VIEWS =================
class OrderPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    async def create_order_ticket(self, interaction: discord.Interaction, game: str, prefix: str):
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

        ticket_id = ticket_count
        ticket_count += 1

        channel_name = f"{prefix}-{ticket_id:04d}"

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            staff_role: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True, manage_channels=True, manage_messages=True),
        }

        channel = await guild.create_text_channel(
            name=channel_name,
            category=open_category,
            overwrites=overwrites,
            topic=build_topic(interaction.user.id, ticket_id, f"ORDER:{game}", "🟡 Awaiting Payment", "Not claimed"),
        )

        await channel.send(
            content=f"{interaction.user.mention} {staff_role.mention}",
            embed=order_ticket_embed(interaction.user, game, ticket_id),
            view=OrderTicketView(),
        )

        await send_log(TICKET_LOG_CHANNEL_ID, "🎫 Order Ticket Opened", f"Customer: {interaction.user.mention}\nGame: {game}\nTicket: {channel.mention}")
        await interaction.response.send_message(f"Your order ticket has been created: {channel.mention}", ephemeral=True)

    @discord.ui.button(label="Roblox", emoji="🤖", style=discord.ButtonStyle.primary, custom_id="prime_panel_roblox")
    async def roblox(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_order_ticket(interaction, "🤖 Roblox", "roblox")

    @discord.ui.button(label="Forza", emoji="🚗", style=discord.ButtonStyle.primary, custom_id="prime_panel_forza")
    async def forza(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_order_ticket(interaction, "🚗 Forza", "forza")

    @discord.ui.button(label="Minecraft", emoji="⛏️", style=discord.ButtonStyle.success, custom_id="prime_panel_minecraft")
    async def minecraft(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_order_ticket(interaction, "⛏️ Minecraft", "minecraft")

    @discord.ui.button(label="Rainbow Six Siege", emoji="🌈", style=discord.ButtonStyle.secondary, custom_id="prime_panel_r6")
    async def r6(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_order_ticket(interaction, "🌈 Rainbow Six Siege", "r6")


class SupportPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    async def create_support_ticket(self, interaction: discord.Interaction, ticket_type: str, prefix: str):
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

        ticket_id = ticket_count
        ticket_count += 1

        channel_name = f"{prefix}-{ticket_id:04d}"

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            staff_role: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True, manage_channels=True, manage_messages=True),
        }

        if ticket_type == "PARTNERSHIP":
            embed = partnership_ticket_embed(interaction.user, ticket_id)
            topic_type = "PARTNERSHIP"
        else:
            embed = support_ticket_embed(interaction.user, ticket_id)
            topic_type = "SUPPORT"

        channel = await guild.create_text_channel(
            name=channel_name,
            category=open_category,
            overwrites=overwrites,
            topic=build_topic(interaction.user.id, ticket_id, topic_type, "🟡 Awaiting Staff", "Not claimed"),
        )

        await channel.send(
            content=f"{interaction.user.mention} {staff_role.mention}",
            embed=embed,
            view=SupportTicketView(),
        )

        await send_log(TICKET_LOG_CHANNEL_ID, "🎫 Support Ticket Opened", f"Customer: {interaction.user.mention}\nType: {ticket_type}\nTicket: {channel.mention}")
        await interaction.response.send_message(f"Your ticket has been created: {channel.mention}", ephemeral=True)

    @discord.ui.button(label="Partnership", emoji="🤝", style=discord.ButtonStyle.primary, custom_id="prime_panel_partnership")
    async def partnership(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_support_ticket(interaction, "PARTNERSHIP", "partner")

    @discord.ui.button(label="Support", emoji="❓", style=discord.ButtonStyle.secondary, custom_id="prime_panel_support")
    async def support(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_support_ticket(interaction, "SUPPORT", "support")



class BoostingPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    async def create_boosting_ticket(self, interaction: discord.Interaction):
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

        ticket_id = ticket_count
        ticket_count += 1

        channel_name = f"boosting-{ticket_id:04d}"

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            staff_role: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True, manage_channels=True, manage_messages=True),
        }

        channel = await guild.create_text_channel(
            name=channel_name,
            category=open_category,
            overwrites=overwrites,
            topic=build_topic(interaction.user.id, ticket_id, "BOOSTING", "🟡 Awaiting Staff", "Not claimed"),
        )

        await channel.send(
            content=f"{interaction.user.mention} {staff_role.mention}",
            embed=boosting_ticket_embed(interaction.user, ticket_id),
            view=SupportTicketView(),
        )

        await send_log(TICKET_LOG_CHANNEL_ID, "🎫 Boosting Ticket Opened", f"Customer: {interaction.user.mention}\nType: Boosting Request\nTicket: {channel.mention}")
        await interaction.response.send_message(f"Your boosting request ticket has been created: {channel.mention}", ephemeral=True)

    @discord.ui.button(label="Boosting Request", emoji="🚀", style=discord.ButtonStyle.primary, custom_id="prime_panel_boosting")
    async def boosting(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_boosting_ticket(interaction)


# ================= EVENTS / COMMANDS =================
@bot.event
async def on_ready():
    bot.add_view(OrderPanelView())
    bot.add_view(SupportPanelView())
    bot.add_view(BoostingPanelView())
    bot.add_view(OrderTicketView())
    bot.add_view(SupportTicketView())
    bot.add_view(PaymentView())
    bot.add_view(ClosedTicketView())

    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Prime Stock"))

    try:
        synced = await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
        print(f"Synced {len(synced)} commands.")
    except Exception as e:
        print(f"Sync error: {e}")

    print(f"Logged in as {bot.user}")


@bot.tree.command(name="ticketpanel", description="Send the Prime Stock order ticket panel.", guild=discord.Object(id=GUILD_ID))
async def ticketpanel(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator and not is_staff(interaction.user):
        await interaction.response.send_message("Only staff can use this.", ephemeral=True)
        return

    await interaction.channel.send(embed=order_panel_embed(), view=OrderPanelView())
    await interaction.response.send_message("Order ticket panel sent.", ephemeral=True)


@bot.tree.command(name="supportpanel", description="Send the Prime Stock support ticket panel.", guild=discord.Object(id=GUILD_ID))
async def supportpanel(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator and not is_staff(interaction.user):
        await interaction.response.send_message("Only staff can use this.", ephemeral=True)
        return

    await interaction.channel.send(embed=support_panel_embed(), view=SupportPanelView())
    await interaction.response.send_message("Support ticket panel sent.", ephemeral=True)



@bot.tree.command(name="boostingpanel", description="Send the Prime Stock boosting request panel.", guild=discord.Object(id=GUILD_ID))
async def boostingpanel(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator and not is_staff(interaction.user):
        await interaction.response.send_message("Only staff can use this.", ephemeral=True)
        return

    await interaction.channel.send(embed=boosting_panel_embed(), view=BoostingPanelView())
    await interaction.response.send_message("Boosting request panel sent.", ephemeral=True)


@bot.tree.command(name="ping", description="Check if Prime Stock is online.", guild=discord.Object(id=GUILD_ID))
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("⚡ Prime Stock is online.", ephemeral=True)


if not TOKEN:
    raise ValueError("Missing DISCORD_TOKEN. Add it in Railway Variables.")

bot.run(TOKEN)
