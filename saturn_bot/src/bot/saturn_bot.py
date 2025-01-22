import os
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
import sys
from pathlib import Path
import asyncio

# Add the src directory to Python path
src_dir = str(Path(__file__).parent.parent)
if src_dir not in sys.path:
    sys.path.append(src_dir)

from tools.aws_manager import AWSManager
from tools.metrics_manager import MetricsManager
from tools.docker_manager import DockerManager

# Load environment variables
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Bot configuration
DISCORD_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
SERVER_ID = int(os.getenv('DISCORD_SERVER_ID'))

# Initialize bot with intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

class SaturnBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=intents)
        self.aws_manager = AWSManager()
        self.metrics_manager = MetricsManager()
        self.docker_manager = DockerManager()
        self.alert_task = None
        
    async def setup_hook(self):
        try:
            print('Starting command sync...')
            # Get the guild object
            guild = discord.Object(id=SERVER_ID)
            # This copies the global commands over to your guild
            self.tree.copy_global_to(guild=guild)
            # Sync commands to the specific guild
            await self.tree.sync(guild=guild)
            print(f'Successfully synced commands to guild ID: {SERVER_ID}')
            
            # For debugging: Print all registered commands
            commands = await self.tree.fetch_commands(guild=guild)
            print("Registered commands:")
            for cmd in commands:
                print(f"- /{cmd.name}: {cmd.description}")
                
            # Start alert monitoring
            self.alert_task = self.loop.create_task(self._monitor_alerts())
        except Exception as e:
            print(f'Failed to sync commands: {str(e)}')
            raise e

    async def _monitor_alerts(self):
        """Background task to monitor container alerts"""
        alert_channel = None
        while True:
            try:
                if not alert_channel:
                    guild = self.get_guild(SERVER_ID)
                    if guild:
                        # Try to find a channel named 'alerts' or use the first text channel
                        alert_channel = discord.utils.get(guild.text_channels, name='alerts')
                        if not alert_channel:
                            alert_channel = guild.text_channels[0]
                
                if alert_channel:
                    alerts = await self.docker_manager.check_alerts()
                    if any("⚠️" in alert for alert in alerts):
                        await alert_channel.send("\n".join(alerts))
                
                await asyncio.sleep(300)  # Check every 5 minutes
            except Exception as e:
                print(f"Error in alert monitoring: {str(e)}")
                await asyncio.sleep(60)  # Wait a minute before retrying

    async def handle_command_error(self, interaction: discord.Interaction, error: Exception, command_name: str):
        """Centralized error handling for commands"""
        error_message = f"Failed to execute {command_name}: {str(error)}"
        print(error_message)
        
        try:
            if not interaction.response.is_done():
                await interaction.response.send_message(f"❌ {error_message}")
            else:
                await interaction.followup.send(f"❌ {error_message}")
        except Exception as e:
            print(f"Failed to send error message: {str(e)}")

bot = SaturnBot()

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print(f'Serving guild ID: {SERVER_ID}')

# AWS Test Command
@bot.tree.command(name="aws_test", description="Test AWS connectivity")
async def aws_test(interaction: discord.Interaction):
    try:
        await bot.aws_manager.test_connection(interaction)
    except Exception as e:
        await bot.handle_command_error(interaction, e, "aws_test")

# Instance Management Commands
@bot.tree.command(name="instance", description="Manage EC2 instance")
@app_commands.describe(action="Action to perform (start/stop/status)")
async def instance(interaction: discord.Interaction, action: str):
    try:
        if action == "start":
            await bot.aws_manager.start_instance(interaction)
        elif action == "stop":
            await bot.aws_manager.stop_instance(interaction)
        elif action == "status":
            await bot.aws_manager.get_instance_status(interaction)
        else:
            await interaction.response.send_message("❌ Invalid action. Use start, stop, or status")
    except Exception as e:
        await bot.handle_command_error(interaction, e, f"instance {action}")

# Metrics Command
@bot.tree.command(name="metrics", description="Get current resource metrics")
@app_commands.guilds(discord.Object(id=SERVER_ID))
async def metrics(interaction: discord.Interaction):
    try:
        await interaction.response.defer()
        metrics_text = await bot.metrics_manager.get_system_metrics()
        await interaction.followup.send(metrics_text)
    except Exception as e:
        await bot.handle_command_error(interaction, e, "metrics")

# Docker Commands
@bot.tree.command(name="containers", description="List all Docker containers")
@app_commands.guilds(discord.Object(id=SERVER_ID))
async def containers(interaction: discord.Interaction):
    try:
        await interaction.response.defer()
        container_list = await bot.docker_manager.list_containers()
        await interaction.followup.send(container_list)
    except Exception as e:
        await bot.handle_command_error(interaction, e, "containers")

@bot.tree.command(name="docker", description="Manage Docker containers")
@app_commands.describe(
    action="Action to perform (start/stop)",
    container="Name of the container"
)
@app_commands.guilds(discord.Object(id=SERVER_ID))
async def docker(interaction: discord.Interaction, action: str, container: str):
    try:
        await interaction.response.defer()
        if action == "start":
            result = await bot.docker_manager.start_container(container)
        elif action == "stop":
            result = await bot.docker_manager.stop_container(container)
        else:
            result = "❌ Invalid action. Use start or stop"
        await interaction.followup.send(result)
    except Exception as e:
        await bot.handle_command_error(interaction, e, f"docker {action}")

@bot.tree.command(name="logs", description="Get container logs")
@app_commands.describe(
    container="Name of the container",
    lines="Number of log lines to show (default: 50)"
)
@app_commands.guilds(discord.Object(id=SERVER_ID))
async def logs(interaction: discord.Interaction, container: str, lines: int = 50):
    try:
        await interaction.response.defer()
        log_chunks = await bot.docker_manager.get_container_logs(container, lines)
        
        # Send first chunk with followup
        if log_chunks:
            await interaction.followup.send(log_chunks[0])
            
            # Send remaining chunks as additional messages
            for chunk in log_chunks[1:]:
                await interaction.channel.send(chunk)
                await asyncio.sleep(0.5)  # Add small delay between messages to maintain order
    except Exception as e:
        await bot.handle_command_error(interaction, e, "logs")

@bot.tree.command(name="alerts", description="Check container alerts")
@app_commands.guilds(discord.Object(id=SERVER_ID))
async def alerts(interaction: discord.Interaction):
    try:
        await interaction.response.defer()
        alerts = await bot.docker_manager.check_alerts()
        await interaction.followup.send("\n".join(alerts))
    except Exception as e:
        await bot.handle_command_error(interaction, e, "alerts")

# Run the bot
if __name__ == "__main__":
    bot.run(DISCORD_TOKEN) 