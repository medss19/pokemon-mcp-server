"""
Test script to verify individual components work
"""
import sys
import asyncio
from pathlib import Path

# Add the src directory to the path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

async def test_pokemon_client():
    """Test the Pokemon client"""
    print("Testing Pokemon client...")
    try:
        from pokemon_mcp.data.pokemon_client import PokemonClient
        
        client = PokemonClient()
        pikachu = await client.get_pokemon("pikachu")
        
        if pikachu:
            print(f"✅ Successfully fetched {pikachu.name}")
            print(f"   Types: {pikachu.types}")
            print(f"   HP: {pikachu.stats.hp}")
        else:
            print("❌ Failed to fetch Pikachu")
            
        await client.close()
        
    except Exception as e:
        print(f"❌ Pokemon client error: {e}")
        import traceback
        traceback.print_exc()

async def test_battle_engine():
    """Test the battle engine"""
    print("\nTesting Battle engine...")
    try:
        from pokemon_mcp.data.pokemon_client import PokemonClient
        from pokemon_mcp.battle.engine import BattleEngine
        
        client = PokemonClient()
        engine = BattleEngine()
        
        # Get two Pokemon
        pikachu = await client.get_pokemon("pikachu")
        charizard = await client.get_pokemon("charizard")
        
        if pikachu and charizard:
            result = await engine.simulate_battle(pikachu, charizard)
            print(f"✅ Battle simulation completed")
            print(f"   Winner: {result.winner}")
            print(f"   Total turns: {result.total_turns}")
            print(f"   Log entries: {len(result.logs)}")
        else:
            print("❌ Could not fetch Pokemon for battle")
            
        await client.close()
        
    except Exception as e:
        print(f"❌ Battle engine error: {e}")
        import traceback
        traceback.print_exc()

def test_imports():
    """Test all imports"""
    print("Testing imports...")
    try:
        from pokemon_mcp.server import server
        print("✅ Server import successful")
        
        from pokemon_mcp.data.pokemon_client import PokemonClient
        print("✅ Pokemon client import successful")
        
        from pokemon_mcp.battle.engine import BattleEngine
        print("✅ Battle engine import successful")
        
        from mcp.server import Server
        print("✅ MCP server import successful")
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """Run all tests"""
    print("=== Pokemon MCP Server Component Tests ===\n")
    
    test_imports()
    await test_pokemon_client()
    await test_battle_engine()
    
    print("\n=== Tests completed ===")

if __name__ == "__main__":
    asyncio.run(main())