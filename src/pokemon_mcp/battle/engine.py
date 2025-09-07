# src/pokemon_mcp/battle/engine.py
import random
import math
from dataclasses import dataclass
from typing import List, Optional, Tuple
from ..data.pokemon_client import Pokemon
from .mechanics import get_type_effectiveness
from .moves import Move, MoveCategory, get_pokemon_moves
from .status import StatusCondition

@dataclass
class BattleLog:
    turn: int
    message: str

@dataclass
class BattleResult:
    winner: str
    loser: str
    total_turns: int
    logs: List[BattleLog]

@dataclass
class BattleStats:
    attack: int
    defense: int
    special_attack: int
    special_defense: int
    speed: int

class BattlePokemon:
    def __init__(self, pokemon: Pokemon):
        self.pokemon = pokemon
        self.current_hp = pokemon.stats.hp
        self.max_hp = pokemon.stats.hp
        self.moves = []  # Will be populated with Move objects
        self.battle_stats = BattleStats(
            attack=pokemon.stats.attack,
            defense=pokemon.stats.defense,
            special_attack=pokemon.stats.special_attack,
            special_defense=pokemon.stats.special_defense,
            speed=pokemon.stats.speed
        )
    
    @property
    def is_fainted(self) -> bool:
        return self.current_hp <= 0
    
    @property
    def name(self) -> str:
        return self.pokemon.name
        
    async def initialize_moves(self):
        """Initialize moves from API data"""
        self.moves = await get_pokemon_moves(self.pokemon.moves)
    
    def get_stat(self, stat_name: str) -> int:
        """Get base stat value"""
        return getattr(self.battle_stats, stat_name)

class BattleEngine:
    def __init__(self):
        self.logs = []
        self.turn = 0
        
    def calculate_damage(self, attacker: BattlePokemon, 
                                defender: BattlePokemon, move: Move) -> Tuple[int, bool, float]:
        """FIXED: Proper Pokemon damage calculation"""
        
        # Base power
        power = move.power
        if power == 0:  # Status move
            return 0, False, 1.0
            
        # Attack and Defense stats
        if move.category == MoveCategory.PHYSICAL:
            attack = attacker.get_stat('attack')
            defense = defender.get_stat('defense')
        else:  # Special
            attack = attacker.get_stat('special_attack')
            defense = defender.get_stat('special_defense')
        
        # Level (assuming level 50 for competitive play)
        level = 50
        
        # CORRECT Pokemon damage formula
        # Damage = ((((2 * Level / 5 + 2) * Attack * Power / Defense) / 50) + 2) * Modifiers
        base_damage = (((2 * level / 5 + 2) * attack * power / defense) / 50) + 2
        
        # Apply modifiers
        damage = base_damage
        
        # STAB (Same Type Attack Bonus) - 1.5x
        stab_bonus = 1.0
        if move.type in attacker.pokemon.types:
            damage *= 1.5
            stab_bonus = 1.5
        
        # Type effectiveness
        type_mult = get_type_effectiveness(move.type, defender.pokemon.types)
        damage *= type_mult
        
        # Critical hit (6.25% chance) - 1.5x in modern games
        critical = False
        if random.random() < 0.0625:  # 1/16 chance
            damage *= 1.5
            critical = True
        
        # Random factor (85-100%) - this prevents exact damage predictions
        damage *= random.uniform(0.85, 1.0)
        
        # Ensure minimum 1 damage, maximum reasonable damage
        final_damage = max(1, min(int(damage), defender.max_hp))
        
        return final_damage, critical, type_mult
    
    def check_accuracy(self, attacker: BattlePokemon, 
                  defender: BattlePokemon, move: Move) -> bool:
        """Check if move hits based on accuracy"""
        return random.randint(1, 100) <= move.accuracy
    
    def select_move(self, pokemon: BattlePokemon, 
                   opponent: BattlePokemon) -> Move:
        """AI move selection with basic strategy"""
        available_moves = [m for m in pokemon.moves if m.pp > 0]
        
        if not available_moves:
            # Struggle (last resort) - weak but always works
            return Move("struggle", "normal", MoveCategory.PHYSICAL, 50, 100, 1)
        
        # Simple AI: prefer super effective moves, but not exclusively
        best_moves = []
        good_moves = []
        
        for move in available_moves:
            effectiveness = get_type_effectiveness(move.type, opponent.pokemon.types)
            
            if effectiveness >= 2.0:  # Super effective
                best_moves.append(move)
            elif effectiveness >= 1.0:  # Normal or better
                good_moves.append(move)
        
        # 70% chance to use super effective move if available
        if best_moves and random.random() < 0.7:
            return random.choice(best_moves)
        elif good_moves:
            return random.choice(good_moves)
        else:
            return random.choice(available_moves)
    
    async def simulate_battle(self, pokemon1: Pokemon, 
                                     pokemon2: Pokemon) -> BattleResult:
        """Simulate battle with proper damage calculations"""
        self.logs = []
        self.turn = 0
        
        # Create battle Pokemon
        p1 = BattlePokemon(pokemon1)
        p2 = BattlePokemon(pokemon2)
        
        # Initialize moves properly with async
        await p1.initialize_moves()
        await p2.initialize_moves()
        
        self._log(f"Battle begins! {p1.pokemon.name} (HP: {p1.max_hp}) vs {p2.pokemon.name} (HP: {p2.max_hp})")
        self._log(f"{p1.pokemon.name} types: {', '.join(p1.pokemon.types)}")
        self._log(f"{p2.pokemon.name} types: {', '.join(p2.pokemon.types)}")
        
        max_turns = 50  # Reasonable limit to prevent infinite battles
        
        while not p1.is_fainted and not p2.is_fainted and self.turn < max_turns:
            self.turn += 1
            self._log(f"--- Turn {self.turn} ---")
            
            # Determine turn order based on speed
            p1_speed = p1.get_stat('speed')
            p2_speed = p2.get_stat('speed')
            
            if p1_speed > p2_speed:
                first, second = p1, p2
            elif p2_speed > p1_speed:
                first, second = p2, p1
            else:
                # Speed tie - random
                first, second = random.choice([(p1, p2), (p2, p1)])
            
            # Execute turns
            if not first.is_fainted:
                self._execute_turn(first, second)
            
            if not second.is_fainted and not first.is_fainted:
                self._execute_turn(second, first)
        
        # Determine winner
        if p1.is_fainted and not p2.is_fainted:
            winner, loser = p2.pokemon.name, p1.pokemon.name
        elif p2.is_fainted and not p1.is_fainted:
            winner, loser = p1.pokemon.name, p2.pokemon.name
        elif self.turn >= max_turns:
            # Battle timeout - winner by remaining HP
            if p1.current_hp > p2.current_hp:
                winner, loser = p1.pokemon.name, p2.pokemon.name
                self._log(f"Battle timeout! Winner determined by remaining HP: {winner}")
            elif p2.current_hp > p1.current_hp:
                winner, loser = p2.pokemon.name, p1.pokemon.name
                self._log(f"Battle timeout! Winner determined by remaining HP: {winner}")
            else:
                winner, loser = "Draw", "Draw"
                self._log("Battle ended in a draw!")
        else:
            winner, loser = "Draw", "Draw"
        
        self._log(f"Battle concluded! Winner: {winner}")
        
        return BattleResult(
            winner=winner,
            loser=loser,
            total_turns=self.turn,
            logs=self.logs
        )
    
    def _execute_turn(self, attacker: BattlePokemon, 
                           defender: BattlePokemon):
        """Execute a Pokemon's turn"""
        # Select and use move
        move = self.select_move(attacker, defender)
        self._use_move(attacker, defender, move)
    
    def _use_move(self, attacker: BattlePokemon, 
                       defender: BattlePokemon, move: Move):
        """Execute a move"""
        self._log(f"{attacker.pokemon.name} uses {move.name}!")
        
        # Reduce PP
        if move.pp > 0:
            move.pp -= 1
        
        # Check accuracy
        if not self.check_accuracy(attacker, defender, move):
            self._log(f"{attacker.pokemon.name}'s attack missed!")
            return
        
        # Calculate damage
        damage, is_critical, type_mult = self.calculate_damage(attacker, defender, move)
        
        if damage > 0:
            old_hp = defender.current_hp
            defender.current_hp = max(0, defender.current_hp - damage)
            actual_damage = old_hp - defender.current_hp
            
            # Build damage message
            msg_parts = [f"Deals {actual_damage} damage!"]
            
            if is_critical:
                msg_parts.append("Critical hit!")
            
            if type_mult > 1.0:
                msg_parts.append("It's super effective!")
            elif type_mult < 1.0 and type_mult > 0:
                msg_parts.append("It's not very effective...")
            elif type_mult == 0:
                msg_parts.append("It has no effect!")
            
            self._log(" ".join(msg_parts))
            
            if defender.is_fainted:
                self._log(f"{defender.pokemon.name} fainted!")
            else:
                hp_percentage = int((defender.current_hp / defender.max_hp) * 100)
                self._log(f"{defender.pokemon.name}: {defender.current_hp}/{defender.max_hp} HP ({hp_percentage}% remaining)")
        else:
            self._log(f"{move.name} had no effect!")
    
    def _log(self, message: str):
        """Add message to battle log"""
        self.logs.append(BattleLog(turn=self.turn, message=message))