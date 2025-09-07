"""
Demo script to showcase the Pokemon MCP Server features
Run this to see the battle system in action!
"""
import sys
import asyncio
import json
from pathlib import Path

# Add the src directory to the path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

async def demo_battle():
    """Demonstrate the enhanced battle system"""
    print("🎮 Pokemon MCP Server - Battle Demo")
    print("=" * 50)
    
    try:
        from pokemon_mcp.data.pokemon_client import PokemonClient
        from pokemon_mcp.battle.engine import BattleEngine
        
        client = PokemonClient()
        engine = BattleEngine()
        
        print("🔍 Fetching Pokemon data...")
        pikachu = await client.get_pokemon("pikachu")
        charizard = await client.get_pokemon("charizard")
        
        if pikachu and charizard:
            print(f"✅ Loaded {pikachu.name.title()} (Electric-type)")
            print(f"   HP: {pikachu.stats.hp}, Attack: {pikachu.stats.attack}, Speed: {pikachu.stats.speed}")
            print(f"✅ Loaded {charizard.name.title()} (Fire/Flying-type)")
            print(f"   HP: {charizard.stats.hp}, Attack: {charizard.stats.attack}, Speed: {charizard.stats.speed}")
            
            print("\n⚔️  BATTLE BEGINS!")
            print("-" * 30)
            
            result = engine.simulate_battle(pikachu, charizard)
            
            # Show battle summary
            print(f"\n🏆 BATTLE RESULT:")
            print(f"   Winner: {result.winner.title()}")
            print(f"   Total Turns: {result.total_turns}")
            print(f"   Battle Log Entries: {len(result.logs)}")
            
            print(f"\n📝 BATTLE LOG (Last 10 entries):")
            for log in result.logs[-10:]:
                print(f"   Turn {log.turn}: {log.message}")
            
        await client.close()
        
    except Exception as e:
        print(f"❌ Demo error: {e}")
        import traceback
        traceback.print_exc()

async def demo_pokemon_data():
    """Demonstrate Pokemon data fetching"""
    print("\n🔍 Pokemon Data Demo")
    print("=" * 30)
    
    try:
        from pokemon_mcp.data.pokemon_client import PokemonClient
        
        client = PokemonClient()
        
        pokemon_list = ["pikachu", "charizard", "blastoise", "venusaur"]
        
        for name in pokemon_list:
            pokemon = await client.get_pokemon(name)
            if pokemon:
                print(f"\n📊 {pokemon.name.title()} (#{pokemon.id})")
                print(f"   Types: {', '.join(pokemon.types).title()}")
                print(f"   Stats: HP={pokemon.stats.hp}, ATK={pokemon.stats.attack}, DEF={pokemon.stats.defense}")
                print(f"   Abilities: {', '.join(pokemon.abilities[:2])}")
                print(f"   Sample Moves: {', '.join(pokemon.moves[:3])}")
        
        await client.close()
        
    except Exception as e:
        print(f"❌ Data demo error: {e}")

async def main():
    """Run all demos"""
    print("🎮 POKEMON MCP SERVER - FEATURE DEMONSTRATION")
    print("=" * 60)
    
    await demo_pokemon_data()
    await demo_battle()
    
    print("\n" + "=" * 60)
    print("✅ Demo completed successfully!")
    print("\n💡 To start the MCP server, run: python run_server.py")
    print("💡 The server will show 'Server ready for MCP connections via stdio'")
    print("💡 This means it's working correctly and waiting for MCP clients!")

if __name__ == "__main__":
    asyncio.run(main())
