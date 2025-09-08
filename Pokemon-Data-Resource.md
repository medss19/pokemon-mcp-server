# Pokemon Data Resource Documentation

## How the MCP Server Exposes Pokemon Data to LLMs

This document explains how the Pokemon MCP server makes comprehensive Pokemon data accessible to Large Language Models through the Model Context Protocol.

## Resource Architecture Overview

The Pokemon MCP server exposes Pokemon data through two primary mechanisms:

1. **MCP Resources** - Static data structures that LLMs can read
2. **MCP Tools** - Dynamic functions that LLMs can execute with parameters

## MCP Resources

### Resource 1: pokemon://data

This resource provides LLMs with comprehensive information about the Pokemon database structure and capabilities.

**Purpose**: Informs LLMs about available Pokemon data and how to access it

**Data Exposed**:
```json
{
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
  "data_source": "PokeAPI (https://pokeapi.co)",
  "total_pokemon": "1000+ Pokemon available"
}
```

### Resource 2: pokemon://types

This resource provides the complete type effectiveness system for battle calculations.

**Purpose**: Reference data for understanding Pokemon type interactions

**Data Structure**:
```json
{
  "description": "Type Effectiveness Chart",
  "type_chart": {
    "fire": {"grass": 2.0, "water": 0.5, "ice": 2.0},
    "water": {"fire": 2.0, "ground": 2.0, "grass": 0.5},
    "electric": {"water": 2.0, "flying": 2.0, "ground": 0.0}
  },
  "effectiveness_values": {
    "2.0": "Super effective (2x damage)",
    "1.0": "Normal effectiveness (1x damage)",
    "0.5": "Not very effective (0.5x damage)",
    "0.0": "No effect (0x damage)"
  }
}
```

## MCP Tools for Data Access

### Tool : get_pokemon

**Function**: Retrieve comprehensive Pokemon information

**Input Schema**:
```json
{
  "name_or_id": "string (required)"
}
```

**Data Structure Exposed**:
```json
{
  "basic_info": {
    "id": 25,
    "name": "pikachu",
    "height": "0.4m",
    "weight": "6.0kg",
    "base_experience": 112,
    "sprite_url": "https://raw.githubusercontent.com/PokeAPI/sprites/..."
  },
  "types": ["electric"],
  "stats": {
    "hp": 35,
    "attack": 55,
    "defense": 40,
    "special_attack": 50,
    "special_defense": 50,
    "speed": 90,
    "total": 320
  },
  "abilities": ["Static", "Lightning Rod"],
  "moves": {
    "sample_moves": ["thunder-shock", "quick-attack", "thunder-wave"],
    "total_available": 42
  },
  "evolution": {
    "evolution_chain": [
      {"name": "pichu", "trigger": "friendship"},
      {"name": "pikachu", "trigger": "thunder-stone"},
      {"name": "raichu"}
    ],
    "total_stages": 3
  }
}
```

## Data Exposure Methods

### 1. Structured JSON Responses

All Pokemon data is returned in consistent, hierarchical JSON structures that LLMs can easily parse and understand.

**Key Design Principles**:
- Consistent field naming across all responses
- Logical grouping of related information
- Complete data sets with no missing required fields
- Standardized data types for reliable processing

### 2. Real-time API Integration

The server maintains live connections to PokeAPI, ensuring LLMs always access current data.

**Implementation Details**:
- Async HTTP client for concurrent requests
- Intelligent caching to reduce API calls
- Error handling with graceful fallbacks
- Rate limiting compliance

### 3. Comprehensive Data Coverage

**Statistical Data**:
- All six base stats for battle calculations
- Stat totals for quick comparisons
- Physical characteristics (height/weight)

**Type System**:
- Primary and secondary types
- Complete type effectiveness relationships
- Battle interaction calculations

**Move Information**:
- Available move sets for each Pokemon
- Move categories (Physical/Special/Status)
- Power, accuracy, and PP values

**Evolution Data**:
- Complete evolution chains
- Evolution triggers and requirements
- Special evolution conditions

### 4. Caching and Performance

**Memory Caching**:
- Frequently accessed Pokemon data cached in memory
- Evolution chain data cached separately
- Configurable cache duration and size limits

**Request Optimization**:
- Batch processing for related data
- Connection pooling for API requests
- Timeout handling and retry logic

## Technical Implementation Details

### Data Validation and Type Safety

All Pokemon data undergoes validation through Pydantic models:

```python
@dataclass
class Pokemon:
    id: int
    name: str
    types: List[str]
    stats: PokemonStats
    abilities: List[str]
    moves: List[str]
```

### Error Handling

The system provides meaningful error responses when data cannot be retrieved:

```json
{
  "error": "Pokemon 'invalid-name' not found. Please check the spelling or try a different Pokemon name/ID."
}
```

### Async Architecture

All data fetching operations use async/await patterns:
- Non-blocking API requests
- Concurrent data processing
- Efficient resource utilization

## Data Flow Architecture

```
LLM Request → MCP Client → MCP Server → PokeAPI → Data Processing → Structured Response → LLM Analysis
```

1. **LLM Query**: Natural language request about Pokemon
2. **MCP Translation**: Client converts to appropriate tool calls
3. **Server Processing**: Validates input and coordinates data fetching
4. **API Integration**: Retrieves live data from PokeAPI
5. **Data Structuring**: Formats response for optimal LLM consumption
6. **LLM Processing**: Analyzes structured data to answer user query