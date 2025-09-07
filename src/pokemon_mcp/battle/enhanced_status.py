# src/pokemon_mcp/battle/enhanced_status.py
from dataclasses import dataclass
from typing import Optional, Tuple, Dict, List
import random
from enum import Enum

class StatusEffect(Enum):
    BURN = "burn"
    POISON = "poison"
    BADLY_POISON = "badly_poison"
    PARALYSIS = "paralysis"
    SLEEP = "sleep"
    FREEZE = "freeze"
    CONFUSION = "confusion"
    FLINCH = "flinch"
    # Additional status conditions
    ATTRACT = "attract"
    CURSE = "curse"
    NIGHTMARE = "nightmare"
    PERISH_SONG = "perish_song"
    TORMENT = "torment"
    TAUNT = "taunt"
    ENCORE = "encore"
    DISABLE = "disable"

@dataclass
class StatusCondition:
    effect: StatusEffect
    duration: int  # -1 for permanent, 0+ for turns remaining
    severity: int = 1  # For badly poison progression
    source_pokemon: str = ""  # Who caused this status
    additional_data: Dict = None  # For complex status effects
    
    def __post_init__(self):
        if self.additional_data is None:
            self.additional_data = {}

class EnhancedStatusManager:
    """Enhanced status effect management with complex interactions"""
    
    @staticmethod
    def apply_status_damage(pokemon_name: str, current_hp: int, max_hp: int, 
                           status: Optional[StatusCondition], turn_number: int = 0) -> Tuple[int, str]:
        """Apply status effect damage with enhanced mechanics"""
        if not status:
            return current_hp, ""
        
        message = ""
        damage = 0
        
        if status.effect == StatusEffect.BURN:
            damage = max(1, max_hp // 16)  # 1/16 of max HP
            current_hp = max(0, current_hp - damage)
            message = f"{pokemon_name} is hurt by burn! ({damage} damage)"
            
        elif status.effect == StatusEffect.POISON:
            damage = max(1, max_hp // 8)   # 1/8 of max HP
            current_hp = max(0, current_hp - damage)
            message = f"{pokemon_name} is hurt by poison! ({damage} damage)"
            
        elif status.effect == StatusEffect.BADLY_POISON:
            # Badly poison damage increases each turn
            damage = max(1, (max_hp * status.severity) // 16)  # Increases with turns
            current_hp = max(0, current_hp - damage)
            message = f"{pokemon_name} is badly poisoned! ({damage} damage)"
            
        elif status.effect == StatusEffect.CURSE:
            # Curse does 1/4 max HP damage
            damage = max(1, max_hp // 4)
            current_hp = max(0, current_hp - damage)
            message = f"{pokemon_name} is hurt by the curse! ({damage} damage)"
            
        elif status.effect == StatusEffect.NIGHTMARE:
            # Nightmare only affects sleeping Pokemon
            if 'sleeping' in status.additional_data:
                damage = max(1, max_hp // 4)
                current_hp = max(0, current_hp - damage)
                message = f"{pokemon_name} is trapped in a nightmare! ({damage} damage)"
                
        return current_hp, message
    
    @staticmethod
    def can_attack(pokemon_name: str, status: Optional[StatusCondition], 
                   move_name: str = "", turn_data: Dict = None) -> Tuple[bool, str]:
        """Enhanced attack prevention check"""
        if not status:
            return True, ""
        
        if turn_data is None:
            turn_data = {}
            
        if status.effect == StatusEffect.PARALYSIS:
            if random.random() < 0.25:  # 25% chance to be fully paralyzed
                return False, f"{pokemon_name} is paralyzed and can't move!"
                
        elif status.effect == StatusEffect.SLEEP:
            if status.duration > 0:
                return False, f"{pokemon_name} is fast asleep!"
            else:
                return True, f"{pokemon_name} woke up!"
                
        elif status.effect == StatusEffect.FREEZE:
            # Fire-type moves or specific moves can thaw
            if move_name and ('fire' in move_name or move_name in ['flame-wheel', 'sacred-fire', 'flare-blitz']):
                return True, f"{pokemon_name} thawed out!"
            elif random.random() < 0.2:  # 20% chance to thaw naturally
                return True, f"{pokemon_name} thawed out!"
            else:
                return False, f"{pokemon_name} is frozen solid!"
                
        elif status.effect == StatusEffect.CONFUSION:
            if random.random() < 0.33:  # 33% chance to hurt itself
                # Self-damage calculation would happen elsewhere
                turn_data['confusion_self_damage'] = True
                return False, f"{pokemon_name} is confused and hurt itself!"
            elif random.random() < 0.5:  # Additional chance to be too confused to attack
                return False, f"{pokemon_name} is confused and can't attack!"
                
        elif status.effect == StatusEffect.FLINCH:
            # Flinch only lasts one turn and prevents action
            return False, f"{pokemon_name} flinched and couldn't move!"
            
        elif status.effect == StatusEffect.ATTRACT:
            if random.random() < 0.5:  # 50% chance to be immobilized by attraction
                return False, f"{pokemon_name} is immobilized by love!"
                
        elif status.effect == StatusEffect.TAUNT:
            # Can only use damaging moves when taunted
            if move_name and turn_data.get('move_power', 0) == 0:
                return False, f"{pokemon_name} can't use {move_name} after being taunted!"
                
        elif status.effect == StatusEffect.ENCORE:
            # Must use the same move as last turn
            last_move = turn_data.get('last_move_used', '')
            if move_name != last_move:
                return False, f"{pokemon_name} must use {last_move} due to encore!"
                
        elif status.effect == StatusEffect.TORMENT:
            # Can't use the same move twice in a row
            last_move = turn_data.get('last_move_used', '')
            if move_name == last_move:
                return False, f"{pokemon_name} can't use the same move twice due to torment!"
                
        elif status.effect == StatusEffect.DISABLE:
            # Specific move is disabled
            disabled_move = status.additional_data.get('disabled_move', '')
            if move_name == disabled_move:
                return False, f"{pokemon_name} can't use {move_name} - it's disabled!"
        
        return True, ""
    
    @staticmethod
    def modify_damage(attacker_status: Optional[StatusCondition], defender_status: Optional[StatusCondition],
                     damage: int, move_type: str = "", is_physical: bool = True) -> Tuple[int, str]:
        """Enhanced damage modification with status interactions"""
        modifier_messages = []
        
        # Attacker status effects
        if attacker_status:
            if attacker_status.effect == StatusEffect.BURN and is_physical:
                damage = damage // 2
                modifier_messages.append("Attack was weakened by burn!")
                
            elif attacker_status.effect == StatusEffect.PARALYSIS:
                if random.random() < 0.1:  # 10% chance for reduced power
                    damage = int(damage * 0.75)
                    modifier_messages.append("Attack was weakened by paralysis!")
        
        # Defender status effects that might affect damage taken
        if defender_status:
            if defender_status.effect == StatusEffect.CONFUSION and random.random() < 0.1:
                # Confused Pokemon might take extra damage occasionally
                damage = int(damage * 1.2)
                modifier_messages.append("Confusion made the attack more effective!")
        
        return damage, " ".join(modifier_messages)
    
    @staticmethod
    def tick_status(status: Optional[StatusCondition], turn_number: int = 0) -> Optional[StatusCondition]:
        """Enhanced status duration management"""
        if not status:
            return None
        
        # Handle duration-based statuses
        if status.duration > 0:
            status.duration -= 1
            
            # Special handling for badly poison
            if status.effect == StatusEffect.BADLY_POISON:
                status.severity += 1  # Damage increases each turn
            
            if status.duration <= 0:
                return None  # Status effect ended
                
        # Handle probability-based recovery
        elif status.duration == -1:  # Permanent until cured or probability
            if status.effect == StatusEffect.SLEEP:
                # Sleep lasts 1-3 turns typically
                if turn_number >= status.additional_data.get('sleep_turns', 3):
                    return None
            elif status.effect == StatusEffect.FREEZE:
                # 20% chance to thaw each turn
                if random.random() < 0.2:
                    return None
            elif status.effect == StatusEffect.CONFUSION:
                # Confusion lasts 1-4 turns
                confusion_turns = status.additional_data.get('confusion_turns', 0) + 1
                status.additional_data['confusion_turns'] = confusion_turns
                if confusion_turns >= random.randint(1, 4):
                    return None
                    
        return status
    
    @staticmethod
    def get_status_message(pokemon_name: str, old_status: Optional[StatusCondition], 
                          new_status: Optional[StatusCondition]) -> str:
        """Enhanced status change messaging"""
        if old_status and not new_status:
            effect_name = old_status.effect.value.replace('_', ' ')
            
            # Special recovery messages
            recovery_messages = {
                StatusEffect.SLEEP: f"{pokemon_name} woke up!",
                StatusEffect.FREEZE: f"{pokemon_name} thawed out!",
                StatusEffect.CONFUSION: f"{pokemon_name} snapped out of confusion!",
                StatusEffect.PARALYSIS: f"{pokemon_name} is no longer paralyzed!",
                StatusEffect.ATTRACT: f"{pokemon_name} got over its infatuation!",
                StatusEffect.TAUNT: f"{pokemon_name} is no longer taunted!",
                StatusEffect.ENCORE: f"The encore ended!",
                StatusEffect.TORMENT: f"{pokemon_name} is no longer tormented!",
                StatusEffect.DISABLE: f"The move is no longer disabled!"
            }
            
            return recovery_messages.get(old_status.effect, f"{pokemon_name} recovered from {effect_name}!")
            
        elif new_status and not old_status:
            effect_name = new_status.effect.value.replace('_', ' ')
            
            # Special infliction messages
            infliction_messages = {
                StatusEffect.BADLY_POISON: f"{pokemon_name} was badly poisoned!",
                StatusEffect.CONFUSION: f"{pokemon_name} became confused!",
                StatusEffect.ATTRACT: f"{pokemon_name} fell in love!",
                StatusEffect.CURSE: f"{pokemon_name} was cursed!",
                StatusEffect.NIGHTMARE: f"{pokemon_name} began having a nightmare!",
                StatusEffect.TAUNT: f"{pokemon_name} was taunted!",
                StatusEffect.ENCORE: f"{pokemon_name} received an encore!",
                StatusEffect.TORMENT: f"{pokemon_name} was tormented!",
                StatusEffect.DISABLE: f"One of {pokemon_name}'s moves was disabled!"
            }
            
            return infliction_messages.get(new_status.effect, f"{pokemon_name} was {effect_name}ed!")
            
        return ""
    
    @staticmethod
    def create_status(effect: StatusEffect, source_pokemon: str = "", **kwargs) -> StatusCondition:
        """Create enhanced status condition with proper parameters"""
        duration_map = {
            StatusEffect.BURN: -1,
            StatusEffect.POISON: -1,
            StatusEffect.BADLY_POISON: -1,
            StatusEffect.PARALYSIS: -1,
            StatusEffect.SLEEP: random.randint(1, 3),
            StatusEffect.FREEZE: -1,
            StatusEffect.CONFUSION: random.randint(1, 4),
            StatusEffect.FLINCH: 1,  # Only lasts one turn
            StatusEffect.ATTRACT: -1,
            StatusEffect.CURSE: -1,
            StatusEffect.NIGHTMARE: -1,
            StatusEffect.PERISH_SONG: 4,  # Faints after 4 turns
            StatusEffect.TORMENT: -1,
            StatusEffect.TAUNT: random.randint(2, 4),
            StatusEffect.ENCORE: random.randint(2, 6),
            StatusEffect.DISABLE: random.randint(1, 5),
        }
        
        additional_data = kwargs.copy()
        
        # Set specific additional data for complex statuses
        if effect == StatusEffect.SLEEP:
            additional_data['sleep_turns'] = duration_map[effect]
        elif effect == StatusEffect.DISABLE:
            additional_data['disabled_move'] = kwargs.get('disabled_move', '')
        elif effect == StatusEffect.NIGHTMARE:
            additional_data['sleeping'] = True
        
        return StatusCondition(
            effect=effect,
            duration=duration_map[effect],
            severity=1 if effect == StatusEffect.BADLY_POISON else 0,
            source_pokemon=source_pokemon,
            additional_data=additional_data
        )
    
    @staticmethod
    def can_be_statused(pokemon_name: str, pokemon_types: List[str], 
                       new_status: StatusEffect, current_status: Optional[StatusCondition] = None) -> bool:
        """Check if a Pokemon can be affected by a status condition"""
        # Already has a major status condition (burn, poison, paralysis, sleep, freeze)
        major_statuses = {StatusEffect.BURN, StatusEffect.POISON, StatusEffect.BADLY_POISON, 
                         StatusEffect.PARALYSIS, StatusEffect.SLEEP, StatusEffect.FREEZE}
        
        if current_status and current_status.effect in major_statuses and new_status in major_statuses:
            return False
        
        # Type immunities
        immunities = {
            'electric': [StatusEffect.PARALYSIS],
            'fire': [StatusEffect.BURN, StatusEffect.FREEZE],
            'ice': [StatusEffect.FREEZE],
            'poison': [StatusEffect.POISON, StatusEffect.BADLY_POISON],
            'steel': [StatusEffect.POISON, StatusEffect.BADLY_POISON],
        }
        
        for ptype in pokemon_types:
            if new_status in immunities.get(ptype, []):
                return False
        
        return True