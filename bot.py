# -*- coding: utf-8 -*-
import discord
from discord.ext import commands
import os
import asyncio

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Replace these IDs with your actual Discord channel/category IDs
ADMIN_SIGNAL_CHANNEL_ID = 1354557383208079572   # Hidden admin channel
PUBLIC_SIGNAL_CHANNEL_ID = 1354557176164782311  # Public signals channel
TICKET_CATEGORY_ID = 1354558070004388081        # Ticket category

@bot.event
async def on_ready():
    print(f"{bot.user.name} is online! 🚀")

# Signal Forwarding (Admin → Public)
@bot.event
async def on_message(message):
    if message.channel.id == ADMIN_SIGNAL_CHANNEL_ID and not message.author.bot:
        public_channel = bot.get_channel(PUBLIC_SIGNAL_CHANNEL_ID)
        await public_channel.send(f"📢 **New Signal**: {message.content}")
    
    # Auto-Kick Spammers
    if not message.author.guild_permissions.administrator:
        spam_words = ["http://", "https://", "promo", "join", "discord.gg/"]
        if any(word in message.content.lower() for word in spam_words):
            await message.author.kick(reason="Spam/Advertising")
            await message.channel.send(f"🚨 {message.author.mention} was kicked for spam!")
    
    await bot.process_commands(message)

# Ticket System
@bot.command()
async def ticket(ctx, *, reason="No reason provided"):
    category = bot.get_channel(TICKET_CATEGORY_ID)
    ticket_channel = await ctx.guild.create_text_channel(
        name=f"ticket-{ctx.author.name}",
        category=category,
        topic=f"Ticket by {ctx.author.mention} | Reason: {reason}"
    )
    await ticket_channel.set_permissions(ctx.author, read_messages=True, send_messages=True)
    await ticket_channel.send(
        f"{ctx.author.mention}, support will assist you shortly!\n"
        f"**Reason:** {reason}"
    )

# Auto-restart logic
async def main():
    try:
        await bot.start(os.environ['TOKEN'])
    except KeyboardInterrupt:
        await bot.close()

# Start the bot
if __name__ == "__main__":
    asyncio.run(main())
