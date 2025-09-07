# src/pokemon_mcp/battle/mechanics.py
import random
from typing import Dict

# Type effectiveness chart (simplified for MVP)
TYPE_EFFECTIVENESS = {
    "fire": {"grass": 2.0, "ice": 2.0, "bug": 2.0, "steel": 2.0, "water": 0.5, "fire": 0.5, "rock": 0.5, "dragon": 0.5},
    "water": {"fire": 2.0, "ground": 2.0, "rock": 2.0, "water": 0.5, "grass": 0.5, "dragon": 0.5},
    "grass": {"water": 2.0, "ground": 2.0, "rock": 2.0, "fire": 0.5, "grass": 0.5, "poison": 0.5, "flying": 0.5, "bug": 0.5, "dragon": 0.5, "steel": 0.5},
    "electric": {"water": 2.0, "flying": 2.0, "electric": 0.5, "grass": 0.5, "ground": 0.0, "dragon": 0.5},
    "psychic": {"fighting": 2.0, "poison": 2.0, "psychic": 0.5, "steel": 0.5, "dark": 0.0},
    "ice": {"grass": 2.0, "ground": 2.0, "flying": 2.0, "dragon": 2.0, "fire": 0.5, "water": 0.5, "ice": 0.5, "steel": 0.5},
    "dragon": {"dragon": 2.0, "steel": 0.5, "fairy": 0.0},
    "dark": {"psychic": 2.0, "ghost": 2.0, "fighting": 0.5, "dark": 0.5, "fairy": 0.5},
    "fairy": {"fighting": 2.0, "dragon": 2.0, "dark": 2.0, "fire": 0.5, "poison": 0.5, "steel": 0.5},
    "normal": {"rock": 0.5, "ghost": 0.0, "steel": 0.5},
    "fighting": {"normal": 2.0, "ice": 2.0, "rock": 2.0, "dark": 2.0, "steel": 2.0, "poison": 0.5, "flying": 0.5, "psychic": 0.5, "bug": 0.5, "fairy": 0.5, "ghost": 0.0},
    "poison": {"grass": 2.0, "fairy": 2.0, "poison": 0.5, "ground": 0.5, "rock": 0.5, "ghost": 0.5, "steel": 0.0},
    "ground": {"fire": 2.0, "electric": 2.0, "poison": 2.0, "rock": 2.0, "steel": 2.0, "grass": 0.5, "bug": 0.5, "flying": 0.0},
    "flying": {"electric": 0.5, "ice": 0.5, "rock": 0.5, "steel": 0.5, "grass": 2.0, "fighting": 2.0, "bug": 2.0},
    "bug": {"grass": 2.0, "psychic": 2.0, "dark": 2.0, "fire": 0.5, "fighting": 0.5, "poison": 0.5, "flying": 0.5, "ghost": 0.5, "steel": 0.5, "fairy": 0.5},
    "rock": {"fire": 2.0, "ice": 2.0, "flying": 2.0, "bug": 2.0, "fighting": 0.5, "ground": 0.5, "steel": 0.5},
    "ghost": {"psychic": 2.0, "ghost": 2.0, "dark": 0.5, "normal": 0.0},
    "steel": {"ice": 2.0, "rock": 2.0, "fairy": 2.0, "fire": 0.5, "water": 0.5, "electric": 0.5, "steel": 0.5}
}

def get_type_effectiveness(attack_type: str, defend_types: list) -> float:
    """Calculate type effectiveness multiplier"""
    multiplier = 1.0
    
    for defend_type in defend_types:
        if attack_type in TYPE_EFFECTIVENESS:
            if defend_type in TYPE_EFFECTIVENESS[attack_type]:
                multiplier *= TYPE_EFFECTIVENESS[attack_type][defend_type]
    
    return multiplier

def calculate_damage(attacker_attack: int, defender_defense: int, move_power: int = 50, type_effectiveness: float = 1.0) -> int:
    """Simplified damage calculation"""
    # Basic formula: ((Attack / Defense) * Move Power * Type Effectiveness) / 10
    base_damage = ((attacker_attack / defender_defense) * move_power * type_effectiveness) / 10
    return max(1, int(base_damage))  # Minimum 1 damage