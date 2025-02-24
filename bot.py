import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from weather_api import get_weather_data
from config import HELP_MESSAGE
import logging

# Set up logging with more detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('weather_bot')

# Load environment variables
load_dotenv()

# Bot setup with minimal intents
intents = discord.Intents.default()  # Use default intents instead of none
intents.message_content = True  # Enable message content intent
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    logger.info(f'{bot.user} has connected to Discord!')
    logger.info(f'Bot is in {len(bot.guilds)} guilds')
    await bot.change_presence(activity=discord.Game(name="!weather <city>"))

@bot.event
async def on_command_error(ctx, error):
    """Global error handler for commands"""
    logger.error(f"Command error occurred: {str(error)}")
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Command not found. Use !help_weather to see available commands.")
    elif isinstance(error, commands.MissingRequiredArgument):
        if ctx.command.name == 'weather':
            await ctx.send("Please provide a city name. Usage: !weather <city>")
        else:
            await ctx.send(f"Missing required argument for {ctx.command.name} command.")
    else:
        logger.error(f"Unexpected error: {str(error)}")
        await ctx.send(f"An error occurred while processing the command: {str(error)}")

@bot.command(name='ping')
async def ping(ctx):
    """Simple command to test bot responsiveness"""
    logger.info(f"Ping command received from {ctx.author}")
    await ctx.send("Pong!")

@bot.command(name='weather')
async def weather(ctx, *, city: str = None):
    """Get weather information for a specified city"""
    logger.info(f"Weather command received for city: {city}")

    if not city:
        await ctx.send("Please provide a city name. Usage: !weather <city>")
        return

    try:
        weather_data = await get_weather_data(city)

        if weather_data.get('cod') in ['404', '500']:
            await ctx.send(weather_data.get('message', 'Error fetching weather data'))
            return

        current = weather_data.get('current_condition', [{}])[0]

        # Create embedded message
        embed = discord.Embed(
            title=f"Weather in {city.title()}",
            description=current.get('weatherDesc', [{}])[0].get('value', 'N/A'),
            color=0x00ff00
        )

        # Add weather information fields
        temp_c = current.get('temp_C', 'N/A')
        temp_f = current.get('temp_F', 'N/A')
        embed.add_field(
            name="Temperature",
            value=f"{temp_c}°C ({temp_f}°F)",
            inline=False
        )
        embed.add_field(
            name="Humidity",
            value=f"{current.get('humidity', 'N/A')}%",
            inline=True
        )
        embed.add_field(
            name="Wind Speed",
            value=f"{current.get('windspeedKmph', 'N/A')} km/h",
            inline=True
        )
        embed.add_field(
            name="Pressure",
            value=f"{current.get('pressure', 'N/A')} mb",
            inline=True
        )

        await ctx.send(embed=embed)

    except Exception as e:
        logger.error(f"Error processing weather command: {str(e)}")
        await ctx.send(f"An error occurred while fetching weather data: {str(e)}")

@bot.command(name='help_weather')
async def help_weather(ctx):
    """Display help information for weather commands"""
    logger.info("Help command received")
    await ctx.send(HELP_MESSAGE)

if __name__ == '__main__':
    bot.run(os.getenv('DISCORD_TOKEN'))