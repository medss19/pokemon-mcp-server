# Pokemon MCP Server
Scopely AI intern assignment - A Model Context Protocol (MCP) server for Pokemon data and battle simulation.

## Overview
This MCP server provides access to Pokemon data and battle simulation capabilities through the Model Context Protocol. It integrates with the PokeAPI to fetch real Pokemon data and includes a battle engine for simulating fights between Pokemon.

## Features
- **Pokemon Data Access**: Fetch detailed Pokemon information including stats, types, abilities, and moves
- **Battle Simulation**: Simulate battles between any two Pokemon with detailed turn-by-turn logs
- **MCP Integration**: Full MCP server implementation with resources and tools

## Quick Start

### Installation
```bash
pip install -r requirements.txt
```

### Running the Server
```bash
python run_server.py
```

The server will start and display:
```
Starting Pokemon Battle MCP Server...
Server ready for MCP connections via stdio
```

**Note**: This is normal behavior! MCP servers run continuously and communicate through stdin/stdout. The server is waiting for MCP client connections.

### Testing Components
```bash
python test_components.py
```

## Available Tools

### 1. get_pokemon
Get detailed information about a specific Pokemon.

**Parameters:**
- `name_or_id` (string): Pokemon name or ID number

**Example:**
```json
{
  "name": "get_pokemon",
  "arguments": {
    "name_or_id": "pikachu"
  }
}
```

### 2. simulate_battle
Simulate a battle between two Pokemon.

**Parameters:**
- `pokemon1` (string): Name or ID of the first Pokemon
- `pokemon2` (string): Name or ID of the second Pokemon

**Example:**
```json
{
  "name": "simulate_battle",
  "arguments": {
    "pokemon1": "pikachu",
    "pokemon2": "charizard"
  }
}
```

## Resources

### pokemon://data
Access to comprehensive Pokemon data resource with information about available data and usage examples.

## Architecture

```
src/
├── pokemon_mcp/
│   ├── server.py          # Main MCP server implementation
│   ├── data/
│   │   ├── pokemon_client.py  # PokeAPI client
│   │   ├── cache.py          # Caching functionality
│   │   └── mock_data.py      # Mock data for testing
│   ├── battle/
│   │   ├── engine.py         # Battle simulation engine
│   │   └── mechanics.py      # Battle mechanics and calculations
│   └── resources/
│       └── pokemon_resource.py  # Resource management
```

## Development

### Running Tests
```bash
python test_components.py      # Test individual components
python test_mcp_client.py     # Test MCP server connectivity
```

### Key Components
- **PokemonClient**: Handles API communication with PokeAPI
- **BattleEngine**: Simulates Pokemon battles with turn-based combat
- **MCP Server**: Exposes functionality through Model Context Protocol

## Error Handling
The server includes comprehensive error handling for:
- Network connectivity issues
- Invalid Pokemon names/IDs
- API rate limiting
- Battle simulation errors

## Contributing
This is an assignment project. See the assignment requirements for development guidelines.