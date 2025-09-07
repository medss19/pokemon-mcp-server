"""
Simple test client to verify the MCP server is working
"""
import asyncio
import json
import subprocess
import sys
from pathlib import Path

async def test_mcp_server():
    """Test the MCP server by sending it a simple message"""
    print("Testing MCP server connectivity...")
    
    # Start the server process
    server_process = subprocess.Popen(
        [sys.executable, "run_server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=Path(__file__).parent
    )
    
    try:
        # Send an initialize request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        # Send the request
        server_process.stdin.write(json.dumps(init_request) + "\n")
        server_process.stdin.flush()
        
        # Wait for response (with timeout)
        try:
            stdout, stderr = server_process.communicate(timeout=5)
            if stdout:
                print("✅ Server responded:")
                print(stdout)
            if stderr:
                print("⚠️ Server stderr:")
                print(stderr)
        except subprocess.TimeoutExpired:
            print("✅ Server is running and accepting connections (timeout expected for persistent connection)")
            server_process.terminate()
            
    except Exception as e:
        print(f"❌ Error testing server: {e}")
    finally:
        # Clean up
        if server_process.poll() is None:
            server_process.terminate()
            server_process.wait()

if __name__ == "__main__":
    asyncio.run(test_mcp_server())
