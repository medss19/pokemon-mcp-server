# Pokemon Battle MCP Server

A Model Context Protocol (MCP) server implementation that provides AI models with comprehensive access to Pokemon data and advanced battle simulation capabilities. This server enables Large Language Models to understand, analyze, and interact with Pokemon information through standardized MCP interfaces.

## Project Overview

This MCP server implements the core requirements for the Pokemon Battle Simulation technical assessment:

- **Pokemon Data Resource**: Complete access to Pokemon information including stats, types, abilities, moves, and evolution chains
- **Battle Simulation Tool**: Advanced Pokemon battle mechanics with type effectiveness, status effects, and detailed logging

The server acts as a bridge between AI systems and the Pokemon universe, allowing LLMs to perform complex Pokemon analysis, team building strategies, and battle predictions.

## Architecture

The project follows a clean, modular architecture:

```
src/pokemon_mcp/
├── server.py                 # Main MCP server implementation
├── data/
│   └── pokemon_client.py     # Pokemon data fetching and caching
├── battle/
│   ├── engine.py            # Battle simulation engine
│   ├── mechanics.py         # Type effectiveness and damage calculations  
│   ├── moves.py             # Move system and effects
│   └── status.py            # Status effect management
└── config.py                # Server configuration
```

**Code for the MCP server with the Pokémon data resource:**
- Primary location: `src/pokemon_mcp/server.py` (lines 15-85)
- Supporting data client: `src/pokemon_mcp/data/pokemon_client.py`
- This implements the MCP resources (`pokemon://data` and `pokemon://types`) and the `get_pokemon` tool

**Code for the battle simulation tool following MCP's tool specification:**
- Primary location: `src/pokemon_mcp/server.py` (lines 86-125) - the `simulate_battle` tool
- Battle engine: `src/pokemon_mcp/battle/engine.py`

## Key Features

### Pokemon Data Access
- Complete Pokemon dataset (1000+ Pokemon)
- Base stats, types, abilities, and moves
- Evolution chain information with requirements
- Physical characteristics and sprites
- Real-time data from PokeAPI with intelligent caching

### Battle Simulation
- Accurate type effectiveness calculations (18-type system)
- Comprehensive damage formulas based on official Pokemon mechanics
- Turn order determination using speed stats
- Status effects: Burn, Poison, Paralysis, Sleep, Freeze
- STAB (Same Type Attack Bonus) implementation
- Critical hit mechanics with proper probability
- Detailed turn-by-turn battle logging

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup Instructions

1. **Clone or extract the project**
   ```bash
   cd pokemon-mcp-server
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify installation**
   ```bash
   python test_components.py
   ```
   This will test core functionality and API connectivity.

## Running the Server

### Production Mode (MCP Communication)
```bash
python run_server.py
```

The server will display:
```
Starting Pokemon Battle MCP Server...
Pokemon Battle MCP Server ready for connections
Listening on stdio for MCP client connections...
```

**Important**: This is normal MCP behavior. The server communicates via stdin/stdout and waits for MCP client connections. It does not provide a web interface in production mode.

### Development Demo (Web Interface)
For testing and demonstration purposes, run:
```bash
python web_demo.py
```

Then visit: http://localhost:5000

1. **Pokemon Lookup**: Search any Pokemon by name or ID to view complete stats, types, abilities, and evolution chain
2. **Battle Simulation**: Enter two Pokemon names to simulate a detailed battle with comprehensive mechanics

This provides a web interface to test Pokemon lookup and battle simulation features. Note that this is for development only - real MCP servers communicate with LLMs through the MCP protocol.

## MCP Integration

### Available Resources

**pokemon://data**
- Comprehensive Pokemon database
- Includes stats, types, abilities, moves, evolution chains
- JSON-structured responses for LLM consumption

**pokemon://types**  
- Complete type effectiveness chart
- Battle calculation reference data

### Available Tools

**get_pokemon**
- Fetch detailed Pokemon information
- Input: Pokemon name or ID
- Output: Complete Pokemon data with evolution chain

**simulate_battle**
- Simulate comprehensive Pokemon battles
- Input: Two Pokemon names/IDs
- Output: Detailed battle results with turn-by-turn logs


## MCP Client Integration Video

*[This section will contain screenshots and/or video demonstration of MCP client integration]*

### Integration Steps
1. Start the MCP server: `python run_server.py`
2. Configure your MCP client to connect to the server
3. LLM can now access Pokemon data and battle simulation tools

*Video/screenshots demonstrating the integration process will be added here*


## Technical Implementation

### Data Source
- Primary data from PokeAPI (https://pokeapi.co)
- Real-time API integration with intelligent caching
- No hardcoded Pokemon data - supports all existing and future Pokemon

### Battle Mechanics
- Official Pokemon damage formula implementation
- Complete 18-type effectiveness system
- Status effects with proper duration and interaction rules
- Move accuracy and Power Point (PP) system
- Speed-based turn order with tie-breaking

### Performance Features
- Async/await architecture for concurrent operations
- HTTP connection pooling and timeout handling
- Memory-efficient caching system
- Graceful error handling and retry logic


## Troubleshooting

### Common Issues

**"Pokemon not found" errors**
- Check Pokemon name spelling
- Try using the Pokemon's ID number instead
- Verify internet connection for API access

**Battle simulation timeouts**
- Some battles may take longer due to API calls
- The system has built-in timeout protection

**Import errors**
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Verify Python version compatibility (3.8+)

## Project Structure Details

### Core MCP Implementation
- **server.py**: Main MCP server with resource and tool definitions
- **pokemon_client.py**: Pokemon data fetching with caching
- **battle/engine.py**: Complete battle simulation system

### Battle System
- **mechanics.py**: Type effectiveness and damage calculations
- **moves.py**: Move system with status effects
- **status.py**: Status effect management (Burn, Poison, etc.)

### Development Tools
- **web_demo.py**: Web interface for testing (development only)
- **test_components.py**: Component testing and validation
- **run_server.py**: Server startup script

### Dependencies

Core requirements:
- mcp >= 1.0.0 (Model Context Protocol)
- httpx >= 0.27.0 (Async HTTP client)
- pydantic >= 2.5.0 (Data validation)
- typing-extensions >= 4.8.0 (Type hints)
- anyio >= 4.0.0 (Async utilities)
- flask >= 2.3.0 (Development demo only)