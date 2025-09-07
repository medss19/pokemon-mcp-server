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
        self.client = httpx.AsyncClient(timeout=30.0)  # Increased timeout
        self._cache = {}  # Simple cache to avoid repeated API calls
        
    async def get_pokemon(self, name_or_id: str) -> Optional[Pokemon]:
        """Fetch Pokemon data from PokéAPI with caching"""
        cache_key = str(name_or_id).lower()
        if cache_key in self._cache:
            return self._cache[cache_key]
            
        try:
            url = f"{self.base_url}/pokemon/{name_or_id.lower()}"
            response = await self.client.get(url)
            
            if response.status_code != 200:
                print(f"API Error: {response.status_code} for {name_or_id}")
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
            abilities = [a['ability']['name'].replace('-', ' ').title() for a in data['abilities']]
            
            # Extract moves (get more moves for better battle variety)
            moves = [m['move']['name'] for m in data['moves'][:50]]  # Increased from 20
            
            # Get sprite URL
            sprite_url = data['sprites']['front_default'] or ""
            
            pokemon = Pokemon(
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
            
            # Cache the result
            self._cache[cache_key] = pokemon
            return pokemon
            
        except Exception as e:
            print(f"Error fetching Pokemon {name_or_id}: {e}")
            return None
    
    async def get_evolution_chain(self, species_url: str) -> Dict:
        """Fetch evolution chain information"""
        try:
            # Get species data first
            species_response = await self.client.get(species_url)
            if species_response.status_code != 200:
                return {"error": "Species data not found"}
                
            species_data = species_response.json()
            evolution_chain_url = species_data['evolution_chain']['url']
            
            # Get evolution chain data
            evolution_response = await self.client.get(evolution_chain_url)
            if evolution_response.status_code != 200:
                return {"error": "Evolution chain data not found"}
                
            evolution_data = evolution_response.json()
            
            # Parse evolution chain
            chain = []
            current = evolution_data['chain']
            
            # Add base form
            chain.append({
                "name": current['species']['name'],
                "is_baby": current.get('is_baby', False)
            })
            
            # Add evolutions
            while current['evolves_to']:
                current = current['evolves_to'][0]  # Take first evolution path
                evolution_details = current.get('evolution_details', [{}])[0]
                
                chain.append({
                    "name": current['species']['name'],
                    "trigger": evolution_details.get('trigger', {}).get('name', 'unknown'),
                    "min_level": evolution_details.get('min_level'),
                    "item": evolution_details.get('item', {}).get('name') if evolution_details.get('item') else None,
                    "held_item": evolution_details.get('held_item', {}).get('name') if evolution_details.get('held_item') else None
                })
            
            return {
                "evolution_chain": chain,
                "total_stages": len(chain),
                "species_name": species_data['name'],
                "genus": species_data.get('genera', [{}])[0].get('genus', 'Unknown Pokemon'),
                "habitat": species_data.get('habitat', {}).get('name') if species_data.get('habitat') else None
            }
            
        except Exception as e:
            print(f"Error fetching evolution chain: {e}")
            return {"error": f"Failed to fetch evolution data: {str(e)}"}
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()