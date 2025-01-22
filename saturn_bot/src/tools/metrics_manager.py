import os
import aiohttp
from dotenv import load_dotenv
from pathlib import Path

# Get the absolute path to the .env file
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

class MetricsManager:
    def __init__(self):
        self.prometheus_url = os.getenv('PROMETHEUS_URL', 'http://localhost:9090')
        
    async def get_system_metrics(self):
        """Get basic system metrics from Prometheus"""
        try:
            metrics = {}
            
            # CPU Usage Query
            cpu_query = 'avg(rate(node_cpu_seconds_total{mode!="idle"}[5m])) * 100'
            metrics['cpu_usage'] = await self._query_prometheus(cpu_query)
            
            # Memory Usage Query
            mem_query = '(node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100'
            metrics['memory_usage'] = await self._query_prometheus(mem_query)
            
            # Disk Usage Query
            disk_query = '(node_filesystem_size_bytes{mountpoint="/"} - node_filesystem_free_bytes{mountpoint="/"}) / node_filesystem_size_bytes{mountpoint="/"} * 100'
            metrics['disk_usage'] = await self._query_prometheus(disk_query)
            
            return self._format_metrics(metrics)
        except Exception as e:
            raise Exception(f"Failed to get system metrics: {str(e)}")
    
    async def _query_prometheus(self, query):
        """Execute a query against Prometheus"""
        try:
            async with aiohttp.ClientSession() as session:
                params = {'query': query}
                async with session.get(f"{self.prometheus_url}/api/v1/query", params=params) as response:
                    if response.status != 200:
                        raise Exception(f"Prometheus query failed with status {response.status}")
                    
                    data = await response.json()
                    if data['status'] != 'success':
                        raise Exception("Query returned unsuccessful status")
                    
                    # Extract the value from the result
                    result = data['data']['result']
                    if not result:
                        return 0.0
                    return float(result[0]['value'][1])
        except Exception as e:
            raise Exception(f"Prometheus query failed: {str(e)}")
    
    def _format_metrics(self, metrics):
        """Format metrics into a readable string"""
        return (
            "📊 System Metrics:\n"
            f"CPU Usage: {metrics['cpu_usage']:.1f}%\n"
            f"Memory Usage: {metrics['memory_usage']:.1f}%\n"
            f"Disk Usage: {metrics['disk_usage']:.1f}%"
        )

if __name__ == "__main__":
    # Test the metrics manager
    import asyncio
    
    async def test():
        manager = MetricsManager()
        metrics = await manager.get_system_metrics()
        print(metrics)
    
    asyncio.run(test()) 