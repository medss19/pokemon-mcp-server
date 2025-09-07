"""
Test script to demonstrate how an LLM would interact with the MCP server
This shows the actual MCP protocol communication
"""
import asyncio
import json
import subprocess
import sys
from pathlib import Path

# Add the src directory to the path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

class MockMCPClient:
    """
    Mock MCP client to demonstrate LLM interaction patterns
    This simulates how Claude, GPT, or other LLMs would query the server
    """
    
    def __init__(self):
        self.server_process = None
        
    async def start_server(self):
        """Start the MCP server process"""
        print("🚀 Starting MCP server...")
        self.server_process = subprocess.Popen(
            [sys.executable, "run_server.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=Path(__file__).parent
        )
        
        # Wait a moment for server to start
        await asyncio.sleep(2)
        print("✅ MCP server started")
    
    def send_mcp_request(self, method, params=None):
        """Send MCP request to server"""
        if not self.server_process:
            raise RuntimeError("Server not started")
            
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params or {}
        }
        
        request_json = json.dumps(request) + "\n"
        self.server_process.stdin.write(request_json)
        self.server_process.stdin.flush()
        
        # Read response
        response_line = self.server_process.stdout.readline()
        return json.loads(response_line.strip()) if response_line.strip() else None
    
    def stop_server(self):
        """Stop the MCP server"""
        if self.server_process:
            self.server_process.terminate()
            self.server_process.wait()
            print("🛑 MCP server stopped")

async def demonstrate_llm_queries():
    """
    Demonstrate how an LLM would query the Pokemon MCP server
    These are the exact patterns an AI would use
    """
    print("=" * 60)
    print("🤖 LLM → MCP Server Interaction Demonstration")
    print("=" * 60)
    
    # Note: For this demo, we'll simulate the queries since setting up 
    # a full MCP client requires more complex stdio handling
    
    print("\n🔍 Example 1: LLM asks 'Tell me about Pikachu'")
    print("MCP Call that would be made:")
    pikachu_query = {
        "tool": "get_pokemon",
        "arguments": {"name_or_id": "pikachu"}
    }
    print(json.dumps(pikachu_query, indent=2))
    
    print("\n⚔️ Example 2: LLM asks 'Who would win: Charizard vs Blastoise?'")
    print("MCP Call that would be made:")
    battle_query = {
        "tool": "simulate_battle", 
        "arguments": {"pokemon1": "charizard", "pokemon2": "blastoise"}
    }
    print(json.dumps(battle_query, indent=2))
    
    print("\n🔄 Example 3: LLM asks 'What's Bulbasaur's evolution line?'")
    print("MCP Call that would be made:")
    evolution_query = {
        "tool": "get_evolution_chain",
        "arguments": {"pokemon_name": "bulbasaur"}
    }
    print(json.dumps(evolution_query, indent=2))
    
    print("\n📖 Example 4: LLM reads Pokemon resource")
    print("MCP Resource read:")
    resource_read = {
        "resource": "pokemon://data",
        "purpose": "Understanding available Pokemon data structure"
    }
    print(json.dumps(resource_read, indent=2))
    
    print("\n" + "=" * 60)
    print("🎯 How LLMs Use This Data:")
    print("=" * 60)
    
    print("""
    1. ANALYSIS: LLM receives structured JSON data about Pokemon
       - Compares stats between Pokemon
       - Explains type advantages/disadvantages  
       - Provides strategic recommendations
    
    2. BATTLE SIMULATION: LLM gets detailed battle logs
       - Analyzes why certain Pokemon won/lost
       - Explains type effectiveness in action
       - Provides turn-by-turn battle breakdowns
    
    3. TEAM BUILDING: LLM uses evolution and type data
       - Suggests balanced team compositions
       - Recommends evolution strategies
       - Explains synergies between Pokemon
    
    4. EDUCATIONAL: LLM teaches Pokemon mechanics
       - Explains complex battle calculations
       - Describes status effect interactions
       - Provides strategic insights
    """)

async def test_direct_components():
    """Test components directly (since full MCP client is complex)"""
    print("\n" + "=" * 60)
    print("🧪 Direct Component Testing (Simulating MCP Calls)")
    print("=" * 60)
    
    try:
        from pokemon_mcp.data.pokemon_client import PokemonClient
        from pokemon_mcp.battle.engine import BattleEngine
        
        client = PokemonClient()
        engine = BattleEngine()
        
        print("\n1️⃣ Testing get_pokemon tool:")
        pikachu = await client.get_pokemon("pikachu")
        if pikachu:
            print(f"✅ Successfully retrieved: {pikachu.name}")
            print(f"   Types: {pikachu.types}")
            print(f"   Stats: HP={pikachu.stats.hp}, ATK={pikachu.stats.attack}, SPD={pikachu.stats.speed}")
            print(f"   Abilities: {pikachu.abilities[:3]}")
        else:
            print("❌ Failed to retrieve Pikachu")
        
        print("\n2️⃣ Testing evolution chain:")
        if pikachu:
            evolution = await client.get_evolution_chain(pikachu.species_url)
            if 'evolution_chain' in evolution:
                chain_names = [p['name'] for p in evolution['evolution_chain']]
                print(f"✅ Evolution chain: {' → '.join(chain_names)}")
            else:
                print("❌ No evolution data found")
        
        print("\n3️⃣ Testing battle simulation:")
        charizard = await client.get_pokemon("charizard")
        if pikachu and charizard:
            result = await engine.simulate_battle(pikachu, charizard)
            print(f"✅ Battle completed: {result.winner} defeated {result.loser}")
            print(f"   Duration: {result.total_turns} turns")
            print(f"   Sample log: {result.logs[1].message if len(result.logs) > 1 else 'N/A'}")
        else:
            print("❌ Could not simulate battle")
        
        await client.close()
        
    except Exception as e:
        print(f"❌ Component test error: {e}")
        import traceback
        traceback.print_exc()

def explain_mcp_architecture():
    """Explain how MCP works vs the web demo"""
    print("\n" + "=" * 60)
    print("🏗️ MCP Architecture Explanation")
    print("=" * 60)
    
    print("""
    PRODUCTION MCP FLOW:
    LLM (Claude/GPT) ↔ MCP Client ↔ MCP Server ↔ Pokemon Data
    
    1. LLM asks: "Compare Pikachu and Charizard"
    2. MCP Client translates to tool calls
    3. MCP Server processes requests  
    4. Server fetches Pokemon data
    5. Structured data returned to LLM
    6. LLM analyzes and responds to user
    
    WEB DEMO FLOW (Development only):
    Browser ↔ Flask App ↔ Pokemon Components ↔ Pokemon Data
    
    - Web demo bypasses MCP protocol
    - Direct API calls to components
    - Visual interface for testing
    - NOT how production MCP works
    
    KEY DIFFERENCES:
    ✅ MCP: Standardized protocol for LLM integration
    ❌ Web: Custom interface for human testing
    
    ✅ MCP: Stdin/stdout communication
    ❌ Web: HTTP requests/responses
    
    ✅ MCP: Designed for AI consumption
    ❌ Web: Designed for human interaction
    """)

async def main():
    """Run the MCP demonstration"""
    print("🎮 Pokemon MCP Server - LLM Integration Demo")
    print("Testing how AI models would interact with the server")
    
    await demonstrate_llm_queries()
    await test_direct_components() 
    explain_mcp_architecture()
    
    print("\n" + "=" * 60)
    print("✅ Demo completed!")
    print("💡 To test with real LLM:")
    print("   1. Run: python run_server.py")
    print("   2. Configure LLM client to connect to MCP server")
    print("   3. LLM can now access Pokemon data and battle simulation")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())