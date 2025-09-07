# src/pokemon_mcp/data/pokemon_client.py
import httpx
import json
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class PokemonStats:
    hp: int
    attack: int
    defense: int
    special_attack: int
    special_defense: int
    speed: int

@dataclass
class Pokemon:
    id: int
    name: str
    types: List[str]
    stats: PokemonStats
    abilities: List[str]
    moves: List[str]
    height: int = 0
    weight: int = 0
    base_experience: int = 0
    sprite_url: str = ""
    species_url: str = ""

class PokemonClient:
    def __init__(self):
        self.base_url = "https://pokeapi.co/api/v2"
        self.client = httpx.AsyncClient(timeout=10.0)
        
    async def get_pokemon(self, name_or_id: str) -> Optional[Pokemon]:
        """Fetch Pokemon data from PokéAPI"""
        try:
            url = f"{self.base_url}/pokemon/{name_or_id.lower()}"
            response = await self.client.get(url)
            
            if response.status_code != 200:
                return None
                
            data = response.json()
            
            # Extract stats
            stats_data = {stat['stat']['name']: stat['base_stat'] for stat in data['stats']}
            stats = PokemonStats(
                hp=stats_data['hp'],
                attack=stats_data['attack'],
                defense=stats_data['defense'],
                special_attack=stats_data['special-attack'],
                special_defense=stats_data['special-defense'],
                speed=stats_data['speed']
            )
            
            # Extract types
            types = [t['type']['name'] for t in data['types']]
            
            # Extract abilities
            abilities = [a['ability']['name'] for a in data['abilities']]
            
            # Extract moves (limited for performance)
            moves = [m['move']['name'] for m in data['moves'][:20]]
            
            # Get sprite URL
            sprite_url = data['sprites']['front_default'] or ""
            
            return Pokemon(
                id=data['id'],
                name=data['name'],
                types=types,
                stats=stats,
                abilities=abilities,
                moves=moves,
                height=data['height'],
                weight=data['weight'],
                base_experience=data.get('base_experience', 0),
                sprite_url=sprite_url,
                species_url=data['species']['url']
            )
            
        except Exception as e:
            print(f"Error fetching Pokemon {name_or_id}: {e}")
            return None
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
