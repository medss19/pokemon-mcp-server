# LLM Query Examples and Usage Patterns

## How Large Language Models Query the Pokemon MCP Server

This document provides comprehensive examples of how LLMs interact with the Pokemon MCP server, including query patterns, expected responses, and analysis capabilities.

## Query Pattern Categories

### 1. Individual Pokemon Analysis

#### Query: "Tell me about Pikachu's stats and abilities"

**MCP Tool Execution**:
```json
{
  "tool": "get_pokemon",
  "arguments": {
    "name_or_id": "pikachu"
  }
}
```

**Server Response**:
```json
{
  "basic_info": {
    "id": 25,
    "name": "pikachu",
    "height": "0.4m",
    "weight": "6.0kg",
    "base_experience": 112,
    "sprite_url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/25.png"
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
  }
}
```

**LLM Analysis Output**:
"Pikachu is an Electric-type Pokemon with moderate stats. Its standout feature is its 90 speed, making it faster than many Pokemon. With abilities like Static and Lightning Rod, it can capitalize on Electric-type moves while having some defensive utility. Its total stat of 320 indicates it's likely an early-game Pokemon that evolves into something stronger."

### 2. Comparative Analysis

#### Query: "Compare Charizard and Blastoise for competitive battling"

**MCP Tool Execution**:
```json
[
  {
    "tool": "get_pokemon",
    "arguments": {"name_or_id": "charizard"}
  },
  {
    "tool": "get_pokemon", 
    "arguments": {"name_or_id": "blastoise"}
  }
]
```

**LLM Analysis Process**:
1. Receives complete data for both Pokemon
2. Compares base stats across all categories
3. Analyzes type advantages/disadvantages
4. Considers ability synergies
5. Evaluates movepool options

**Expected LLM Response**:
"Charizard (Fire/Flying, 534 total stats) vs Blastoise (Water, 534 total stats):

**Charizard Advantages**:
- Higher Special Attack (109 vs 85) for powerful special moves
- Superior Speed (100 vs 78) for first-strike capability
- Flying type provides Ground immunity

**Blastoise Advantages**: 
- Better defensive stats (Defense 100 vs 78)
- Water typing resists Fire moves (major advantage over Charizard)
- More consistent bulk with higher HP

**Verdict**: Blastoise has the type advantage and better survivability, while Charizard offers higher offensive pressure and speed control."

### 3. Battle Prediction and Simulation

#### Query: "Who would win: Garchomp vs Dragonite?"

**MCP Tool Execution**:
```json
{
  "tool": "simulate_battle",
  "arguments": {
    "pokemon1": "garchomp",
    "pokemon2": "dragonite"
  }
}
```

**Server Response**:
```json
{
  "battle_summary": {
    "winner": "garchomp",
    "loser": "dragonite",
    "total_turns": 12,
    "battle_type": "Advanced Pokemon Battle Simulation"
  },
  "participants": {
    "pokemon1": {
      "name": "garchomp",
      "types": ["dragon", "ground"],
      "stats": {"hp": 108, "attack": 130, "speed": 102}
    },
    "pokemon2": {
      "name": "dragonite",
      "types": ["dragon", "flying"],
      "stats": {"hp": 91, "attack": 134, "speed": 80}
    }
  },
  "detailed_log": [
    {"turn": 1, "message": "Battle begins! garchomp vs dragonite"},
    {"turn": 1, "message": "garchomp uses earthquake!"},
    {"turn": 1, "message": "It's super effective! Deals 85 damage!"},
    {"turn": 2, "message": "dragonite uses dragon claw!"},
    {"turn": 2, "message": "Deals 45 damage!"}
  ]
}
```

**LLM Analysis Output**:
"Based on the battle simulation, Garchomp defeated Dragonite in 12 turns. Key factors:

1. **Speed Advantage**: Garchomp's 102 speed vs Dragonite's 80 allowed consistent first strikes
2. **Type Effectiveness**: Garchomp's Ground-type moves (like Earthquake) are super effective against Dragonite's Flying type
3. **Defensive Typing**: Garchomp's Ground typing provides useful resistances

The battle log shows Garchomp consistently dealing higher damage due to type advantages, ultimately leading to victory."

### 4. Team Building and Strategy

#### Query: "Build a balanced team around Bulbasaur"

**LLM Query Process**:
1. Get Bulbasaur data for analysis
2. Identify type weaknesses (Fire, Flying, Ice, Psychic)
3. Query Pokemon that cover these weaknesses
4. Analyze evolution potential

**MCP Tool Calls**:
```json
[
  {
    "tool": "get_pokemon",
    "arguments": {"name_or_id": "bulbasaur"}
  },
  {
    "tool": "get_pokemon", 
    "arguments": {"name_or_id": "squirtle"}
  },
  {
    "tool": "get_pokemon",
    "arguments": {"name_or_id": "charmander"}
  }
]
```

**LLM Strategic Analysis**:
"Team building around Bulbasaur (Grass/Poison):

**Core Pokemon**: Bulbasaur → Ivysaur → Venusaur
- Strong against Water, Ground, Rock types
- Weak to Fire, Flying, Ice, Psychic

**Recommended Team Members**:
1. **Water-type** (Squirtle line): Covers Fire weakness
2. **Steel or Rock-type**: Resists Flying and Ice moves  
3. **Dark-type**: Handles Psychic threats
4. **Electric-type**: Coverage for Flying types
5. **Fighting-type**: General offensive pressure

**Strategy**: Use Bulbasaur's early-game utility (Sleep Powder, Poison effects) while building a defensive core that covers its main weaknesses."

### 5. Evolution Planning

#### Query: "When should I evolve my Pichu and what are the benefits?"

**MCP Tool Execution**:
```json
{
  "tool": "get_pokemon",
  "arguments": {"name_or_id": "pichu"}
}
```

**Evolution Data Analysis**:
```json
{
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

**LLM Strategic Response**:
"Pichu Evolution Strategy:

**Pichu → Pikachu (Friendship Evolution)**:
- Stat improvements across all categories
- Access to better movepool
- Timing: Evolve when friendship is maximized and you've learned desired moves

**Pikachu → Raichu (Thunder Stone)**:
- Significant stat boost, especially Special Attack and Speed
- Trade-off: May lose access to some Pikachu-only moves
- Timing: Evolve after learning key moves that Raichu can't learn naturally

**Recommendation**: Focus on friendship building for the first evolution, then use Thunder Stone strategically based on your movepool needs."

### 6. Type Coverage Analysis

#### Query: "What types resist Electric attacks and how should I handle them?"

**LLM Process**:
1. Reads pokemon://types resource
2. Analyzes type effectiveness chart
3. Identifies resistances and immunities

**Resource Query**:
```
Read resource: pokemon://types
```

**Type Chart Analysis**:
```json
{
  "electric": {
    "water": 2.0,
    "flying": 2.0,
    "electric": 0.5,
    "grass": 0.5,
    "ground": 0.0,
    "dragon": 0.5
  }
}
```

**LLM Strategic Response**:
"Electric-type move coverage analysis:

**Resists Electric (0.5x damage)**:
- Electric-types (self-resistance)
- Grass-types
- Dragon-types

**Immune to Electric (0x damage)**:
- Ground-types (complete immunity)

**Counter-strategies**:
1. **Ice-type moves** for Grass and Dragon resistors
2. **Water/Ice moves** for Ground-types  
3. **Hidden Power** for type coverage
4. **Focus on non-Electric STAB** when possible

**Team Recommendation**: Pair Electric-types with Pokemon that have Ice or Water coverage to handle resistant types."

### 7. Advanced Battle Mechanics

#### Query: "Explain how status effects work in Pokemon battles"

**LLM Process**:
1. Analyzes battle simulation logs for status effect examples
2. References battle engine mechanics
3. Provides comprehensive explanation

**Expected LLM Response**:
"Status effects in Pokemon battles (based on battle simulations):

**Burn**:
- Reduces Attack stat by 50%
- Deals 1/16 max HP damage each turn
- Affects physical moves primarily

**Poison**:
- Deals 1/8 max HP damage each turn
- No stat modifications
- Cumulative damage over time

**Paralysis**:
- 25% chance to prevent attacks each turn
- Reduces Speed stat significantly
- Can completely shut down fast Pokemon

**Sleep**:
- Prevents attacks for 1-3 turns
- No damage, but complete action prevention
- Turn count decreases automatically

**Freeze**:
- 80% chance to prevent attacks each turn
- 20% chance to thaw naturally
- Fire-type moves can thaw frozen Pokemon

**Strategic Usage**: Status effects are crucial for battle control, with Paralysis being excellent for speed control, Burn for physical attackers, and Sleep for setup opportunities."

## Advanced Query Patterns

### Multi-Pokemon Analysis

**Query**: "Compare the starter Pokemon from Generation 1 for a new player"

**Tool Execution Pattern**:
```json
[
  {"tool": "get_pokemon", "arguments": {"name_or_id": "bulbasaur"}},
  {"tool": "get_pokemon", "arguments": {"name_or_id": "charmander"}},
  {"tool": "get_pokemon", "arguments": {"name_or_id": "squirtle"}}
]
```

### Statistical Analysis

**Query**: "Which Pokemon has the highest speed stat among Electric types?"

**LLM Process**:
1. Query multiple Electric-type Pokemon
2. Compare speed statistics
3. Rank and provide analysis

### Battle Meta Analysis

**Query**: "What makes a Pokemon competitively viable?"

**LLM Analysis Framework**:
- Base stat totals and distributions
- Type combinations and coverage
- Ability synergies
- Available movepool quality
- Role in team compositions

## Error Handling Examples

### Invalid Pokemon Query

**Query**: "Tell me about Pokeman123"

**Server Response**:
```json
{
  "error": "Pokemon 'pokeman123' not found. Please check the spelling or try a different Pokemon name/ID."
}
```

**LLM Response**:
"I couldn't find a Pokemon named 'Pokeman123'. This might be due to a spelling error. Could you check the name and try again? You can also use the Pokemon's ID number if you know it."
