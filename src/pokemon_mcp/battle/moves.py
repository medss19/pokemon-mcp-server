# src/pokemon_mcp/battle/moves.py
import httpx
from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum

class StatusEffect(Enum):
    BURN = "burn"
    POISON = "poison"
    PARALYSIS = "paralysis"
    SLEEP = "sleep"
    FREEZE = "freeze"

class MoveCategory(Enum):
    PHYSICAL = "physical"
    SPECIAL = "special"
    STATUS = "status"

@dataclass
class Move:
    name: str
    type: str
    category: MoveCategory
    power: int
    accuracy: int
    pp: int
    status_effect: Optional[StatusEffect] = None
    status_chance: float = 0.0
    priority: int = 0
    description: str = ""

class MoveClient:
    def __init__(self):
        self.base_url = "https://pokeapi.co/api/v2"
        self.client = httpx.Client(timeout=10.0)
        self._move_cache = {}
    
    async def get_move(self, move_name: str) -> Move:
        """Fetch move data from PokéAPI"""
        if move_name in self._move_cache:
            return self._move_cache[move_name]
        
        try:
            url = f"{self.base_url}/move/{move_name.lower().replace(' ', '-')}"
            response = self.client.get(url)
            
            if response.status_code != 200:
                return self._create_default_move(move_name)
            
            data = response.json()
            
            # Parse move data
            move = Move(
                name=data['name'],
                type=data['type']['name'],
                category=MoveCategory(data['damage_class']['name']),
                power=data['power'] or 0,
                accuracy=data['accuracy'] or 100,
                pp=data['pp'] or 10,
                priority=data['priority'],
                description=self._get_move_description(data)
            )
            
            # Check for status effects
            status_effect, chance = self._parse_status_effects(data)
            if status_effect:
                move.status_effect = status_effect
                move.status_chance = chance
            
            self._move_cache[move_name] = move
            return move
            
        except Exception as e:
            print(f"Error fetching move {move_name}: {e}")
            return self._create_default_move(move_name)
    
    def _create_default_move(self, move_name: str) -> Move:
        """Create a default tackle-like move"""
        return Move(
            name=move_name,
            type="normal",
            category=MoveCategory.PHYSICAL,
            power=40,
            accuracy=100,
            pp=35,
            description="A basic physical attack"
        )
    
    def _get_move_description(self, data: dict) -> str:
        """Extract move description from API data"""
        for entry in data.get('flavor_text_entries', []):
            if entry['language']['name'] == 'en':
                return entry['flavor_text'].replace('\n', ' ').replace('\f', ' ')
        return "No description available"
    
    def _parse_status_effects(self, data: dict) -> tuple[Optional[StatusEffect], float]:
        """Parse status effects from move data"""
        effect_chance = data.get('effect_chance', 0)
        
        # Map common status-inducing moves
        status_keywords = {
            'burn': StatusEffect.BURN,
            'poison': StatusEffect.POISON,
            'paralyze': StatusEffect.PARALYSIS,
            'sleep': StatusEffect.SLEEP,
            'freeze': StatusEffect.FREEZE
        }
        
        effect_text = data.get('effect_entries', [{}])[0].get('effect', '').lower()
        
        for keyword, status in status_keywords.items():
            if keyword in effect_text:
                return status, effect_chance / 100.0
        
        return None, 0.0

async def get_pokemon_moves(pokemon_moves: List[str]) -> List[Move]:
    """Convert Pokemon move names to Move objects using API"""
    client = MoveClient()
    moves = []
    
    for move_name in pokemon_moves[:4]:  # Limit to 4 moves
        move = await client.get_move(move_name)
        moves.append(move)
    
    return moves