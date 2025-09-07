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
            description="Access to comprehensive Pokemon data including stats, types, abilities, moves, and evolution information",
            mimeType="application/json"
        ),
        Resource(
            uri="pokemon://types",
            name="Type Effectiveness Chart",
            description="Pokemon type effectiveness relationships for battle calculations",
            mimeType="application/json"
        )
    ]

@server.read_resource()
async def read_resource(uri: str) -> str:
    """Read Pokemon resource data"""
    if uri == "pokemon://data":
        return json.dumps({
            "description": "Pokemon Data Resource",
            "features": [
                "Base stats (HP, Attack, Defense, Special Attack, Special Defense, Speed)",
                "Types (Fire, Water, Grass, Electric, etc.)",
                "Abilities and their effects",
                "Available moves and move data",
                "Evolution chains and requirements",
                "Physical characteristics (height, weight)",
                "Base experience and sprites"
            ],
            "usage": {
                "tool": "get_pokemon",
                "description": "Use get_pokemon tool with Pokemon name or ID to fetch detailed data",
                "examples": [
                    "get_pokemon('pikachu')",
                    "get_pokemon('25')",
                    "get_pokemon('charizard')"
                ]
            },
            "data_source": "PokeAPI (https://pokeapi.co)",
            "total_pokemon": "1000+ Pokemon available"
        }, indent=2)
    
    elif uri == "pokemon://types":
        from .battle.mechanics import TYPE_EFFECTIVENESS
        return json.dumps({
            "description": "Type Effectiveness Chart",
            "type_chart": TYPE_EFFECTIVENESS,
            "effectiveness_values": {
                "2.0": "Super effective (2x damage)",
                "1.0": "Normal effectiveness (1x damage)", 
                "0.5": "Not very effective (0.5x damage)",
                "0.0": "No effect (0x damage)"
            },
            "usage": "Used automatically in battle simulations for damage calculations"
        }, indent=2)
    
    else:
        raise ValueError(f"Unknown resource: {uri}")

@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools"""
    return [
        Tool(
            name="get_pokemon",
            description="Get detailed information about a specific Pokemon including stats, types, abilities, moves, and evolution data",
            inputSchema={
                "type": "object",
                "properties": {
                    "name_or_id": {
                        "type": "string",
                        "description": "Pokemon name (e.g., 'pikachu') or ID number (e.g., '25')"
                    }
                },
                "required": ["name_or_id"]
            }
        ),
        Tool(
            name="simulate_battle",
            description="Simulate a comprehensive battle between two Pokemon with advanced mechanics including type effectiveness, status effects, and detailed turn-by-turn logging",
            inputSchema={
                "type": "object",
                "properties": {
                    "pokemon1": {
                        "type": "string",
                        "description": "Name or ID of the first Pokemon battler"
                    },
                    "pokemon2": {
                        "type": "string", 
                        "description": "Name or ID of the second Pokemon battler"
                    }
                },
                "required": ["pokemon1", "pokemon2"]
            }
        ),
        Tool(
            name="get_evolution_chain",
            description="Get the complete evolution chain for a Pokemon species",
            inputSchema={
                "type": "object",
                "properties": {
                    "pokemon_name": {
                        "type": "string",
                        "description": "Pokemon name to get evolution chain for"
                    }
                },
                "required": ["pokemon_name"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls"""
    
    if name == "get_pokemon":
        name_or_id = arguments.get("name_or_id")
        if not name_or_id:
            return [TextContent(type="text", text="Error: name_or_id parameter is required")]
        
        pokemon = await pokemon_client.get_pokemon(name_or_id)
        if not pokemon:
            return [TextContent(type="text", text=f"Pokemon '{name_or_id}' not found. Please check the spelling or try a different Pokemon name/ID.")]
        
        # Get evolution data
        evolution_data = await pokemon_client.get_evolution_chain(pokemon.species_url)
        
        # Format comprehensive Pokemon data
        pokemon_data = {
            "basic_info": {
                "id": pokemon.id,
                "name": pokemon.name,
                "height": f"{pokemon.height/10}m",
                "weight": f"{pokemon.weight/10}kg",
                "base_experience": pokemon.base_experience,
                "sprite_url": pokemon.sprite_url
            },
            "types": pokemon.types,
            "stats": {
                "hp": pokemon.stats.hp,
                "attack": pokemon.stats.attack, 
                "defense": pokemon.stats.defense,
                "special_attack": pokemon.stats.special_attack,
                "special_defense": pokemon.stats.special_defense,
                "speed": pokemon.stats.speed,
                "total": (pokemon.stats.hp + pokemon.stats.attack + pokemon.stats.defense + 
                         pokemon.stats.special_attack + pokemon.stats.special_defense + pokemon.stats.speed)
            },
            "abilities": pokemon.abilities,
            "moves": {
                "sample_moves": pokemon.moves[:15],  # Show more moves
                "total_available": len(pokemon.moves)
            },
            "evolution": evolution_data
        }
        
        return [TextContent(type="text", text=json.dumps(pokemon_data, indent=2))]
    
    elif name == "get_evolution_chain":
        pokemon_name = arguments.get("pokemon_name")
        if not pokemon_name:
            return [TextContent(type="text", text="Error: pokemon_name parameter is required")]
            
        pokemon = await pokemon_client.get_pokemon(pokemon_name)
        if not pokemon:
            return [TextContent(type="text", text=f"Pokemon '{pokemon_name}' not found")]
            
        evolution_data = await pokemon_client.get_evolution_chain(pokemon.species_url)
        return [TextContent(type="text", text=json.dumps(evolution_data, indent=2))]
    
    elif name == "simulate_battle":
        pokemon1_name = arguments.get("pokemon1")
        pokemon2_name = arguments.get("pokemon2")
        
        if not pokemon1_name or not pokemon2_name:
            return [TextContent(type="text", text="Error: Both pokemon1 and pokemon2 parameters are required")]
        
        # Fetch both Pokemon
        pokemon1 = await pokemon_client.get_pokemon(pokemon1_name)
        pokemon2 = await pokemon_client.get_pokemon(pokemon2_name)
        
        if not pokemon1:
            return [TextContent(type="text", text=f"Pokemon '{pokemon1_name}' not found. Please check the spelling or try a different Pokemon.")]
        if not pokemon2:
            return [TextContent(type="text", text=f"Pokemon '{pokemon2_name}' not found. Please check the spelling or try a different Pokemon.")]
        
        # Simulate the battle (NOW PROPERLY ASYNC)
        result = await battle_engine.simulate_battle(pokemon1, pokemon2)
        
        # Format comprehensive battle result
        battle_report = {
            "battle_summary": {
                "winner": result.winner,
                "loser": result.loser, 
                "total_turns": result.total_turns,
                "battle_type": "Advanced Pokemon Battle Simulation"
            },
            "participants": {
                "pokemon1": {
                    "name": pokemon1.name,
                    "types": pokemon1.types,
                    "stats": {
                        "hp": pokemon1.stats.hp,
                        "attack": pokemon1.stats.attack,
                        "defense": pokemon1.stats.defense,
                        "special_attack": pokemon1.stats.special_attack,
                        "special_defense": pokemon1.stats.special_defense,
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
                        "special_attack": pokemon2.stats.special_attack,
                        "special_defense": pokemon2.stats.special_defense,
                        "speed": pokemon2.stats.speed
                    }
                }
            },
            "mechanics_used": [
                "Type effectiveness calculations",
                "STAB (Same Type Attack Bonus)",
                "Critical hit chances",
                "Speed-based turn order",
                "Status effect applications",
                "Comprehensive damage formulas"
            ],
            "detailed_log": [{"turn": log.turn, "message": log.message} for log in result.logs]
        }
        
        return [TextContent(type="text", text=json.dumps(battle_report, indent=2))]
    
    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}. Available tools: get_pokemon, simulate_battle, get_evolution_chain")]

async def main():
    """Main server entry point"""
    async with stdio_server() as (read_stream, write_stream):
        print("🎮 Pokemon Battle MCP Server ready for connections", flush=True)
        print("📡 Listening on stdio for MCP client connections...", flush=True)
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