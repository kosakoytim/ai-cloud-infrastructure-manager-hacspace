import docker
import os
from dotenv import load_dotenv
from pathlib import Path
import asyncio
from datetime import datetime, timedelta
import json
from typing import List, Tuple

# Get the absolute path to the .env file
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

class DockerManager:
    def __init__(self):
        self.client = docker.from_env()
        self.alert_thresholds = {
            'cpu_percent': float(os.getenv('DOCKER_ALERT_CPU_THRESHOLD', '80')),
            'memory_percent': float(os.getenv('DOCKER_ALERT_MEMORY_THRESHOLD', '80')),
        }
        
    async def list_containers(self):
        """List all containers with their status"""
        try:
            containers = self.client.containers.list(all=True)
            if not containers:
                return "No containers found"
            
            status = ["📦 Containers:"]
            for container in containers:
                # Get container status emoji
                status_emoji = {
                    'running': '🟢',
                    'exited': '🔴',
                    'created': '⚪',
                    'paused': '⏸️',
                    'restarting': '🔄'
                }.get(container.status, '❓')
                
                # Get container name (first name without '/')
                name = container.name if isinstance(container.name, str) else container.name[0].lstrip('/')
                
                # Add container info to status list
                status.append(f"{status_emoji} {name} ({container.status})")
                
                # If running, add basic stats
                if container.status == 'running':
                    try:
                        stats = container.stats(stream=False)
                        cpu_percent = self._calculate_cpu_percent(stats)
                        memory_percent = self._calculate_memory_percent(stats)
                        status.append(f"   CPU: {cpu_percent:.1f}% | Memory: {memory_percent:.1f}%")
                    except:
                        status.append("   Unable to get container stats")
            
            return "\n".join(status)
        except Exception as e:
            raise Exception(f"Failed to list containers: {str(e)}")

    async def start_container(self, container_name):
        """Start a container by name"""
        try:
            container = self.client.containers.get(container_name)
            if container.status == 'running':
                return f"Container '{container_name}' is already running"
            container.start()
            return f"✅ Started container '{container_name}'"
        except docker.errors.NotFound:
            raise Exception(f"Container '{container_name}' not found")
        except Exception as e:
            raise Exception(f"Failed to start container: {str(e)}")

    async def stop_container(self, container_name):
        """Stop a container by name"""
        try:
            container = self.client.containers.get(container_name)
            if container.status != 'running':
                return f"Container '{container_name}' is not running"
            container.stop()
            return f"✅ Stopped container '{container_name}'"
        except docker.errors.NotFound:
            raise Exception(f"Container '{container_name}' not found")
        except Exception as e:
            raise Exception(f"Failed to stop container: {str(e)}")

    async def get_container_logs(self, container_name: str, tail: int = 50) -> List[str]:
        """Get container logs split into Discord-friendly chunks"""
        try:
            container = self.client.containers.get(container_name)
            logs = container.logs(tail=tail, timestamps=True).decode('utf-8')
            
            if not logs:
                return [f"No logs found for container '{container_name}'"]
            
            # Format logs with timestamps
            formatted_logs = []
            for line in logs.splitlines():
                # Split timestamp from log message
                try:
                    timestamp = line[:30]
                    message = line[30:]
                    dt = datetime.strptime(timestamp.split('.')[0], '%Y-%m-%dT%H:%M:%S')
                    formatted_logs.append(f"{dt.strftime('%Y-%m-%d %H:%M:%S')} {message}")
                except:
                    formatted_logs.append(line)
            
            # Split logs into chunks that fit Discord's message limit
            chunks = []
            current_chunk = [f"📜 Logs for {container_name} (Part 1):"]
            current_length = len(current_chunk[0]) + 6  # Add 6 for the code block markers ```\n```
            
            for i, log_line in enumerate(formatted_logs, 1):
                # Calculate length with new line
                line_length = len(log_line) + 1  # +1 for newline
                
                # If adding this line would exceed Discord's limit, start a new chunk
                if current_length + line_length > 1900:  # Leave some margin for safety
                    chunks.append("```\n" + "\n".join(current_chunk) + "\n```")
                    part_num = len(chunks) + 1
                    current_chunk = [f"📜 Logs for {container_name} (Part {part_num}):"]
                    current_length = len(current_chunk[0]) + 6
                
                current_chunk.append(log_line)
                current_length += line_length
            
            # Add the last chunk if it has content
            if current_chunk:
                chunks.append("```\n" + "\n".join(current_chunk) + "\n```")
            
            return chunks
            
        except docker.errors.NotFound:
            return [f"Container '{container_name}' not found"]
        except Exception as e:
            return [f"Failed to get container logs: {str(e)}"]

    async def check_alerts(self):
        """Check container metrics and return alerts if thresholds are exceeded"""
        try:
            alerts = []
            containers = self.client.containers.list()
            
            for container in containers:
                try:
                    stats = container.stats(stream=False)
                    name = container.name if isinstance(container.name, str) else container.name[0].lstrip('/')
                    
                    # Calculate CPU and memory usage
                    cpu_percent = self._calculate_cpu_percent(stats)
                    memory_percent = self._calculate_memory_percent(stats)
                    
                    # Check thresholds
                    if cpu_percent > self.alert_thresholds['cpu_percent']:
                        alerts.append(f"⚠️ High CPU usage in {name}: {cpu_percent:.1f}%")
                    if memory_percent > self.alert_thresholds['memory_percent']:
                        alerts.append(f"⚠️ High memory usage in {name}: {memory_percent:.1f}%")
                except:
                    continue
            
            return alerts if alerts else ["✅ All containers are running within normal parameters"]
        except Exception as e:
            raise Exception(f"Failed to check alerts: {str(e)}")

    def _calculate_cpu_percent(self, stats):
        """Calculate CPU usage percentage from stats"""
        cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - \
                   stats['precpu_stats']['cpu_usage']['total_usage']
        system_delta = stats['cpu_stats']['system_cpu_usage'] - \
                      stats['precpu_stats']['system_cpu_usage']
        online_cpus = stats['cpu_stats'].get('online_cpus', len(stats['cpu_stats']['cpu_usage'].get('percpu_usage', [1])))
        
        if system_delta > 0.0:
            return (cpu_delta / system_delta) * online_cpus * 100.0
        return 0.0

    def _calculate_memory_percent(self, stats):
        """Calculate memory usage percentage from stats"""
        usage = stats['memory_stats']['usage']
        limit = stats['memory_stats']['limit']
        return (usage / limit) * 100.0

if __name__ == "__main__":
    # Test the Docker manager
    async def test():
        manager = DockerManager()
        print("Listing containers:")
        print(await manager.list_containers())
        print("\nChecking alerts:")
        print(await manager.check_alerts())
    
    asyncio.run(test()) 