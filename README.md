# Pokémon Battle MCP Server
**Technical Assessment - Model Context Protocol Implementation**

A comprehensive Model Context Protocol (MCP) server that provides AI models with access to Pokémon data and advanced battle simulation capabilities. This server bridges the gap between AI systems and the Pokémon world, enabling LLMs to understand and interact with Pokémon data through standardized MCP interfaces.

## 🎯 Project Overview

This MCP server implements two core functionalities as specified in the technical assessment:

1. **Pokémon Data Resource** - Comprehensive access to Pokémon information
2. **Battle Simulation Tool** - Advanced Pokémon battle mechanics with status effects

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation
```bash
# Clone the repository
git clone <repository-url>
cd pokemon-mcp-server

# Install dependencies
pip install -r requirements.txt
```

### Running the MCP Server
```bash
python run_server.py
```

The server will start and display:
```
🎮 Pokemon Battle MCP Server ready for connections
📡 Listening on stdio for MCP client connections...
```

**Important**: This is normal MCP server behavior! The server communicates via stdin/stdout and waits for MCP client connections.

### Testing Components (Optional)
```bash
python test_components.py
```

### Demo Web Interface (Development Only)
```bash
python simple_web_demo.py
```
Access at: http://localhost:5000

## 📋 Assignment Deliverables

### Part 1: Pokémon Data Resource ✅

**Requirement**: Design and implement an MCP resource that connects to public Pokémon datasets

**Implementation**:
- **Resource URI**: `pokemon://data`
- **Data Source**: PokeAPI (https://pokeapi.co)
- **Comprehensive Data Exposed**:
  - ✅ Base stats (HP, Attack, Defense, Special Attack, Special Defense, Speed)
  - ✅ Types (Fire, Water, Grass, Electric, etc.)
  - ✅ Abilities and their effects
  - ✅ Available moves and move data  
  - ✅ Evolution information and chains
  - ✅ Physical characteristics (height, weight)
  - ✅ Sprites and images

**MCP Resource Design Patterns**:
- Follows MCP resource specification
- JSON-structured data responses
- Comprehensive metadata and usage examples
- Error handling and validation

### Part 2: Battle Simulation Tool ✅

**Requirement**: Design and implement an MCP tool for Pokémon battles

**Implementation**:
- **Tool Name**: `simulate_battle`
- **Core Battle Mechanics**:
  - ✅ Type effectiveness calculations (18 types, full chart)
  - ✅ Damage calculations based on stats and move power
  - ✅ Turn order determination based on Speed stats  
  - ✅ Status effects implementation (Burn, Poison, Paralysis, Sleep, Freeze)
  - ✅ STAB (Same Type Attack Bonus)
  - ✅ Critical hit mechanics
  - ✅ Move accuracy and PP system

**Advanced Features**:
- Detailed turn-by-turn battle logging
- Winner determination based on HP depletion
- Comprehensive battle reports with statistics
- Support for 1000+ Pokémon

## 🛠 MCP Tools & Resources

### Available MCP Resources

#### 1. `pokemon://data`
Comprehensive Pokémon database resource
- **Purpose**: Exposes all Pokémon data to LLMs
- **Data**: Stats, types, abilities, moves, evolution chains
- **Format**: JSON-structured responses

#### 2. `pokemon://types`  
Type effectiveness reference
- **Purpose**: Battle calculation reference
- **Data**: Complete type effectiveness chart
- **Usage**: Automatic integration in battles

### Available MCP Tools

#### 1. `get_pokemon`
**Purpose**: Fetch detailed Pokémon information
**Parameters**:
- `name_or_id` (string): Pokémon name or ID

**LLM Query Examples**:
```json
{
  "name": "get_pokemon",
  "arguments": {"name_or_id": "pikachu"}
}
```

#### 2. `simulate_battle`
**Purpose**: Simulate comprehensive Pokémon battles
**Parameters**:
- `pokemon1` (string): First Pokémon name/ID
- `pokemon2` (string): Second Pokémon name/ID

**LLM Query Examples**:
```json
{
  "name": "simulate_battle", 
  "arguments": {"pokemon1": "charizard", "pokemon2": "blastoise"}
}
```

#### 3. `get_evolution_chain`
**Purpose**: Retrieve complete evolution information
**Parameters**:
- `pokemon_name` (string): Pokémon to get evolution chain for

## 🤖 LLM Integration Examples

### How an LLM Would Query Resources

**Example 1: Basic Pokémon Data Query**
```
LLM Request: "Tell me about Pikachu's stats"
MCP Call: get_pokemon("pikachu")
Response: Complete JSON with stats, types, abilities, moves
```

**Example 2: Battle Analysis**
```  
LLM Request: "Who would win between Charizard and Blastoise?"
MCP Call: simulate_battle("charizard", "blastoise")
Response: Detailed battle simulation with turn-by-turn log
```

**Example 3: Evolution Information**
```
LLM Request: "What's Bulbasaur's evolution line?"
MCP Call: get_evolution_chain("bulbasaur")  
Response: Complete evolution chain with requirements
```

### Resource Data Exposure Documentation

**How the Resource Exposes Pokémon Data**:

1. **Structured JSON Format**: All data returned in consistent JSON structure
2. **Comprehensive Coverage**: 1000+ Pokémon with complete stat sets
3. **Real-time API Integration**: Live data from PokeAPI
4. **Caching System**: Efficient data retrieval and storage
5. **Error Handling**: Graceful handling of invalid requests
6. **Type Safety**: Validated data structures with proper typing

**Data Structure Example**:
```json
{
  "basic_info": {
    "id": 25,
    "name": "pikachu", 
    "height": "0.4m",
    "weight": "6.0kg"
  },
  "types": ["electric"],
  "stats": {
    "hp": 35,
    "attack": 55,
    "defense": 40,
    "total": 320
  },
  "abilities": ["Static", "Lightning Rod"],
  "evolution": {
    "evolution_chain": [...],
    "total_stages": 2
  }
}
```

## 🎮 Battle Mechanics Implementation

### Type Effectiveness System
- Complete 18-type system implemented
- Accurate multipliers (0x, 0.5x, 1x, 2x damage)
- Multi-type Pokémon support

### Status Effects (3+ Required)
1. **Burn** - Reduces attack, causes HP damage
2. **Poison** - Causes HP damage each turn
3. **Paralysis** - May prevent attacks, reduces speed
4. **Sleep** - Prevents attacks for 1-3 turns  
5. **Freeze** - May prevent attacks until thawed

### Advanced Battle Features
- Move PP (Power Points) system
- Critical hit calculations (6.25% base chance)
- STAB bonus for same-type moves
- Speed-based turn order with tie-breaking
- Comprehensive damage formula implementation

## 🏗 Architecture

```
src/pokemon_mcp/
├── server.py              # Main MCP server implementation
├── data/
│   ├── pokemon_client.py  # PokeAPI integration & caching
│   └── cache.py          # Data caching system
├── battle/
│   ├── engine.py         # Battle simulation engine  
│   ├── mechanics.py      # Type effectiveness & damage
│   ├── moves.py          # Move system & effects
│   └── status.py         # Status effect management
└── config.py             # Server configuration
```

## 🧪 Testing & Validation

### Component Testing
```bash
python test_components.py
```
Tests individual components:
- ✅ Pokémon data fetching
- ✅ Battle engine functionality  
- ✅ MCP server imports
- ✅ API connectivity

### MCP Client Testing  
```bash
python test_mcp_client.py
```
Tests MCP protocol integration:
- ✅ Resource listing and reading
- ✅ Tool execution
- ✅ Error handling

## 📝 Technical Specifications

### Dependencies
- `mcp>=1.0.0` - Model Context Protocol implementation
- `httpx>=0.27.0` - Async HTTP client for API calls
- `pydantic>=2.5.0` - Data validation and serialization
- `typing-extensions>=4.8.0` - Enhanced type hints

### Performance Features
- Async/await architecture for concurrent operations
- HTTP connection pooling and timeouts
- Intelligent caching system
- Rate limiting and retry logic
- Memory-efficient data structures

### Error Handling
- Graceful API failure handling
- Invalid Pokémon name detection
- Network timeout management  
- Comprehensive logging system

## 🔧 Configuration

Environment variables (optional):
```bash
POKEAPI_BASE_URL=https://pokeapi.co/api/v2
REQUEST_TIMEOUT=30
MAX_RETRIES=3  
CACHE_DURATION=3600
```

## 📖 Usage Notes

### Understanding MCP
This is an **MCP Server**, not a standalone application:
- Communicates via stdin/stdout with MCP clients
- Designed for LLM integration (Claude, GPT, etc.)
- The web demo is for development/testing only
- Production usage requires an MCP-compatible client

### LLM Integration
To use with an LLM:
1. Start the MCP server: `python run_server.py`
2. Configure your LLM client to connect to the MCP server
3. LLM can now access Pokémon data and battle simulation

### No Hardcoded Data
- All Pokémon data sourced from live PokeAPI
- No embedded datasets or hardcoded values
- Real-time data fetching with caching
- Supports all existing and future Pokémon

## 🎯 Assignment Completion Status

- ✅ **Part 1**: Pokémon Data Resource implemented
- ✅ **Part 2**: Battle Simulation Tool implemented  
- ✅ **MCP Protocol**: Full MCP server specification compliance
- ✅ **Battle Mechanics**: Type effectiveness, damage calculation, turn order
- ✅ **Status Effects**: 5 status effects implemented (exceeds 3 minimum)
- ✅ **Documentation**: Comprehensive usage and integration docs
- ✅ **Testing**: Component and integration tests included
- ✅ **Project Structure**: Clean, maintainable codebase
- ✅ **LLM Examples**: Clear integration examples provided

## 🤝 Support

For issues or questions about this MCP server implementation, please check:
1. Component tests: `python test_components.py`
2. Server logs when running `python run_server.py`
3. Web demo for functionality verification: `python simple_web_demo.py`

---

**Ready for LLM Integration** 🚀  
This MCP server is production-ready and follows all MCP protocol specifications for seamless AI model integration.