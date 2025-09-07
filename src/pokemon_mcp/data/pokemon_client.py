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
class EvolutionChain:
    species_name: str
    evolves_to: List[str]
    evolution_details: List[Dict]

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
    evolution_chain: Optional[EvolutionChain] = None

class PokemonClient:
    def __init__(self):
        self.base_url = "https://pokeapi.co/api/v2"
        self.client = httpx.AsyncClient(timeout=10.0)
        
    async def get_pokemon(self, name_or_id: str, include_evolution: bool = True) -> Optional[Pokemon]:
        """Fetch Pokemon data from PokéAPI with evolution support"""
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
            
            # Get evolution chain if requested
            evolution_chain = None
            if include_evolution:
                evolution_chain = await self._get_evolution_chain(data['species']['url'])
            
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
                evolution_chain=evolution_chain
            )
            
        except Exception as e:
            print(f"Error fetching Pokemon {name_or_id}: {e}")
            return None
    
    async def _get_evolution_chain(self, species_url: str) -> Optional[EvolutionChain]:
        """Get evolution chain for a Pokemon"""
        try:
            # Get species data first
            response = await self.client.get(species_url)
            if response.status_code != 200:
                return None
            
            species_data = response.json()
            evolution_chain_url = species_data['evolution_chain']['url']
            
            # Get evolution chain data
            response = await self.client.get(evolution_chain_url)
            if response.status_code != 200:
                return None
            
            evolution_data = response.json()
            chain = evolution_data['chain']
            
            # Parse evolution chain
            species_name = chain['species']['name']
            evolves_to = []
            evolution_details = []
            
            def parse_evolutions(chain_node):
                for evolution in chain_node.get('evolves_to', []):
                    evolves_to.append(evolution['species']['name'])
                    evolution_details.append(evolution.get('evolution_details', [{}])[0])
                    # Recursively parse further evolutions
                    parse_evolutions(evolution)
            
            parse_evolutions(chain)
            
            return EvolutionChain(
                species_name=species_name,
                evolves_to=evolves_to,
                evolution_details=evolution_details
            )
            
        except Exception as e:
            print(f"Error fetching evolution chain: {e}")
            return None
    
    async def get_evolution_line(self, name_or_id: str) -> List[Pokemon]:
        """Get all Pokemon in an evolution line"""
        try:
            # Get the base Pokemon first
            pokemon = await self.get_pokemon(name_or_id, include_evolution=True)
            if not pokemon or not pokemon.evolution_chain:
                return [pokemon] if pokemon else []
            
            evolution_line = []
            
            # Get the base species
            base_pokemon = await self.get_pokemon(pokemon.evolution_chain.species_name, include_evolution=False)
            if base_pokemon:
                evolution_line.append(base_pokemon)
            
            # Get all evolutions
            for evolution_name in pokemon.evolution_chain.evolves_to:
                evolved_pokemon = await self.get_pokemon(evolution_name, include_evolution=False)
                if evolved_pokemon:
                    evolution_line.append(evolved_pokemon)
            
            return evolution_line
            
        except Exception as e:
            print(f"Error fetching evolution line: {e}")
            return []
    
    async def close(self):
        await self.client.aclose()
