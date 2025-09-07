# src/pokemon_mcp/data/mock_data.py
from .pokemon_client import Pokemon, PokemonStats

# Mock Pokemon data for testing when API is unavailable
MOCK_POKEMON = {
    "pikachu": Pokemon(
        id=25,
        name="pikachu",
        types=["electric"],
        stats=PokemonStats(hp=35, attack=55, defense=40, special_attack=50, special_defense=50, speed=90),
        abilities=["static", "lightning-rod"],
        moves=["tackle", "thunder-shock", "quick-attack", "double-team", "slam"]
    ),
    "charizard": Pokemon(
        id=6,
        name="charizard", 
        types=["fire", "flying"],
        stats=PokemonStats(hp=78, attack=84, defense=78, special_attack=109, special_defense=85, speed=100),
        abilities=["blaze", "solar-power"],
        moves=["scratch", "ember", "dragon-rage", "scary-face", "fire-fang"]
    ),
    "blastoise": Pokemon(
        id=9,
        name="blastoise",
        types=["water"],
        stats=PokemonStats(hp=79, attack=83, defense=100, special_attack=85, special_defense=105, speed=78),
        abilities=["torrent", "rain-dish"],
        moves=["tackle", "water-gun", "withdraw", "bubble", "bite"]
    ),
    "venusaur": Pokemon(
        id=3,
        name="venusaur",
        types=["grass", "poison"], 
        stats=PokemonStats(hp=80, attack=82, defense=83, special_attack=100, special_defense=100, speed=80),
        abilities=["overgrow", "chlorophyll"],
        moves=["tackle", "vine-whip", "poison-powder", "razor-leaf", "growth"]
    )
}

def get_mock_pokemon(name_or_id: str) -> Pokemon:
    """Get mock Pokemon data"""
    name = str(name_or_id).lower()
    
    # Handle numeric IDs
    id_to_name = {
        "25": "pikachu",
        "6": "charizard", 
        "9": "blastoise",
        "3": "venusaur"
    }
    
    if name in id_to_name:
        name = id_to_name[name]
    
    return MOCK_POKEMON.get(name)