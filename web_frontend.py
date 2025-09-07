# web_frontend.py
import asyncio
import json
from flask import Flask, render_template, request, jsonify
from src.pokemon_mcp.data.pokemon_client import PokemonClient
from src.pokemon_mcp.battle.engine import BattleEngine
from src.pokemon_mcp.data.evolution import EvolutionClient

app = Flask(__name__)

# Global clients
pokemon_client = PokemonClient()
battle_engine = BattleEngine()
evolution_client = EvolutionClient()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/pokemon/<name>')
def get_pokemon_api(name):
    """Get Pokemon data"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        pokemon = loop.run_until_complete(pokemon_client.get_pokemon(name.lower()))
        
        if pokemon:
            return jsonify({
                'success': True,
                'pokemon': {
                    'name': pokemon.name,
                    'id': pokemon.id,
                    'types': pokemon.types,
                    'stats': {
                        'hp': pokemon.stats.hp,
                        'attack': pokemon.stats.attack,
                        'defense': pokemon.stats.defense,
                        'special_attack': pokemon.stats.special_attack,
                        'special_defense': pokemon.stats.special_defense,
                        'speed': pokemon.stats.speed
                    },
                    'moves': pokemon.moves[:8],  # Show first 8 moves
                    'sprite': pokemon.sprite_url
                }
            })
        else:
            return jsonify({'success': False, 'error': 'Pokemon not found'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/battle', methods=['POST'])
def battle_api():
    """Simulate a battle between two Pokemon"""
    try:
        data = request.json
        pokemon1_name = data.get('pokemon1')
        pokemon2_name = data.get('pokemon2')
        
        if not pokemon1_name or not pokemon2_name:
            return jsonify({'success': False, 'error': 'Both Pokemon names required'})
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Fetch Pokemon
        pokemon1 = loop.run_until_complete(pokemon_client.get_pokemon(pokemon1_name.lower()))
        pokemon2 = loop.run_until_complete(pokemon_client.get_pokemon(pokemon2_name.lower()))
        
        if not pokemon1 or not pokemon2:
            return jsonify({'success': False, 'error': 'One or both Pokemon not found'})
        
        # Simulate battle
        result = loop.run_until_complete(battle_engine.simulate_battle(pokemon1, pokemon2))
        
        # Format battle logs
        battle_logs = []
        for log in result.logs:
            battle_logs.append({
                'turn': log.turn,
                'message': log.message
            })
        
        return jsonify({
            'success': True,
            'battle': {
                'winner': result.winner,
                'loser': result.loser,
                'total_turns': result.total_turns,
                'logs': battle_logs
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/evolution/<name>')
def get_evolution_api(name):
    """Get Pokemon evolution data"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Get base Pokemon
        pokemon = loop.run_until_complete(pokemon_client.get_pokemon(name.lower()))
        if not pokemon:
            return jsonify({'success': False, 'error': 'Pokemon not found'})
        
        # Get evolution line
        evolution_line = loop.run_until_complete(evolution_client.get_evolution_line(pokemon.species_url))
        
        return jsonify({
            'success': True,
            'evolution': {
                'pokemon_name': pokemon.name,
                'evolution_line': evolution_line
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Test basic functionality
        pikachu = loop.run_until_complete(pokemon_client.get_pokemon("pikachu"))
        
        if pikachu:
            return jsonify({
                'success': True,
                'status': 'healthy',
                'api_connection': 'working',
                'test_pokemon': pikachu.name
            })
        else:
            return jsonify({'success': False, 'status': 'unhealthy', 'error': 'Cannot fetch test Pokemon'})
            
    except Exception as e:
        return jsonify({'success': False, 'status': 'unhealthy', 'error': str(e)})

if __name__ == '__main__':
    print("🌟 Starting Pokemon MCP Server Web Frontend...")
    print("📊 Features available:")
    print("   • Pokemon data lookup with stats and sprites")
    print("   • Advanced battle simulation with detailed logs") 
    print("   • Evolution chain analysis")
    print("   • Health monitoring")
    print("\n🚀 Access the frontend at: http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
