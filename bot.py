# -*- coding: utf-8 -*-
import discord
from discord.ext import commands
import os
import asyncio

bot = commands.Bot(command_prefix="!")

# Configuration
ADMIN_CHANNEL_ID = 1354557383208079572  # Your admin channel ID
signal_channels = {"forex": 1354557176164782311, "crypto": 1354726609277685902}  # Format: {"forex": channel_id, "crypto": channel_id}
message_map = {}      # Tracks {admin_msg_id: public_msg_id}

@bot.event
async def on_ready():
    print(f"{bot.user.name} is online! 🚀")
    # Initialize default channels if not set
    if not signal_channels:
        admin_channel = bot.get_channel(ADMIN_CHANNEL_ID)
        await admin_channel.send("⚠️ No channels configured! Use `!setchannel forex #channel`")

@bot.command()
async def setchannel(ctx, signal_type: str, channel: discord.TextChannel):
    """Set forwarding channel for signal types (forex/crypto)"""
    if signal_type.lower() in ["forex", "crypto"]:
        signal_channels[signal_type.lower()] = channel.id
        await ctx.send(f"✅ {signal_type.upper()} signals will forward to {channel.mention}")
    else:
        await ctx.send("❌ Invalid type! Use `forex` or `crypto`")

@bot.event
async def on_message(message):
    if message.channel.id == ADMIN_CHANNEL_ID and not message.author.bot:
        # Check if message starts with signal type
        content = message.content.lower()
        
        if content.startswith(("forex", "crypto")):
            signal_type = content.split()[0]
            if signal_type in signal_channels:
                # Remove the prefix and forward clean message
                clean_content = message.content[len(signal_type):].strip()
                public_channel = bot.get_channel(signal_channels[signal_type])
                
                # Forward with attachments
                sent_message = await public_channel.send(
                    content=clean_content,
                    files=[await attachment.to_file() for attachment in message.attachments]
                )
                message_map[message.id] = sent_message.id
        else:
            await message.channel.send("❌ Start messages with `forex` or `crypto`")

    await bot.process_commands(message)

@bot.event
async def on_message_edit(before, after):
    if after.channel.id == ADMIN_CHANNEL_ID and not after.author.bot:
        try:
            public_msg_id = message_map[after.id]
            signal_type = after.content.lower().split()[0]
            public_channel = bot.get_channel(signal_channels[signal_type])
            public_msg = await public_channel.fetch_message(public_msg_id)
            
            clean_content = after.content[len(signal_type):].strip()
            await public_msg.edit(
                content=clean_content,
                attachments=[await attachment.to_file() for attachment in after.attachments]
            )
        except:
            pass

@bot.event
async def on_message_delete(message):
    if message.channel.id == ADMIN_CHANNEL_ID and not message.author.bot:
        try:
            public_msg_id = message_map[message.id]
            signal_type = message.content.lower().split()[0]
            public_channel = bot.get_channel(signal_channels[signal_type])
            public_msg = await public_channel.fetch_message(public_msg_id)
            await public_msg.delete()
            del message_map[message.id]
        except:
            pass

# Auto-restart system
async def main():
    while True:
        try:
            await bot.start(os.environ['TOKEN'])
        except Exception as e:
            print(f"CRASH: {e}. Restarting in 5s...")
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())
