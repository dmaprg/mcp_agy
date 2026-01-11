import psutil
import json
from mcp.server.fastmcp import FastMCP

# Create a FastMCP server
mcp = FastMCP("System Monitor")

@mcp.tool()
def get_resource_usage() -> str:
    """Returns system resource usage: CPU, RAM, and Disk."""
    # CPU usage
    cpu_percent = psutil.cpu_percent(interval=1)
    
    # RAM usage
    virtual_mem = psutil.virtual_memory()
    ram_usage = {
        "total_gb": round(virtual_mem.total / (1024**3), 2),
        "available_gb": round(virtual_mem.available / (1024**3), 2),
        "percent_used": virtual_mem.percent
    }
    
    # Disk usage
    disk_usage = psutil.disk_usage('/')
    disk_info = {
        "total_gb": round(disk_usage.total / (1024**3), 2),
        "used_gb": round(disk_usage.used / (1024**3), 2),
        "free_gb": round(disk_usage.free / (1024**3), 2),
        "percent_used": disk_usage.percent
    }
    
    usage = {
        "cpu_usage_percent": cpu_percent,
        "ram_usage": ram_usage,
        "disk_usage": disk_info
    }
    
    return json.dumps(usage, indent=2)

@mcp.tool()
def list_top_processes() -> str:
    """Returns the top 5 processes by memory usage."""
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
        try:
            processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    
    # Sort by RSS (Resident Set Size) memory
    top_processes = sorted(processes, key=lambda x: x['memory_info'].rss, reverse=True)[:5]
    
    # Format for readability
    formatted_processes = []
    for p in top_processes:
        formatted_processes.append({
            "pid": p['pid'],
            "name": p['name'],
            "memory_rss_mb": round(p['memory_info'].rss / (1024**2), 2)
        })
    
    return json.dumps(formatted_processes, indent=2)

if __name__ == "__main__":
    mcp.run()
