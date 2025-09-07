"""
Simple script to run the Pokemon MCP server
"""
import sys
import asyncio
import traceback
from pathlib import Path

# Add the src directory to the path so we can import our modules
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from pokemon_mcp.server import main

if __name__ == "__main__":
    print("Starting Pokemon Battle MCP Server...")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Server error: {e}")
        print("\nFull traceback:")
        traceback.print_exc()
        sys.exit(1)