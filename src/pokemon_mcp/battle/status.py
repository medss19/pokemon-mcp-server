# src/pokemon_mcp/battle/status.py
from dataclasses import dataclass
from typing import Optional, Tuple
import random
from .moves import StatusEffect

@dataclass
class StatusCondition:
    effect: StatusEffect
    duration: int
    damage_per_turn: int = 0

class StatusManager:
    """Manages status effects for Pokemon in battle"""
    
    @staticmethod
    def apply_status_damage(pokemon_name: str, current_hp: int, max_hp: int, status: Optional[StatusCondition]) -> Tuple[int, str]:
        """Apply status effect damage and return new HP and message"""
        if not status:
            return current_hp, ""
        
        message = ""
        if status.effect == StatusEffect.BURN:
            damage = max(1, max_hp // 16)  # 1/16 of max HP
            current_hp = max(0, current_hp - damage)
            message = f"{pokemon_name} is hurt by burn! ({damage} damage)"
            
        elif status.effect == StatusEffect.POISON:
            damage = max(1, max_hp // 8)   # 1/8 of max HP
            current_hp = max(0, current_hp - damage)
            message = f"{pokemon_name} is hurt by poison! ({damage} damage)"
            
        return current_hp, message
    
    @staticmethod
    def can_attack(pokemon_name: str, status: Optional[StatusCondition]) -> Tuple[bool, str]:
        """Check if Pokemon can attack based on status"""
        if not status:
            return True, ""
            
        if status.effect == StatusEffect.PARALYSIS:
            if random.random() < 0.25:  # 25% chance to be fully paralyzed
                return False, f"{pokemon_name} is paralyzed and can't move!"
                
        elif status.effect == StatusEffect.SLEEP:
            if status.duration > 0:
                return False, f"{pokemon_name} is fast asleep!"
                
        elif status.effect == StatusEffect.FREEZE:
            if random.random() < 0.8:  # 80% chance to stay frozen
                return False, f"{pokemon_name} is frozen solid!"
        
        return True, ""
    
    @staticmethod
    def modify_damage(attacker_status: Optional[StatusCondition], damage: int) -> Tuple[int, str]:
        """Modify damage based on attacker's status"""
        if not attacker_status:
            return damage, ""
            
        modifier_message = ""
        
        if attacker_status.effect == StatusEffect.BURN:
            # Burn halves physical attack damage
            damage = damage // 2
            modifier_message = "Attack was weakened by burn!"
            
        elif attacker_status.effect == StatusEffect.PARALYSIS:
            # Paralysis reduces speed and may reduce damage slightly
            if random.random() < 0.1:  # 10% chance for reduced power
                damage = int(damage * 0.75)
                modifier_message = "Attack was weakened by paralysis!"
        
        return damage, modifier_message
    
    @staticmethod
    def tick_status(status: Optional[StatusCondition]) -> Optional[StatusCondition]:
        """Reduce status duration and return updated status"""
        if not status:
            return None
            
        if status.duration > 0:
            status.duration -= 1
            if status.duration <= 0:
                return None  # Status effect ended
                
        return status
    
    @staticmethod
    def get_status_message(pokemon_name: str, old_status: Optional[StatusCondition], new_status: Optional[StatusCondition]) -> str:
        """Get message about status changes"""
        if old_status and not new_status:
            effect_name = old_status.effect.value
            return f"{pokemon_name} recovered from {effect_name}!"
            
        if new_status and not old_status:
            effect_name = new_status.effect.value
            return f"{pokemon_name} was {effect_name}ed!"
            
        return ""
    
    @staticmethod
    def create_status(effect: StatusEffect) -> StatusCondition:
        """Create a new status condition with appropriate duration"""
        duration_map = {
            StatusEffect.BURN: -1,      # Lasts until healed
            StatusEffect.POISON: -1,    # Lasts until healed
            StatusEffect.PARALYSIS: -1, # Lasts until healed
            StatusEffect.SLEEP: random.randint(1, 3),  # 1-3 turns
            StatusEffect.FREEZE: -1,    # Lasts until healed or fire attack
        }
        
        damage_map = {
            StatusEffect.BURN: 1,
            StatusEffect.POISON: 1,
            StatusEffect.PARALYSIS: 0,
            StatusEffect.SLEEP: 0,
            StatusEffect.FREEZE: 0,
        }
        
        return StatusCondition(
            effect=effect,
            duration=duration_map[effect],
            damage_per_turn=damage_map[effect]
        )