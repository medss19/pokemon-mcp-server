# src/pokemon_mcp/data/evolution.py
import httpx
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from enum import Enum

class EvolutionTrigger(Enum):
    LEVEL_UP = "level-up"
    TRADE = "trade"
    USE_ITEM = "use-item"
    SHED = "shed"
    SPIN = "spin"
    TOWER_OF_DARKNESS = "tower-of-darkness"
    TOWER_OF_WATERS = "tower-of-waters"
    THREE_CRITICAL_HITS = "three-critical-hits"
    TAKE_DAMAGE = "take-damage"

@dataclass
class EvolutionCondition:
    trigger: EvolutionTrigger
    min_level: Optional[int] = None
    item: Optional[str] = None
    held_item: Optional[str] = None
    known_move: Optional[str] = None
    known_move_type: Optional[str] = None
    location: Optional[str] = None
    min_happiness: Optional[int] = None
    min_beauty: Optional[int] = None
    min_affection: Optional[int] = None
    time_of_day: Optional[str] = None
    gender: Optional[str] = None
    relative_physical_stats: Optional[int] = None
    party_species: Optional[str] = None
    party_type: Optional[str] = None
    trade_species: Optional[str] = None
    needs_overworld_rain: bool = False
    turn_upside_down: bool = False

@dataclass
class EvolutionLink:
    species: str
    conditions: List[EvolutionCondition]
    is_baby: bool = False

@dataclass
class EvolutionChain:
    id: int
    baby_trigger_item: Optional[str] = None
    chain: List[EvolutionLink] = None

class EvolutionClient:
    def __init__(self):
        self.base_url = "https://pokeapi.co/api/v2"
        self.client = httpx.Client(timeout=10.0)
        self._evolution_cache = {}
        self._species_cache = {}
    
    async def get_pokemon_evolution_chain(self, pokemon_name: str) -> Optional[EvolutionChain]:
        """Get complete evolution chain for a Pokemon"""
        try:
            # First get the species data
            species_url = f"{self.base_url}/pokemon-species/{pokemon_name.lower()}"
            species_response = self.client.get(species_url)
            
            if species_response.status_code != 200:
                return None
            
            species_data = species_response.json()
            evolution_chain_url = species_data['evolution_chain']['url']
            
            # Get evolution chain data
            if evolution_chain_url in self._evolution_cache:
                return self._evolution_cache[evolution_chain_url]
            
            evolution_response = self.client.get(evolution_chain_url)
            if evolution_response.status_code != 200:
                return None
            
            evolution_data = evolution_response.json()
            chain = self._parse_evolution_chain(evolution_data)
            
            self._evolution_cache[evolution_chain_url] = chain
            return chain
            
        except Exception as e:
            print(f"Error fetching evolution chain for {pokemon_name}: {e}")
            return None
    
    def _parse_evolution_chain(self, data: Dict[str, Any]) -> EvolutionChain:
        """Parse evolution chain data from API"""
        chain = EvolutionChain(
            id=data['id'],
            baby_trigger_item=data.get('baby_trigger_item', {}).get('name') if data.get('baby_trigger_item') else None,
            chain=[]
        )
        
        # Parse the nested chain structure
        current = data['chain']
        while current:
            # Parse current species
            species_name = current['species']['name']
            
            # Parse evolution conditions
            conditions = []
            for detail in current.get('evolution_details', []):
                condition = self._parse_evolution_detail(detail)
                if condition:
                    conditions.append(condition)
            
            link = EvolutionLink(
                species=species_name,
                conditions=conditions,
                is_baby=current.get('is_baby', False)
            )
            chain.chain.append(link)
            
            # Move to next evolution (take first if multiple branches)
            if current.get('evolves_to'):
                current = current['evolves_to'][0]
            else:
                current = None
        
        return chain
    
    def _parse_evolution_detail(self, detail: Dict[str, Any]) -> Optional[EvolutionCondition]:
        """Parse individual evolution condition"""
        try:
            trigger_name = detail.get('trigger', {}).get('name')
            if not trigger_name:
                return None
            
            trigger = EvolutionTrigger(trigger_name)
            
            return EvolutionCondition(
                trigger=trigger,
                min_level=detail.get('min_level'),
                item=detail.get('item', {}).get('name') if detail.get('item') else None,
                held_item=detail.get('held_item', {}).get('name') if detail.get('held_item') else None,
                known_move=detail.get('known_move', {}).get('name') if detail.get('known_move') else None,
                known_move_type=detail.get('known_move_type', {}).get('name') if detail.get('known_move_type') else None,
                location=detail.get('location', {}).get('name') if detail.get('location') else None,
                min_happiness=detail.get('min_happiness'),
                min_beauty=detail.get('min_beauty'),
                min_affection=detail.get('min_affection'),
                time_of_day=detail.get('time_of_day'),
                gender=detail.get('gender'),
                relative_physical_stats=detail.get('relative_physical_stats'),
                party_species=detail.get('party_species', {}).get('name') if detail.get('party_species') else None,
                party_type=detail.get('party_type', {}).get('name') if detail.get('party_type') else None,
                trade_species=detail.get('trade_species', {}).get('name') if detail.get('trade_species') else None,
                needs_overworld_rain=detail.get('needs_overworld_rain', False),
                turn_upside_down=detail.get('turn_upside_down', False)
            )
        except Exception as e:
            print(f"Error parsing evolution detail: {e}")
            return None
    
    async def can_evolve(self, pokemon_name: str, level: int = 50, 
                        happiness: int = 255, **kwargs) -> List[str]:
        """Check what a Pokemon can evolve into given conditions"""
        chain = await self.get_pokemon_evolution_chain(pokemon_name)
        if not chain:
            return []
        
        # Find current Pokemon in chain
        current_index = -1
        for i, link in enumerate(chain.chain):
            if link.species.lower() == pokemon_name.lower():
                current_index = i
                break
        
        if current_index == -1 or current_index >= len(chain.chain) - 1:
            return []  # Not found or already final evolution
        
        # Check next evolution requirements
        next_link = chain.chain[current_index + 1]
        possible_evolutions = []
        
        for condition in next_link.conditions:
            if self._check_evolution_condition(condition, level, happiness, **kwargs):
                possible_evolutions.append(next_link.species)
                break
        
        return possible_evolutions
    
    def _check_evolution_condition(self, condition: EvolutionCondition, 
                                  level: int, happiness: int, **kwargs) -> bool:
        """Check if evolution condition is met"""
        if condition.min_level and level < condition.min_level:
            return False
        
        if condition.min_happiness and happiness < condition.min_happiness:
            return False
        
        if condition.item and condition.item not in kwargs.get('items_used', []):
            return False
        
        if condition.held_item and condition.held_item != kwargs.get('held_item'):
            return False
        
        if condition.known_move and condition.known_move not in kwargs.get('known_moves', []):
            return False
        
        if condition.time_of_day and condition.time_of_day != kwargs.get('time_of_day', 'day'):
            return False
        
        if condition.gender and condition.gender != kwargs.get('gender'):
            return False
        
        if condition.location and condition.location != kwargs.get('location'):
            return False
        
        # Add more condition checks as needed
        
        return True
    
    async def get_evolution_tree(self, pokemon_name: str) -> Dict[str, Any]:
        """Get full evolution tree as a structured dictionary"""
        chain = await self.get_pokemon_evolution_chain(pokemon_name)
        if not chain:
            return {}
        
        tree = {
            "chain_id": chain.id,
            "baby_trigger_item": chain.baby_trigger_item,
            "evolutions": []
        }
        
        for i, link in enumerate(chain.chain):
            evolution_data = {
                "species": link.species,
                "is_baby": link.is_baby,
                "stage": i + 1,
                "conditions": []
            }
            
            for condition in link.conditions:
                condition_data = {
                    "trigger": condition.trigger.value,
                    "requirements": {}
                }
                
                # Add non-None requirements
                req_fields = [
                    'min_level', 'item', 'held_item', 'known_move', 'known_move_type',
                    'location', 'min_happiness', 'min_beauty', 'min_affection',
                    'time_of_day', 'gender', 'relative_physical_stats',
                    'party_species', 'party_type', 'trade_species'
                ]
                
                for field in req_fields:
                    value = getattr(condition, field)
                    if value is not None:
                        condition_data["requirements"][field] = value
                
                # Add boolean flags
                if condition.needs_overworld_rain:
                    condition_data["requirements"]["needs_overworld_rain"] = True
                if condition.turn_upside_down:
                    condition_data["requirements"]["turn_upside_down"] = True
                
                evolution_data["conditions"].append(condition_data)
            
            tree["evolutions"].append(evolution_data)
        
        return tree