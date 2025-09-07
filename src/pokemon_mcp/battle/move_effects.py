# src/pokemon_mcp/battle/move_effects.py
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import random

class MoveEffect(Enum):
    # Damage effects
    FIXED_DAMAGE = "fixed_damage"
    LEVEL_DAMAGE = "level_damage"  # Dragon Rage, Sonic Boom
    USER_HP_DAMAGE = "user_hp_damage"  # Struggle, recoil moves
    
    # Stat modifications
    RAISE_ATTACK = "raise_attack"
    RAISE_DEFENSE = "raise_defense"
    RAISE_SPECIAL_ATTACK = "raise_special_attack"
    RAISE_SPECIAL_DEFENSE = "raise_special_defense"
    RAISE_SPEED = "raise_speed"
    RAISE_ACCURACY = "raise_accuracy"
    RAISE_EVASION = "raise_evasion"
    
    LOWER_ATTACK = "lower_attack"
    LOWER_DEFENSE = "lower_defense"
    LOWER_SPECIAL_ATTACK = "lower_special_attack"
    LOWER_SPECIAL_DEFENSE = "lower_special_defense"
    LOWER_SPEED = "lower_speed"
    LOWER_ACCURACY = "lower_accuracy"
    LOWER_EVASION = "lower_evasion"
    
    # Multi-hit effects
    MULTI_HIT_2_5 = "multi_hit_2_5"  # Fury Swipes, Pin Missile
    MULTI_HIT_2 = "multi_hit_2"      # Double Kick
    MULTI_HIT_3 = "multi_hit_3"      # Triple Kick
    
    # Healing effects
    HEAL_USER = "heal_user"
    HEAL_USER_STATUS = "heal_user_status"
    DRAIN_HP = "drain_hp"  # Absorb, Mega Drain
    
    # Weather effects
    SET_SUNNY = "set_sunny"
    SET_RAIN = "set_rain"
    SET_SANDSTORM = "set_sandstorm"
    SET_HAIL = "set_hail"
    
    # Special effects
    PRIORITY_MOVE = "priority_move"
    OHKO = "ohko"  # One-hit KO moves
    CHARGE_TURN = "charge_turn"  # Solar Beam, Fly
    PROTECT = "protect"
    FLINCH = "flinch"
    CONFUSE = "confuse"
    
    # Type changing
    CHANGE_USER_TYPE = "change_user_type"
    
    # Misc
    COPY_TARGET_STATS = "copy_target_stats"  # Psych Up
    RESET_STATS = "reset_stats"  # Haze
    SWITCH_STATS = "switch_stats"  # Power Swap

@dataclass
class MoveEffectData:
    effect: MoveEffect
    chance: float = 1.0  # Probability of effect occurring
    magnitude: int = 1   # How strong the effect is (stat stages, etc.)
    target: str = "opponent"  # "self", "opponent", "both"
    additional_data: Dict[str, Any] = None

class MoveEffectProcessor:
    """Processes move effects during battle"""
    
    def __init__(self):
        self.weather = None
        self.weather_turns = 0
    
    def process_move_effects(self, move_data: dict, attacker, defender, battle_context: dict) -> List[str]:
        """Process all effects of a move and return log messages"""
        messages = []
        
        # Get move effects from API data
        effects = self._parse_move_effects(move_data)
        
        for effect_data in effects:
            if random.random() <= effect_data.chance:
                effect_messages = self._apply_effect(effect_data, attacker, defender, battle_context)
                messages.extend(effect_messages)
        
        return messages
    
    def _parse_move_effects(self, move_data: dict) -> List[MoveEffectData]:
        """Parse move effects from API data"""
        effects = []
        
        # Parse from effect entries
        effect_entries = move_data.get('effect_entries', [])
        effect_text = ""
        for entry in effect_entries:
            if entry['language']['name'] == 'en':
                effect_text = entry['effect'].lower()
                break
        
        # Parse stat changes
        stat_changes = move_data.get('stat_changes', [])
        for stat_change in stat_changes:
            stat_name = stat_change['stat']['name']
            change = stat_change['change']
            
            if change > 0:
                effect_type = f"raise_{stat_name.replace('-', '_')}"
            else:
                effect_type = f"lower_{stat_name.replace('-', '_')}"
            
            try:
                effect = MoveEffect(effect_type)
                effects.append(MoveEffectData(
                    effect=effect,
                    magnitude=abs(change),
                    target="self" if "user" in effect_text or "self" in effect_text else "opponent"
                ))
            except ValueError:
                continue
        
        # Parse specific move effects based on move name
        move_name = move_data['name']
        specific_effects = self._get_specific_move_effects(move_name, move_data)
        effects.extend(specific_effects)
        
        return effects
    
    def _get_specific_move_effects(self, move_name: str, move_data: dict) -> List[MoveEffectData]:
        """Get effects for specific well-known moves"""
        effects = []
        
        # Multi-hit moves
        multi_hit_moves = {
            'fury-swipes': MoveEffectData(MoveEffect.MULTI_HIT_2_5),
            'pin-missile': MoveEffectData(MoveEffect.MULTI_HIT_2_5),
            'spike-cannon': MoveEffectData(MoveEffect.MULTI_HIT_2_5),
            'double-kick': MoveEffectData(MoveEffect.MULTI_HIT_2),
            'double-slap': MoveEffectData(MoveEffect.MULTI_HIT_2_5),
        }
        
        if move_name in multi_hit_moves:
            effects.append(multi_hit_moves[move_name])
        
        # Weather moves
        weather_moves = {
            'sunny-day': MoveEffectData(MoveEffect.SET_SUNNY),
            'rain-dance': MoveEffectData(MoveEffect.SET_RAIN),
            'sandstorm': MoveEffectData(MoveEffect.SET_SANDSTORM),
            'hail': MoveEffectData(MoveEffect.SET_HAIL),
        }
        
        if move_name in weather_moves:
            effects.append(weather_moves[move_name])
        
        # Healing moves
        healing_moves = {
            'recover': MoveEffectData(MoveEffect.HEAL_USER, magnitude=50),  # 50% HP
            'soft-boiled': MoveEffectData(MoveEffect.HEAL_USER, magnitude=50),
            'rest': MoveEffectData(MoveEffect.HEAL_USER, magnitude=100),
            'absorb': MoveEffectData(MoveEffect.DRAIN_HP, magnitude=50),
            'mega-drain': MoveEffectData(MoveEffect.DRAIN_HP, magnitude=50),
            'giga-drain': MoveEffectData(MoveEffect.DRAIN_HP, magnitude=50),
        }
        
        if move_name in healing_moves:
            effects.append(healing_moves[move_name])
        
        # Priority moves
        priority = move_data.get('priority', 0)
        if priority > 0:
            effects.append(MoveEffectData(MoveEffect.PRIORITY_MOVE, magnitude=priority))
        
        # OHKO moves
        ohko_moves = ['fissure', 'guillotine', 'horn-drill', 'sheer-cold']
        if move_name in ohko_moves:
            effects.append(MoveEffectData(MoveEffect.OHKO, chance=0.3))  # 30% base accuracy
        
        # Flinch moves
        flinch_chance = self._extract_flinch_chance(move_data)
        if flinch_chance > 0:
            effects.append(MoveEffectData(MoveEffect.FLINCH, chance=flinch_chance))
        
        return effects
    
    def _extract_flinch_chance(self, move_data: dict) -> float:
        """Extract flinch chance from move data"""
        # Moves that commonly cause flinching
        flinch_moves = {
            'air-slash': 0.3,
            'bite': 0.3,
            'dark-pulse': 0.2,
            'extrasensory': 0.1,
            'fake-out': 1.0,
            'fire-fang': 0.1,
            'headbutt': 0.3,
            'hyper-fang': 0.1,
            'ice-fang': 0.1,
            'iron-head': 0.3,
            'needle-arm': 0.3,
            'rock-slide': 0.3,
            'sky-attack': 0.3,
            'snore': 0.3,
            'stomp': 0.3,
            'thunder-fang': 0.1,
            'twister': 0.2,
            'waterfall': 0.2,
            'zen-headbutt': 0.2,
        }
        
        move_name = move_data['name']
        return flinch_moves.get(move_name, 0.0)
    
    def _apply_effect(self, effect_data: MoveEffectData, attacker, defender, 
                     battle_context: dict) -> List[str]:
        """Apply a specific move effect"""
        messages = []
        target = attacker if effect_data.target == "self" else defender
        
        if effect_data.effect in [MoveEffect.RAISE_ATTACK, MoveEffect.RAISE_DEFENSE,
                                 MoveEffect.RAISE_SPECIAL_ATTACK, MoveEffect.RAISE_SPECIAL_DEFENSE,
                                 MoveEffect.RAISE_SPEED, MoveEffect.RAISE_ACCURACY, MoveEffect.RAISE_EVASION]:
            stat_name = effect_data.effect.value.replace("raise_", "")
            success = target.modify_stat_stage(stat_name, effect_data.magnitude)
            if success:
                messages.append(f"{target.pokemon.name}'s {stat_name.replace('_', ' ').title()} rose!")
            else:
                messages.append(f"{target.pokemon.name}'s {stat_name.replace('_', ' ').title()} won't go higher!")
        
        elif effect_data.effect in [MoveEffect.LOWER_ATTACK, MoveEffect.LOWER_DEFENSE,
                                   MoveEffect.LOWER_SPECIAL_ATTACK, MoveEffect.LOWER_SPECIAL_DEFENSE,
                                   MoveEffect.LOWER_SPEED, MoveEffect.LOWER_ACCURACY, MoveEffect.LOWER_EVASION]:
            stat_name = effect_data.effect.value.replace("lower_", "")
            success = target.modify_stat_stage(stat_name, -effect_data.magnitude)
            if success:
                messages.append(f"{target.pokemon.name}'s {stat_name.replace('_', ' ').title()} fell!")
            else:
                messages.append(f"{target.pokemon.name}'s {stat_name.replace('_', ' ').title()} won't go lower!")
        
        elif effect_data.effect == MoveEffect.HEAL_USER:
            heal_amount = (attacker.max_hp * effect_data.magnitude) // 100
            old_hp = attacker.current_hp
            attacker.current_hp = min(attacker.max_hp, attacker.current_hp + heal_amount)
            actual_heal = attacker.current_hp - old_hp
            if actual_heal > 0:
                messages.append(f"{attacker.pokemon.name} recovered {actual_heal} HP!")
            else:
                messages.append(f"{attacker.pokemon.name} is already at full health!")
        
        elif effect_data.effect == MoveEffect.DRAIN_HP:
            # Assumes damage was already calculated and stored in battle_context
            damage_dealt = battle_context.get('last_damage', 0)
            heal_amount = (damage_dealt * effect_data.magnitude) // 100
            old_hp = attacker.current_hp
            attacker.current_hp = min(attacker.max_hp, attacker.current_hp + heal_amount)
            actual_heal = attacker.current_hp - old_hp
            if actual_heal > 0:
                messages.append(f"{attacker.pokemon.name} drained {actual_heal} HP!")
        
        elif effect_data.effect in [MoveEffect.SET_SUNNY, MoveEffect.SET_RAIN,
                                   MoveEffect.SET_SANDSTORM, MoveEffect.SET_HAIL]:
            weather_names = {
                MoveEffect.SET_SUNNY: "harsh sunlight",
                MoveEffect.SET_RAIN: "rain",
                MoveEffect.SET_SANDSTORM: "sandstorm",
                MoveEffect.SET_HAIL: "hail"
            }
            self.weather = effect_data.effect
            self.weather_turns = 5
            messages.append(f"The weather changed to {weather_names[effect_data.effect]}!")
        
        elif effect_data.effect == MoveEffect.MULTI_HIT_2_5:
            hits = random.choices([2, 3, 4, 5], weights=[37.5, 37.5, 12.5, 12.5])[0]
            battle_context['multi_hit_count'] = hits
            messages.append(f"Hit {hits} times!")
        
        elif effect_data.effect == MoveEffect.MULTI_HIT_2:
            battle_context['multi_hit_count'] = 2
            messages.append("Hit 2 times!")
        
        elif effect_data.effect == MoveEffect.OHKO:
            # Implement OHKO logic
            if defender.current_hp > 0:
                defender.current_hp = 0
                messages.append(f"It's a one-hit KO!")
        
        elif effect_data.effect == MoveEffect.FLINCH:
            # Set flinch flag for next turn
            battle_context['flinched'] = True
            messages.append(f"{defender.pokemon.name} flinched!")
        
        return messages
    
    def apply_weather_effects(self, pokemon, battle_context: dict) -> List[str]:
        """Apply weather effects at end of turn"""
        messages = []
        
        if self.weather_turns <= 0:
            return messages
        
        if self.weather == MoveEffect.SET_SANDSTORM:
            if 'rock' not in pokemon.pokemon.types and 'ground' not in pokemon.pokemon.types and 'steel' not in pokemon.pokemon.types:
                damage = pokemon.max_hp // 16
                pokemon.current_hp = max(0, pokemon.current_hp - damage)
                messages.append(f"{pokemon.pokemon.name} is hurt by the sandstorm! ({damage} damage)")
        
        elif self.weather == MoveEffect.SET_HAIL:
            if 'ice' not in pokemon.pokemon.types:
                damage = pokemon.max_hp // 16
                pokemon.current_hp = max(0, pokemon.current_hp - damage)
                messages.append(f"{pokemon.pokemon.name} is hurt by the hail! ({damage} damage)")
        
        self.weather_turns -= 1
        if self.weather_turns <= 0:
            weather_names = {
                MoveEffect.SET_SUNNY: "harsh sunlight",
                MoveEffect.SET_RAIN: "rain",
                MoveEffect.SET_SANDSTORM: "sandstorm",
                MoveEffect.SET_HAIL: "hail"
            }
            messages.append(f"The {weather_names[self.weather]} stopped!")
            self.weather = None
        
        return messages
    
    def get_weather_damage_modifier(self, move_type: str) -> float:
        """Get damage modifier based on current weather"""
        if self.weather == MoveEffect.SET_SUNNY:
            if move_type == 'fire':
                return 1.5
            elif move_type == 'water':
                return 0.5
        elif self.weather == MoveEffect.SET_RAIN:
            if move_type == 'water':
                return 1.5
            elif move_type == 'fire':
                return 0.5
        
        return 1.0