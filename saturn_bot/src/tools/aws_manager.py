import boto3
import os
from dotenv import load_dotenv
from pathlib import Path
import asyncio
from typing import Optional, Dict, Any

# Get the absolute path to the .env file
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

class AWSManager:
    def __init__(self):
        # Load and validate AWS credentials
        required_env_vars = {
            'AWS_ACCESS_KEY_ID': 'Access Key ID',
            'AWS_SECRET_ACCESS_KEY': 'Secret Access Key',
            'AWS_REGION': 'Region',
            'AWS_INSTANCE_ID': 'Instance ID'
        }
        
        env_values = {key: os.getenv(key, 'Not found') for key in required_env_vars}
        
        # Print configuration for debugging
        print(f"AWS Configuration:")
        print(f"Region: {env_values['AWS_REGION']}")
        print(f"Access Key: {env_values['AWS_ACCESS_KEY_ID'][:4]}... {'(missing)' if env_values['AWS_ACCESS_KEY_ID'] == 'Not found' else '(found)'}")
        print(f"Secret Key: {'(missing)' if env_values['AWS_SECRET_ACCESS_KEY'] == 'Not found' else '(found)'}")
        print(f"Instance ID: {env_values['AWS_INSTANCE_ID']}")

        # Check for missing environment variables
        missing_vars = [name for key, name in required_env_vars.items() if env_values[key] == 'Not found']
        if missing_vars:
            raise Exception(f"Missing required environment variables: {', '.join(missing_vars)}")

        self.ec2 = boto3.client(
            'ec2',
            aws_access_key_id=env_values['AWS_ACCESS_KEY_ID'],
            aws_secret_access_key=env_values['AWS_SECRET_ACCESS_KEY'],
            region_name=env_values['AWS_REGION']
        )
        self.instance_id = env_values['AWS_INSTANCE_ID']

    async def get_instance_details(self) -> Dict[str, Any]:
        """Get instance details from AWS"""
        try:
            response = self.ec2.describe_instances(InstanceIds=[self.instance_id])
            return response['Reservations'][0]['Instances'][0]
        except Exception as e:
            raise Exception(f"Failed to get instance details: {str(e)}")

    async def test_connection(self, interaction):
        await interaction.response.defer()
        try:
            instance = await self.get_instance_details()
            await interaction.followup.send(
                "✅ AWS Connection successful!\n"
                f"Instance '{instance.get('Tags', [{'Value': 'Unknown'}])[0]['Value']}' is accessible."
            )
        except Exception as e:
            await interaction.followup.send(f"❌ AWS Connection failed: {str(e)}")

    async def start_instance(self, interaction):
        await interaction.response.defer()
        try:
            instance = await self.get_instance_details()
            state = instance['State']['Name']
            
            if state == 'running':
                await interaction.followup.send("ℹ️ Instance is already running")
                return
            elif state == 'pending':
                await interaction.followup.send("ℹ️ Instance is already starting")
                return
            
            await interaction.followup.send("🔄 Starting instance...")
            self.ec2.start_instances(InstanceIds=[self.instance_id])
            
            # Wait for instance to start
            waiter = self.ec2.get_waiter('instance_running')
            await asyncio.to_thread(waiter.wait, InstanceIds=[self.instance_id])
            
            # Get final status
            instance = await self.get_instance_details()
            await interaction.followup.send(
                f"✅ Instance started successfully!\n"
                f"Public IP: {instance.get('PublicIpAddress', 'N/A')}\n"
                f"SSH: ssh -i terraform/saturn-key ubuntu@{instance.get('PublicIpAddress', 'N/A')}"
            )
            
        except Exception as e:
            await interaction.followup.send(f"❌ Error starting instance: {str(e)}")

    async def stop_instance(self, interaction):
        await interaction.response.defer()
        try:
            instance = await self.get_instance_details()
            state = instance['State']['Name']
            
            if state == 'stopped':
                await interaction.followup.send("ℹ️ Instance is already stopped")
                return
            elif state == 'stopping':
                await interaction.followup.send("ℹ️ Instance is already stopping")
                return
            
            await interaction.followup.send("🔄 Stopping instance...")
            self.ec2.stop_instances(InstanceIds=[self.instance_id])
            
            # Wait for instance to stop
            waiter = self.ec2.get_waiter('instance_stopped')
            await asyncio.to_thread(waiter.wait, InstanceIds=[self.instance_id])
            await interaction.followup.send("✅ Instance stopped successfully!")
            
        except Exception as e:
            await interaction.followup.send(f"❌ Error stopping instance: {str(e)}")

    async def get_instance_status(self, interaction):
        await interaction.response.defer()
        try:
            instance = await self.get_instance_details()
            state = instance['State']['Name']
            
            status_emoji = {
                'running': '🟢',
                'pending': '🟡',
                'stopping': '🟡',
                'stopped': '🔴',
                'shutting-down': '🟡',
                'terminated': '⚫'
            }

            # Get instance name from tags
            instance_name = next((tag['Value'] for tag in instance.get('Tags', []) if tag['Key'] == 'Name'), 'Unknown')

            status = [
                f"{status_emoji.get(state, '❓')} Instance Status:",
                f"Name: {instance_name}",
                f"State: {state}",
            ]

            if state == 'running':
                status.extend([
                    f"Public IP: {instance.get('PublicIpAddress', 'N/A')}",
                    f"Instance Type: {instance['InstanceType']}",
                    f"Launch Time: {instance['LaunchTime'].strftime('%Y-%m-%d %H:%M:%S')}",
                    "",
                    "SSH Connection:",
                    f"ssh -i terraform/saturn-key ubuntu@{instance.get('PublicIpAddress', 'N/A')}"
                ])
            
            await interaction.followup.send('\n'.join(status))
        except Exception as e:
            await interaction.followup.send(f"❌ Error getting instance status: {str(e)}") 