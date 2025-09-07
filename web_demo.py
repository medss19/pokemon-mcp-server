# web_demo.py
"""
Simple Pokemon MCP Server Web Demo - DEVELOPMENT ONLY
A lightweight Flask app to demonstrate Pokemon features
NOTE: This is NOT how MCP works in production - it's for testing only
"""
import asyncio
import sys
from pathlib import Path
from flask import Flask, render_template_string, request, jsonify

# Add the src directory to the path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from pokemon_mcp.data.pokemon_client import PokemonClient
from pokemon_mcp.battle.engine import BattleEngine

app = Flask(__name__)

# Initialize clients
pokemon_client = PokemonClient()
battle_engine = BattleEngine()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Pokemon MCP Server Demo</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; background: #f0f0f0; }
        .header { text-align: center; background: #4CAF50; color: white; padding: 20px; border-radius: 10px; margin-bottom: 30px; }
        .section { background: white; padding: 20px; margin: 20px 0; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .form-group { margin: 15px 0; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input { width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 5px; }
        button { background: #4CAF50; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin: 10px 5px; }
        button:hover { background: #45a049; }
        .result { margin-top: 20px; padding: 15px; border-radius: 5px; }
        .success { background: #d4edda; border: 1px solid #c3e6cb; color: #155724; }
        .error { background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; }
        .pokemon-info { display: grid; grid-template-columns: 1fr 2fr; gap: 20px; margin: 15px 0; }
        .stats { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
        .stat { background: #f8f9fa; padding: 8px; border-radius: 5px; }
        .battle-log { max-height: 300px; overflow-y: auto; background: #f8f9fa; padding: 15px; border-radius: 5px; }
        .log-entry { margin: 3px 0; padding: 3px; }
        .turn-header { background: #e3f2fd; font-weight: bold; padding: 5px; border-radius: 3px; }
        .warning { background: #fff3cd; border: 1px solid #ffeaa7; color: #856404; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
        @media (max-width: 768px) { .pokemon-info, .stats { grid-template-columns: 1fr; } }
    </style>
</head>
<body>
    <div class="warning">
        <strong>⚠️ Development Demo Only</strong><br>
        This web interface is for testing purposes. In production, this MCP server communicates with LLMs via stdin/stdout protocol.
        Real usage: LLM → MCP Client → This Server → Pokemon Data
    </div>

    <div class="header">
        <h1>🎮 Pokemon MCP Server Demo</h1>
        <p>Testing Pokemon Data & Battle Simulation Features</p>
    </div>

    <div class="section">
        <h2>🔍 Pokemon Lookup</h2>
        <div class="form-group">
            <label>Pokemon Name or ID:</label>
            <input type="text" id="pokemon-name" placeholder="e.g., pikachu, charizard, 25">
        </div>
        <button onclick="searchPokemon()">Search Pokemon</button>
        <div id="pokemon-result"></div>
    </div>

    <div class="section">
        <h2>⚔️ Battle Simulator</h2>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
            <div class="form-group">
                <label>Pokemon 1:</label>
                <input type="text" id="pokemon1" placeholder="e.g., pikachu">
            </div>
            <div class="form-group">
                <label>Pokemon 2:</label>
                <input type="text" id="pokemon2" placeholder="e.g., charizard">
            </div>
        </div>
        <button onclick="simulateBattle()">Start Battle!</button>
        <div id="battle-result"></div>
    </div>

    <div class="section">
        <h2>🔄 Evolution Chain</h2>
        <div class="form-group">
            <label>Pokemon Name:</label>
            <input type="text" id="evolution-name" placeholder="e.g., bulbasaur, squirtle">
        </div>
        <button onclick="getEvolution()">Get Evolution Chain</button>
        <div id="evolution-result"></div>
    </div>

    <script>
        async function searchPokemon() {
            const name = document.getElementById('pokemon-name').value.trim();
            const result = document.getElementById('pokemon-result');
            
            if (!name) {
                result.innerHTML = '<div class="result error">Please enter a Pokemon name</div>';
                return;
            }
            
            result.innerHTML = '<div class="result">🔄 Loading...</div>';
            
            try {
                const response = await fetch(`/api/pokemon/${encodeURIComponent(name)}`);
                const data = await response.json();
                
                if (data.success) {
                    const p = data.pokemon;
                    result.innerHTML = `
                        <div class="result success">
                            <div class="pokemon-info">
                                <div>
                                    <img src="${p.sprite}" alt="${p.name}" style="width: 150px; height: 150px;">
                                    <h3>${p.name.charAt(0).toUpperCase() + p.name.slice(1)} #${p.id}</h3>
                                    <p><strong>Types:</strong> ${p.types.join(', ')}</p>
                                    <p><strong>Height:</strong> ${p.height} | <strong>Weight:</strong> ${p.weight}</p>
                                </div>
                                <div class="stats">
                                    <div class="stat"><strong>HP:</strong> ${p.stats.hp}</div>
                                    <div class="stat"><strong>Attack:</strong> ${p.stats.attack}</div>
                                    <div class="stat"><strong>Defense:</strong> ${p.stats.defense}</div>
                                    <div class="stat"><strong>Sp. Attack:</strong> ${p.stats.special_attack}</div>
                                    <div class="stat"><strong>Sp. Defense:</strong> ${p.stats.special_defense}</div>
                                    <div class="stat"><strong>Speed:</strong> ${p.stats.speed}</div>
                                </div>
                            </div>
                            <p><strong>Abilities:</strong> ${p.abilities.join(', ')}</p>
                            <p><strong>Sample Moves:</strong> ${p.moves.slice(0, 8).join(', ')}</p>
                        </div>
                    `;
                } else {
                    result.innerHTML = `<div class="result error">❌ ${data.error}</div>`;
                }
            } catch (error) {
                result.innerHTML = `<div class="result error">❌ Error: ${error.message}</div>`;
            }
        }

        async function simulateBattle() {
            const pokemon1 = document.getElementById('pokemon1').value.trim();
            const pokemon2 = document.getElementById('pokemon2').value.trim();
            const result = document.getElementById('battle-result');
            
            if (!pokemon1 || !pokemon2) {
                result.innerHTML = '<div class="result error">Please enter both Pokemon names</div>';
                return;
            }
            
            result.innerHTML = '<div class="result">⚔️ Simulating battle...</div>';
            
            try {
                const response = await fetch('/api/battle', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ pokemon1, pokemon2 })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    const b = data.battle;
                    result.innerHTML = `
                        <div class="result success">
                            <h3>🏆 Winner: ${b.winner.charAt(0).toUpperCase() + b.winner.slice(1)}</h3>
                            <p>💀 Defeated: ${b.loser.charAt(0).toUpperCase() + b.loser.slice(1)}</p>
                            <p>🕐 Battle lasted ${b.total_turns} turns</p>
                            <h4>📜 Battle Log:</h4>
                            <div class="battle-log">
                                ${b.logs.map(log => `
                                    <div class="log-entry ${log.message.includes('Turn') ? 'turn-header' : ''}">
                                        ${log.message}
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    `;
                } else {
                    result.innerHTML = `<div class="result error">❌ ${data.error}</div>`;
                }
            } catch (error) {
                result.innerHTML = `<div class="result error">❌ Error: ${error.message}</div>`;
            }
        }

        async function getEvolution() {
            const name = document.getElementById('evolution-name').value.trim();
            const result = document.getElementById('evolution-result');
            
            if (!name) {
                result.innerHTML = '<div class="result error">Please enter a Pokemon name</div>';
                return;
            }
            
            result.innerHTML = '<div class="result">🔄 Loading evolution data...</div>';
            
            try {
                const response = await fetch(`/api/evolution/${encodeURIComponent(name)}`);
                const data = await response.json();
                
                if (data.success) {
                    const chain = data.evolution.evolution_chain;
                    result.innerHTML = `
                        <div class="result success">
                            <h3>🔄 Evolution Chain (${chain.length} stages)</h3>
                            <div style="display: flex; flex-wrap: wrap; gap: 15px;">
                                ${chain.map((pokemon, index) => `
                                    <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; text-align: center; min-width: 150px;">
                                        <h4>Stage ${index + 1}</h4>
                                        <strong>${pokemon.name.charAt(0).toUpperCase() + pokemon.name.slice(1)}</strong>
                                        ${pokemon.trigger ? `<br><small>Evolves via: ${pokemon.trigger}</small>` : ''}
                                        ${pokemon.min_level ? `<br><small>Level: ${pokemon.min_level}</small>` : ''}
                                        ${pokemon.item ? `<br><small>Item: ${pokemon.item}</small>` : ''}
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    `;
                } else {
                    result.innerHTML = `<div class="result error">❌ ${data.error}</div>`;
                }
            } catch (error) {
                result.innerHTML = `<div class="result error">❌ Error: ${error.message}</div>`;
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/pokemon/<name>')
def get_pokemon_api(name):
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
                    'moves': pokemon.moves,
                    'abilities': pokemon.abilities,
                    'sprite': pokemon.sprite_url,
                    'height': f"{pokemon.height/10}m",
                    'weight': f"{pokemon.weight/10}kg"
                }
            })
        else:
            return jsonify({'success': False, 'error': 'Pokemon not found. Please check spelling or try a different name.'})
    except Exception as e:
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'})

@app.route('/api/battle', methods=['POST'])
def battle_api():
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
        
        if not pokemon1:
            return jsonify({'success': False, 'error': f'Pokemon "{pokemon1_name}" not found. Please check spelling.'})
        if not pokemon2:
            return jsonify({'success': False, 'error': f'Pokemon "{pokemon2_name}" not found. Please check spelling.'})
        
        # Simulate battle (FIXED: Now properly async)
        result = loop.run_until_complete(battle_engine.simulate_battle(pokemon1, pokemon2))
        
        return jsonify({
            'success': True,
            'battle': {
                'winner': result.winner,
                'loser': result.loser,
                'total_turns': result.total_turns,
                'logs': [{'turn': log.turn, 'message': log.message} for log in result.logs]
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Battle simulation error: {str(e)}'})

@app.route('/api/evolution/<name>')
def evolution_api(name):
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Get Pokemon first
        pokemon = loop.run_until_complete(pokemon_client.get_pokemon(name.lower()))
        if not pokemon:
            return jsonify({'success': False, 'error': f'Pokemon "{name}" not found'})
            
        # Get evolution chain
        evolution_data = loop.run_until_complete(pokemon_client.get_evolution_chain(pokemon.species_url))
        
        return jsonify({
            'success': True,
            'evolution': evolution_data
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Evolution data error: {str(e)}'})

if __name__ == '__main__':
    print("🌟 Starting Pokemon MCP Server Web Demo...")
    print("⚠️  IMPORTANT: This is a DEVELOPMENT DEMO only!")
    print("📝 Real MCP servers communicate with LLMs via stdin/stdout")
    print("🎮 Features available:")
    print("   • Pokemon data lookup with comprehensive stats")
    print("   • Advanced battle simulation with detailed logs") 
    print("   • Evolution chain information")
    print("   • Clean, responsive web interface")
    print("\n🚀 Access the demo at: http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)