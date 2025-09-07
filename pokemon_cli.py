
"""
Pokemon MCP Server - Demo CLI Tool
Comprehensive testing interface for all Pokemon MCP Server features
"""
import asyncio
import sys
import json
from pathlib import Path
from typing import Optional

# Add the src directory to the path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from pokemon_mcp.data.pokemon_client import PokemonClient
from pokemon_mcp.battle.engine import BattleEngine
from pokemon_mcp.data.evolution import EvolutionClient
from pokemon_mcp.utils.health_check import HealthCheck
from pokemon_mcp.utils.logger import Logger

class PokemonCLI:
    def __init__(self):
        self.pokemon_client = PokemonClient()
        self.battle_engine = BattleEngine()
        self.evolution_client = EvolutionClient()
        self.health_check = HealthCheck()
        self.logger = Logger()
        
    async def main_menu(self):
        """Display main menu and handle user input"""
        while True:
            print("\n" + "="*60)
            print("🎮 POKEMON MCP SERVER - DEMO CLI")
            print("="*60)
            print("1. 🔍 Search Pokemon")
            print("2. ⚔️  Simulate Battle")
            print("3. 🔄 Evolution Analysis") 
            print("4. 📊 Server Health Check")
            print("5. 🎯 Advanced Battle with Status Effects")
            print("6. 🌟 Evolution Line Explorer")
            print("7. 📈 Pokemon Stats Comparison")
            print("8. 🔧 System Diagnostics")
            print("9. 📝 Battle with Full Logs")
            print("0. ❌ Exit")
            print("="*60)
            
            choice = input("Enter your choice (0-9): ").strip()
            
            try:
                if choice == "1":
                    await self.search_pokemon()
                elif choice == "2":
                    await self.simulate_battle()
                elif choice == "3":
                    await self.evolution_analysis()
                elif choice == "4":
                    await self.health_check_menu()
                elif choice == "5":
                    await self.advanced_battle()
                elif choice == "6":
                    await self.evolution_explorer()
                elif choice == "7":
                    await self.pokemon_comparison()
                elif choice == "8":
                    await self.system_diagnostics()
                elif choice == "9":
                    await self.detailed_battle()
                elif choice == "0":
                    print("👋 Thanks for using Pokemon MCP Server CLI!")
                    await self.cleanup()
                    break
                else:
                    print("❌ Invalid choice. Please try again.")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Exiting...")
                await self.cleanup()
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                self.logger.error(f"CLI Error: {e}")
    
    async def search_pokemon(self):
        """Search for Pokemon with detailed information"""
        print("\n🔍 POKEMON SEARCH")
        print("-" * 30)
        
        name = input("Enter Pokemon name or ID: ").strip()
        if not name:
            print("❌ Please enter a Pokemon name or ID")
            return
            
        print(f"🔍 Searching for {name}...")
        
        pokemon = await self.pokemon_client.get_pokemon(name, include_evolution=True)
        if not pokemon:
            print(f"❌ Pokemon '{name}' not found")
            return
            
        # Display detailed Pokemon information
        print(f"\n✅ Found: {pokemon.name.title()} (#{pokemon.id})")
        print(f"📏 Height: {pokemon.height/10:.1f}m | Weight: {pokemon.weight/10:.1f}kg")
        print(f"⭐ Base Experience: {pokemon.base_experience}")
        
        # Types with emoji
        type_emojis = {
            'fire': '🔥', 'water': '💧', 'grass': '🌱', 'electric': '⚡',
            'normal': '⚪', 'fighting': '👊', 'poison': '☠️', 'ground': '🌍',
            'flying': '🦅', 'psychic': '🔮', 'bug': '🐛', 'rock': '🗿',
            'ghost': '👻', 'dragon': '🐉', 'dark': '🌑', 'steel': '⚙️',
            'fairy': '🧚', 'ice': '❄️'
        }
        
        types_str = " ".join([f"{type_emojis.get(t, '❓')}{t.title()}" for t in pokemon.types])
        print(f"🏷️  Types: {types_str}")
        
        # Stats
        print(f"\n📊 STATS:")
        stats = pokemon.stats
        print(f"   HP: {stats.hp:3d} | Attack: {stats.attack:3d} | Defense: {stats.defense:3d}")
        print(f"   Sp.Atk: {stats.special_attack:3d} | Sp.Def: {stats.special_defense:3d} | Speed: {stats.speed:3d}")
        print(f"   Total: {stats.hp + stats.attack + stats.defense + stats.special_attack + stats.special_defense + stats.speed}")
        
        # Abilities
        print(f"\n⚡ Abilities: {', '.join(pokemon.abilities)}")
        
        # Sample moves
        print(f"\n🎯 Sample Moves: {', '.join(pokemon.moves[:8])}")
        
        # Evolution information
        if pokemon.evolution_chain:
            evo = pokemon.evolution_chain
            print(f"\n🔄 Evolution Chain: {evo.species_name}")
            if evo.evolves_to:
                print(f"   Evolves to: {' → '.join(evo.evolves_to)}")
        
        input("\nPress Enter to continue...")
    
    async def simulate_battle(self):
        """Simulate a basic battle between two Pokemon"""
        print("\n⚔️ BATTLE SIMULATION")
        print("-" * 30)
        
        pokemon1_name = input("Enter first Pokemon: ").strip()
        pokemon2_name = input("Enter second Pokemon: ").strip()
        
        if not pokemon1_name or not pokemon2_name:
            print("❌ Please enter both Pokemon names")
            return
            
        print(f"🔍 Loading {pokemon1_name} and {pokemon2_name}...")
        
        # Fetch Pokemon
        pokemon1 = await self.pokemon_client.get_pokemon(pokemon1_name, include_evolution=False)
        pokemon2 = await self.pokemon_client.get_pokemon(pokemon2_name, include_evolution=False)
        
        if not pokemon1:
            print(f"❌ {pokemon1_name} not found")
            return
        if not pokemon2:
            print(f"❌ {pokemon2_name} not found")
            return
            
        print(f"\n🥊 {pokemon1.name.title()} VS {pokemon2.name.title()}")
        print(f"   {pokemon1.name}: HP={pokemon1.stats.hp}, ATK={pokemon1.stats.attack}, SPD={pokemon1.stats.speed}")
        print(f"   {pokemon2.name}: HP={pokemon2.stats.hp}, ATK={pokemon2.stats.attack}, SPD={pokemon2.stats.speed}")
        
        # Simulate battle
        result = self.battle_engine.simulate_battle(pokemon1, pokemon2)
        
        print(f"\n🏆 BATTLE RESULT:")
        print(f"   Winner: {result.winner.title()}")
        print(f"   Loser: {result.loser.title()}")
        print(f"   Total Turns: {result.total_turns}")
        
        # Show last few log entries
        print(f"\n📝 Battle Highlights (last 5 events):")
        for log in result.logs[-5:]:
            print(f"   Turn {log.turn}: {log.message}")
        
        input("\nPress Enter to continue...")
    
    async def evolution_analysis(self):
        """Analyze Pokemon evolution chains"""
        print("\n🔄 EVOLUTION ANALYSIS")
        print("-" * 30)
        
        name = input("Enter Pokemon name: ").strip()
        if not name:
            print("❌ Please enter a Pokemon name")
            return
            
        print(f"🔄 Analyzing evolution chain for {name}...")
        
        # Get evolution tree
        tree = await self.evolution_client.get_evolution_tree(name)
        if not tree:
            print(f"❌ No evolution data found for {name}")
            return
            
        print(f"\n🌳 EVOLUTION TREE (Chain ID: {tree['chain_id']})")
        
        if tree.get('baby_trigger_item'):
            print(f"👶 Baby Trigger Item: {tree['baby_trigger_item']}")
        
        print("\n🔄 Evolution Stages:")
        for evolution in tree['evolutions']:
            stage_indicator = "🥚" if evolution['is_baby'] else f"⭐{evolution['stage']}"
            print(f"\n{stage_indicator} {evolution['species'].title()} (Stage {evolution['stage']})")
            
            if evolution['conditions']:
                print("   Requirements:")
                for condition in evolution['conditions']:
                    trigger = condition['trigger'].replace('-', ' ').title()
                    print(f"     • Trigger: {trigger}")
                    
                    reqs = condition.get('requirements', {})
                    if reqs:
                        for req, value in reqs.items():
                            req_display = req.replace('_', ' ').title()
                            print(f"       - {req_display}: {value}")
        
        # Check what current Pokemon can evolve into
        can_evolve = await self.evolution_client.can_evolve(name, level=50)
        if can_evolve:
            print(f"\n✨ {name.title()} can evolve into: {', '.join(can_evolve)}")
        else:
            print(f"\n🚫 {name.title()} cannot evolve further")
        
        input("\nPress Enter to continue...")
    
    async def health_check_menu(self):
        """System health check"""
        print("\n📊 SYSTEM HEALTH CHECK")
        print("-" * 30)
        
        print("🔍 Checking system health...")
        
        # Check API connectivity
        api_status = await self.health_check.check_pokeapi()
        print(f"📡 PokéAPI: {'✅ Online' if api_status else '❌ Offline'}")
        
        # Check MCP server components
        server_status = self.health_check.check_mcp_server()
        print(f"🖥️  MCP Server: {'✅ Ready' if server_status else '❌ Error'}")
        
        # Check database/cache
        cache_status = self.health_check.check_cache()
        print(f"💾 Cache System: {'✅ Available' if cache_status else '⚠️  Limited'}")
        
        # Memory usage
        memory_info = self.health_check.get_memory_usage()
        print(f"🧠 Memory Usage: {memory_info}MB")
        
        # Response time test
        print("\n⏱️  Testing response times...")
        response_time = await self.health_check.test_response_time()
        print(f"📈 Avg Response Time: {response_time:.2f}ms")
        
        input("\nPress Enter to continue...")
    
    async def advanced_battle(self):
        """Advanced battle with status effects and detailed mechanics"""
        print("\n🎯 ADVANCED BATTLE SIMULATION")
        print("-" * 30)
        
        pokemon1_name = input("Enter first Pokemon: ").strip()
        pokemon2_name = input("Enter second Pokemon: ").strip()
        
        if not pokemon1_name or not pokemon2_name:
            print("❌ Please enter both Pokemon names")
            return
            
        # Get Pokemon with full details
        pokemon1 = await self.pokemon_client.get_pokemon(pokemon1_name)
        pokemon2 = await self.pokemon_client.get_pokemon(pokemon2_name)
        
        if not pokemon1 or not pokemon2:
            print("❌ One or both Pokemon not found")
            return
            
        print(f"\n🎯 ADVANCED BATTLE: {pokemon1.name.title()} VS {pokemon2.name.title()}")
        
        # Note: This would use the advanced battle system if we had it
        # For now, use the enhanced regular battle
        result = self.battle_engine.simulate_battle(pokemon1, pokemon2)
        
        print(f"\n🏆 ADVANCED BATTLE RESULT:")
        print(f"   Champion: {result.winner.title()}")
        print(f"   Defeated: {result.loser.title()}")
        print(f"   Battle Duration: {result.total_turns} turns")
        
        # Show detailed battle log
        print(f"\n📜 COMPLETE BATTLE LOG:")
        for log in result.logs:
            print(f"   Turn {log.turn:2d}: {log.message}")
        
        input("\nPress Enter to continue...")
    
    async def evolution_explorer(self):
        """Explore complete evolution lines"""
        print("\n🌟 EVOLUTION LINE EXPLORER")
        print("-" * 30)
        
        name = input("Enter Pokemon name: ").strip()
        if not name:
            return
            
        print(f"🔍 Getting evolution line for {name}...")
        
        evolution_line = await self.pokemon_client.get_evolution_line(name)
        if not evolution_line:
            print(f"❌ No evolution line found for {name}")
            return
            
        print(f"\n🌟 COMPLETE EVOLUTION LINE ({len(evolution_line)} stages)")
        print("=" * 50)
        
        for i, pokemon in enumerate(evolution_line):
            stage_emoji = ["🥚", "🐛", "🦋", "🐉"][min(i, 3)]
            total_stats = sum([pokemon.stats.hp, pokemon.stats.attack, pokemon.stats.defense,
                             pokemon.stats.special_attack, pokemon.stats.special_defense, pokemon.stats.speed])
            
            print(f"\n{stage_emoji} STAGE {i+1}: {pokemon.name.title()}")
            print(f"   Types: {' + '.join(pokemon.types).title()}")
            print(f"   Base Stats Total: {total_stats}")
            print(f"   HP: {pokemon.stats.hp} | ATK: {pokemon.stats.attack} | DEF: {pokemon.stats.defense}")
            print(f"   SP.ATK: {pokemon.stats.special_attack} | SP.DEF: {pokemon.stats.special_defense} | SPD: {pokemon.stats.speed}")
            
            if i < len(evolution_line) - 1:
                print("   ⬇️  Evolves to...")
        
        input("\nPress Enter to continue...")
    
    async def pokemon_comparison(self):
        """Compare two Pokemon stats side by side"""
        print("\n📈 POKEMON STATS COMPARISON")
        print("-" * 30)
        
        pokemon1_name = input("Enter first Pokemon: ").strip()
        pokemon2_name = input("Enter second Pokemon: ").strip()
        
        if not pokemon1_name or not pokemon2_name:
            return
            
        # Get both Pokemon
        pokemon1 = await self.pokemon_client.get_pokemon(pokemon1_name)
        pokemon2 = await self.pokemon_client.get_pokemon(pokemon2_name)
        
        if not pokemon1 or not pokemon2:
            print("❌ One or both Pokemon not found")
            return
            
        print(f"\n📊 COMPARISON: {pokemon1.name.title()} VS {pokemon2.name.title()}")
        print("=" * 60)
        
        # Stats comparison
        stats = ['hp', 'attack', 'defense', 'special_attack', 'special_defense', 'speed']
        stat_names = ['HP', 'Attack', 'Defense', 'Sp. Attack', 'Sp. Defense', 'Speed']
        
        print(f"{'Stat':<12} {'|':<1} {pokemon1.name.title():<15} {'|':<1} {pokemon2.name.title():<15} {'|':<1} {'Winner':<10}")
        print("-" * 60)
        
        p1_wins = 0
        p2_wins = 0
        
        for stat, stat_name in zip(stats, stat_names):
            p1_val = getattr(pokemon1.stats, stat)
            p2_val = getattr(pokemon2.stats, stat)
            
            if p1_val > p2_val:
                winner = pokemon1.name.title()
                p1_wins += 1
            elif p2_val > p1_val:
                winner = pokemon2.name.title()
                p2_wins += 1
            else:
                winner = "Tie"
            
            print(f"{stat_name:<12} | {p1_val:<15d} | {p2_val:<15d} | {winner:<10}")
        
        # Total stats
        p1_total = sum(getattr(pokemon1.stats, stat) for stat in stats)
        p2_total = sum(getattr(pokemon2.stats, stat) for stat in stats)
        
        print("-" * 60)
        print(f"{'TOTAL':<12} | {p1_total:<15d} | {p2_total:<15d} | {'Better overall':<10}")
        
        print(f"\n🏆 SUMMARY:")
        print(f"   {pokemon1.name.title()} wins {p1_wins} stats")
        print(f"   {pokemon2.name.title()} wins {p2_wins} stats")
        
        if p1_total > p2_total:
            print(f"   🎯 {pokemon1.name.title()} has higher total stats ({p1_total} vs {p2_total})")
        elif p2_total > p1_total:
            print(f"   🎯 {pokemon2.name.title()} has higher total stats ({p2_total} vs {p1_total})")
        else:
            print(f"   🤝 Equal total stats ({p1_total})")
        
        input("\nPress Enter to continue...")
    
    async def system_diagnostics(self):
        """Run comprehensive system diagnostics"""
        print("\n🔧 SYSTEM DIAGNOSTICS")
        print("-" * 30)
        
        print("🔍 Running comprehensive diagnostics...")
        
        # Test all major components
        tests = [
            ("PokéAPI Connectivity", self.health_check.check_pokeapi()),
            ("MCP Server Status", self.health_check.check_mcp_server()),
            ("Battle Engine", self._test_battle_engine()),
            ("Evolution System", self._test_evolution_system()),
            ("Cache Performance", self.health_check.check_cache()),
        ]
        
        results = []
        for test_name, test_coro in tests:
            if asyncio.iscoroutine(test_coro):
                result = await test_coro
            else:
                result = test_coro
            results.append((test_name, result))
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"   {test_name}: {status}")
        
        # Summary
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        print(f"\n📊 DIAGNOSTIC SUMMARY:")
        print(f"   Tests Passed: {passed}/{total}")
        print(f"   System Health: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("   🎉 All systems operational!")
        elif passed >= total * 0.8:
            print("   ⚠️  System mostly functional with minor issues")
        else:
            print("   🚨 System has significant issues")
        
        input("\nPress Enter to continue...")
    
    async def detailed_battle(self):
        """Battle with full detailed logging"""
        print("\n📝 DETAILED BATTLE SIMULATION")
        print("-" * 30)
        
        pokemon1_name = input("Enter first Pokemon: ").strip()
        pokemon2_name = input("Enter second Pokemon: ").strip()
        
        if not pokemon1_name or not pokemon2_name:
            return
            
        # Get Pokemon
        pokemon1 = await self.pokemon_client.get_pokemon(pokemon1_name)
        pokemon2 = await self.pokemon_client.get_pokemon(pokemon2_name)
        
        if not pokemon1 or not pokemon2:
            print("❌ One or both Pokemon not found")
            return
            
        print(f"\n📝 DETAILED BATTLE LOG")
        print("=" * 50)
        
        # Pre-battle analysis
        print(f"🔍 PRE-BATTLE ANALYSIS:")
        print(f"   {pokemon1.name.title()}: {' + '.join(pokemon1.types).title()} type")
        print(f"   {pokemon2.name.title()}: {' + '.join(pokemon2.types).title()} type")
        
        # Type effectiveness preview
        from pokemon_mcp.battle.mechanics import get_type_effectiveness
        p1_vs_p2 = get_type_effectiveness(pokemon1.types[0], pokemon2.types)
        p2_vs_p1 = get_type_effectiveness(pokemon2.types[0], pokemon1.types)
        
        print(f"   Type Matchup: {pokemon1.name} → {pokemon2.name}: {p1_vs_p2}x effectiveness")
        print(f"   Type Matchup: {pokemon2.name} → {pokemon1.name}: {p2_vs_p1}x effectiveness")
        
        # Simulate battle
        result = self.battle_engine.simulate_battle(pokemon1, pokemon2)
        
        print(f"\n⚔️ BATTLE COMMENCES!")
        print("-" * 30)
        
        # Show every single log entry
        for log in result.logs:
            print(f"Turn {log.turn:2d}: {log.message}")
        
        print(f"\n🏆 FINAL RESULT:")
        print(f"   🥇 Champion: {result.winner.title()}")
        print(f"   🥈 Runner-up: {result.loser.title()}")
        print(f"   ⏱️  Battle Duration: {result.total_turns} turns")
        print(f"   📊 Total Events: {len(result.logs)} log entries")
        
        input("\nPress Enter to continue...")
    
    async def _test_battle_engine(self):
        """Test battle engine functionality"""
        try:
            # Quick test battle
            pokemon1 = await self.pokemon_client.get_pokemon("pikachu")
            pokemon2 = await self.pokemon_client.get_pokemon("charizard")
            
            if not pokemon1 or not pokemon2:
                return False
                
            result = self.battle_engine.simulate_battle(pokemon1, pokemon2)
            return result.winner and result.total_turns > 0
        except:
            return False
    
    async def _test_evolution_system(self):
        """Test evolution system functionality"""
        try:
            tree = await self.evolution_client.get_evolution_tree("pikachu")
            return tree and 'chain_id' in tree
        except:
            return False
    
    async def cleanup(self):
        """Cleanup resources"""
        try:
            await self.pokemon_client.close()
        except:
            pass

async def main():
    """Main entry point"""
    print("🎮 Starting Pokemon MCP Server Demo CLI...")
    
    cli = PokemonCLI()
    try:
        await cli.main_menu()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"💥 Fatal error: {e}")
    finally:
        await cli.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
