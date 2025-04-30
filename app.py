import os
import logging
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "cloudedtrainer_secret")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)  # needed for url_for to generate with https

# Import modules after app initialization to avoid circular imports
from game_scanner import GameScanner
from trainer_manager import TrainerManager
from storage_manager import StorageManager

# Initialize global objects
game_scanner = GameScanner()
trainer_manager = TrainerManager()
storage = StorageManager()

# Initialize default trainers if none exist
from trainers import get_all_trainers
trainer_list = []
for trainer in get_all_trainers():
    trainer_list.append({
        "name": trainer.name,
        "game_name": trainer.game_name,
        "description": trainer.description,
        "process_name": trainer.process_name,
    })
storage.initialize_default_trainers(trainer_list)

@app.route('/')
def index():
    installed_games = game_scanner.get_installed_games()
    running_games = game_scanner.get_running_games()
    
    # Merge with storage information
    games_with_trainers = []
    for game in installed_games:
        trainer = storage.get_trainer_by_game(game.get('name'))
        game['has_trainer'] = trainer is not None
        game['is_running'] = game.get('name') in [g.get('name') for g in running_games]
        games_with_trainers.append(game)
    
    return render_template('index.html', games=games_with_trainers)

@app.route('/game/<game_name>')
def game_detail(game_name):
    game_info = game_scanner.get_game_info(game_name)
    
    if not game_info:
        flash(f"Game {game_name} not found", "danger")
        return redirect(url_for('index'))
    
    trainer = storage.get_trainer_by_game(game_name)
    
    if not trainer:
        flash(f"No trainer available for {game_name}", "warning")
        return redirect(url_for('index'))
    
    # Get available cheats for this game
    available_cheats = trainer_manager.get_available_cheats(game_name)
    
    return render_template('game.html', 
                          game=game_info, 
                          trainer=trainer, 
                          cheats=available_cheats,
                          is_running=game_scanner.is_game_running(game_name))

@app.route('/activate_cheat', methods=['POST'])
def activate_cheat():
    game_name = request.form.get('game_name')
    cheat_id = request.form.get('cheat_id')
    active = request.form.get('active') == 'true'
    
    success = trainer_manager.toggle_cheat(game_name, cheat_id, active)
    
    if success:
        return jsonify({"status": "success", "message": f"Cheat {'activated' if active else 'deactivated'}"})
    else:
        return jsonify({"status": "error", "message": "Failed to toggle cheat. Make sure the game is running."})

@app.route('/refresh_games')
def refresh_games():
    game_scanner.refresh()
    flash("Game list refreshed", "success")
    return redirect(url_for('index'))

@app.route('/settings')
def settings():
    app_settings = storage.settings
    return render_template('settings.html', settings=app_settings)

@app.route('/api/settings', methods=['GET'])
def get_settings():
    return jsonify(storage.settings)

@app.route('/api/settings', methods=['POST'])
def update_settings():
    settings_data = request.get_json()
    if settings_data:
        storage.update_settings(settings_data)
        return jsonify({"status": "success", "message": "Settings updated successfully"})
    return jsonify({"status": "error", "message": "Invalid settings data"})

@app.route('/about')
def about():
    return render_template('about.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('base.html', error="404 - Page Not Found"), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('base.html', error="500 - Server Error"), 500

@app.context_processor
def inject_globals():
    return {
        'app_name': 'CloudedTrainer',
        'version': '0.1.0',
        'now': datetime.now
    }
