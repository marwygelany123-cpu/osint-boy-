import discord
from discord.ext import commands
import asyncio
import io
import os
from faker import Faker
import phonenumbers
from phonenumbers import geocoder, carrier

intents = discord.Intents.all()
TOKEN = os.getenv("DISCORD_TOKEN", "حط_التوكن_بتاعك_هنا")

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)
fake = Faker()

def create_embed(title, description=None, color=0x3498db):
    embed = discord.Embed(title=title, description=description, color=color)
    return embed

async def send_long_output(ctx, content, tool_name):
    output = content.strip()
    if len(output) > 1900:
        with io.BytesIO(output.encode('utf-8')) as file_bin:
            file = discord.File(file_bin, filename=f"{tool_name}_report.txt")
            await ctx.send(f"✅ Results for {tool_name}:", file=file)
    else:
        await ctx.send(f"**Results for {tool_name}:**\n```\n{output}\n```")

async def run_osint_tool(ctx, cmd_list, tool_name):
    async with ctx.typing():
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd_list,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            output = (stdout + stderr).decode('utf-8', errors='ignore').strip()
            await send_long_output(ctx, output, tool_name)
        except Exception as e:
            await ctx.send(f"❌ Error: {str(e)}")

@bot.command()
@commands.cooldown(1, 10, commands.BucketType.user)
async def scan(ctx, method: str, target: str):
    tools = {
        "holehe": ["holehe", target],
        "sherlock": ["python3", "sherlock.py", target],
        "maigret": ["maigret", target]
    }
    method = method.lower()
    if method in tools:
        await ctx.send(f"🔎 Scanning {target} with {method}...")
        await run_osint_tool(ctx, tools[method], method)
    else:
        await ctx.send("❌ Tool not found")

@bot.command()
async def phone(ctx, number: str):
    try:
        parsed = phonenumbers.parse(number)
        region = geocoder.description_for_number(parsed, "en")
        await ctx.send(f"📞 Region: {region}")
    except:
        await ctx.send("❌ Invalid number")

@bot.command()
async def fakeid(ctx):
    await ctx.send(f"Name: {fake.name()}\nIP: {fake.ipv4()}")

@bot.event
async def on_ready():
    print(f"✅ Bot is online: {bot.user}")

bot.run(TOKEN)
