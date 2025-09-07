# src/pokemon_mcp/server.py
import asyncio
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
from mcp.types import (
    Resource, 
    Tool, 
    TextContent, 
    ImageContent, 
    EmbeddedResource
)
from mcp.server.stdio import stdio_server
from .data.pokemon_client import PokemonClient
from .battle.engine import BattleEngine
import json

# Initialize our services
pokemon_client = PokemonClient()
battle_engine = BattleEngine()

# Create the MCP server
server = Server("pokemon-battle-server")

@server.list_resources()
async def list_resources() -> list[Resource]:
    """List available Pokemon data resources"""
    return [
        Resource(
            uri="pokemon://data",
            name="Pokemon Database",
            description="Access to comprehensive Pokemon data including stats, types, abilities, and moves",
            mimeType="application/json"
        )
    ]

@server.read_resource()
async def read_resource(uri: str) -> str:
    """Read Pokemon resource data"""
    if uri == "pokemon://data":
        return """
        Pokemon Data Resource
        
        This resource provides access to comprehensive Pokemon data from the PokeAPI.
        
        Available data includes:
        - Base stats (HP, Attack, Defense, Special Attack, Special Defense, Speed)
        - Types (Fire, Water, Grass, etc.)
        - Abilities
        - Available moves
        
        To query specific Pokemon data, use the get_pokemon tool with a Pokemon name or ID.
        
        Example usage:
        - get_pokemon("pikachu")
        - get_pokemon("25")  # Pikachu's ID
        """
    else:
        raise ValueError(f"Unknown resource: {uri}")

@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools"""
    return [
        Tool(
            name="get_pokemon",
            description="Get detailed information about a specific Pokemon",
            inputSchema={
                "type": "object",
                "properties": {
                    "name_or_id": {
                        "type": "string",
                        "description": "Pokemon name or ID number"
                    }
                },
                "required": ["name_or_id"]
            }
        ),
        Tool(
            name="simulate_battle",
            description="Simulate a battle between two Pokemon",
            inputSchema={
                "type": "object",
                "properties": {
                    "pokemon1": {
                        "type": "string",
                        "description": "Name or ID of the first Pokemon"
                    },
                    "pokemon2": {
                        "type": "string",
                        "description": "Name or ID of the second Pokemon"
                    }
                },
                "required": ["pokemon1", "pokemon2"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls"""
    
    if name == "get_pokemon":
        name_or_id = arguments.get("name_or_id")
        if not name_or_id:
            return [TextContent(type="text", text="Error: name_or_id is required")]
        
        pokemon = await pokemon_client.get_pokemon(name_or_id)
        if not pokemon:
            return [TextContent(type="text", text=f"Pokemon '{name_or_id}' not found")]
        
        # Format Pokemon data as JSON
        pokemon_data = {
            "id": pokemon.id,
            "name": pokemon.name,
            "types": pokemon.types,
            "stats": {
                "hp": pokemon.stats.hp,
                "attack": pokemon.stats.attack,
                "defense": pokemon.stats.defense,
                "special_attack": pokemon.stats.special_attack,
                "special_defense": pokemon.stats.special_defense,
                "speed": pokemon.stats.speed
            },
            "abilities": pokemon.abilities,
            "moves": pokemon.moves[:10]  # Limit to first 10 for MVP
        }
        
        return [TextContent(type="text", text=json.dumps(pokemon_data, indent=2))]
    
    elif name == "simulate_battle":
        pokemon1_name = arguments.get("pokemon1")
        pokemon2_name = arguments.get("pokemon2")
        
        if not pokemon1_name or not pokemon2_name:
            return [TextContent(type="text", text="Error: Both pokemon1 and pokemon2 are required")]
        
        # Fetch both Pokemon
        pokemon1 = await pokemon_client.get_pokemon(pokemon1_name)
        pokemon2 = await pokemon_client.get_pokemon(pokemon2_name)
        
        if not pokemon1:
            return [TextContent(type="text", text=f"Pokemon '{pokemon1_name}' not found")]
        if not pokemon2:
            return [TextContent(type="text", text=f"Pokemon '{pokemon2_name}' not found")]
        
        # Simulate the battle
        result = battle_engine.simulate_battle(pokemon1, pokemon2)
        
        # Format battle result
        battle_report = {
            "battle_summary": {
                "winner": result.winner,
                "loser": result.loser,
                "total_turns": result.total_turns
            },
            "participants": {
                "pokemon1": {
                    "name": pokemon1.name,
                    "types": pokemon1.types,
                    "stats": {
                        "hp": pokemon1.stats.hp,
                        "attack": pokemon1.stats.attack,
                        "defense": pokemon1.stats.defense,
                        "speed": pokemon1.stats.speed
                    }
                },
                "pokemon2": {
                    "name": pokemon2.name,
                    "types": pokemon2.types,
                    "stats": {
                        "hp": pokemon2.stats.hp,
                        "attack": pokemon2.stats.attack,
                        "defense": pokemon2.stats.defense,
                        "speed": pokemon2.stats.speed
                    }
                }
            },
            "battle_log": [{"turn": log.turn, "message": log.message} for log in result.logs]
        }
        
        return [TextContent(type="text", text=json.dumps(battle_report, indent=2))]
    
    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]

async def main():
    """Main server entry point"""
    async with stdio_server() as (read_stream, write_stream):
        print("Server ready for MCP connections via stdio", flush=True)
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="pokemon-battle-server",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())