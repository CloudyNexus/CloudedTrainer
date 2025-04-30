// CloudedTrainer - Trainer management JavaScript

// Initialize the trainer management when the DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('Trainer manager initialized');
    
    // Setup cheat toggle switches
    setupCheatToggles();
    
    // Setup polling for game status
    setupGameStatusPolling();
});

// Setup the cheat toggle switches
function setupCheatToggles() {
    const cheatSwitches = document.querySelectorAll('.cheat-toggle');
    
    cheatSwitches.forEach(switchEl => {
        switchEl.addEventListener('change', function() {
            const gameName = this.getAttribute('data-game-name');
            const cheatId = this.getAttribute('data-cheat-id');
            const active = this.checked;
            
            // Show loading spinner
            toggleLoadingSpinner(true);
            
            // Send request to toggle the cheat
            toggleCheat(gameName, cheatId, active);
        });
    });
}

// Toggle a cheat on or off
function toggleCheat(gameName, cheatId, active) {
    // Create form data
    const formData = new FormData();
    formData.append('game_name', gameName);
    formData.append('cheat_id', cheatId);
    formData.append('active', active.toString());
    
    // Send request to the server
    fetch('/activate_cheat', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        // Hide loading spinner
        toggleLoadingSpinner(false);
        
        // Show result toast
        const messageType = data.status === 'success' ? 'success' : 'danger';
        showToast(data.message, messageType);
        
        // If there was an error, reset the toggle switch
        if (data.status !== 'success') {
            const switchEl = document.querySelector(`.cheat-toggle[data-cheat-id="${cheatId}"]`);
            if (switchEl) {
                switchEl.checked = !active;
            }
        }
    })
    .catch(error => {
        // Hide loading spinner
        toggleLoadingSpinner(false);
        
        // Show error toast
        console.error('Error toggling cheat:', error);
        showToast('Error toggling cheat. Please try again.', 'danger');
        
        // Reset the toggle switch
        const switchEl = document.querySelector(`.cheat-toggle[data-cheat-id="${cheatId}"]`);
        if (switchEl) {
            switchEl.checked = !active;
        }
    });
}

// Setup polling to check if the game is still running
function setupGameStatusPolling() {
    const gameStatusElement = document.getElementById('game-status');
    const gameName = gameStatusElement ? gameStatusElement.getAttribute('data-game-name') : null;
    
    if (!gameName) return;
    
    // Poll every 5 seconds
    setInterval(() => {
        fetch(`/game/${encodeURIComponent(gameName)}?check_status=1`)
            .then(response => response.json())
            .then(data => {
                // Update game status
                if (data.is_running) {
                    gameStatusElement.innerHTML = '<span class="badge bg-success">Running</span>';
                    
                    // Enable all cheat toggles
                    document.querySelectorAll('.cheat-toggle').forEach(toggle => {
                        toggle.disabled = false;
                    });
                } else {
                    gameStatusElement.innerHTML = '<span class="badge bg-danger">Not Running</span>';
                    
                    // Disable all cheat toggles
                    document.querySelectorAll('.cheat-toggle').forEach(toggle => {
                        toggle.disabled = true;
                        
                        // Also uncheck them since cheats can't be active if game isn't running
                        toggle.checked = false;
                    });
                    
                    // Show toast notification if game was previously running
                    if (gameStatusElement.getAttribute('data-was-running') === 'true') {
                        showToast('Game has stopped running. Cheats have been deactivated.', 'warning');
                    }
                }
                
                // Update the was-running attribute
                gameStatusElement.setAttribute('data-was-running', data.is_running.toString());
            })
            .catch(error => {
                console.error('Error checking game status:', error);
            });
    }, 5000);
}

// Launch the game
function launchGame(gameName, launchPath) {
    if (!launchPath) {
        showToast('Launch path not available', 'danger');
        return;
    }
    
    // Show loading spinner
    toggleLoadingSpinner(true);
    
    // Create form data
    const formData = new FormData();
    formData.append('game_name', gameName);
    formData.append('launch_path', launchPath);
    
    // Send request to launch the game
    fetch('/launch_game', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        // Hide loading spinner
        toggleLoadingSpinner(false);
        
        // Show result toast
        const messageType = data.status === 'success' ? 'success' : 'danger';
        showToast(data.message, messageType);
        
        // Refresh game status if successful
        if (data.status === 'success') {
            setTimeout(() => {
                window.location.reload();
            }, 2000);
        }
    })
    .catch(error => {
        // Hide loading spinner
        toggleLoadingSpinner(false);
        
        // Show error toast
        console.error('Error launching game:', error);
        showToast('Error launching game. Please try again.', 'danger');
    });
}

// Memory scanner functionality
function scanMemory(gameId) {
    // Show scan modal
    const scanModal = new bootstrap.Modal(document.getElementById('scanModal'));
    scanModal.show();
    
    // Reset scan form
    document.getElementById('scan-form').reset();
    
    // Setup form submission
    document.getElementById('scan-form').addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Get scan parameters
        const valueType = document.getElementById('value-type').value;
        const scanType = document.getElementById('scan-type').value;
        const scanValue = document.getElementById('scan-value').value;
        
        // Show loading status
        document.getElementById('scan-results').innerHTML = '<div class="text-center"><div class="spinner-border" role="status"><span class="visually-hidden">Loading...</span></div><p class="mt-2">Scanning memory...</p></div>';
        
        // Simulate scan results (in a real implementation, this would call an endpoint)
        setTimeout(() => {
            // Display dummy results (in a real app, this would show actual scan results)
            document.getElementById('scan-results').innerHTML = `
                <div class="alert alert-info">
                    Memory scanning is a premium feature. Upgrade to unlock this functionality.
                </div>
            `;
        }, 1500);
    });
}

// Update trainer settings
function saveTrainerSettings() {
    // Gather general settings
    const settings = {
        auto_refresh: document.getElementById('setting-auto-refresh').checked,
        start_with_system: document.getElementById('setting-start-with-system').checked,
        check_updates: document.getElementById('setting-check-updates').checked,
        scan_frequency: parseInt(document.getElementById('setting-scan-frequency').value),
        theme: document.getElementById('setting-theme').value,
        
        // Advanced settings
        memory_scan_method: document.getElementById('setting-memory-scan-method').value,
        log_level: document.getElementById('setting-log-level').value,
        log_path: document.getElementById('setting-log-path').value
    };
    
    // Send settings to server
    fetch('/api/settings', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(settings)
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            showToast('Settings saved successfully', 'success');
        } else {
            showToast('Error saving settings: ' + data.message, 'danger');
        }
    })
    .catch(error => {
        console.error('Error saving settings:', error);
        showToast('Error saving settings. Please try again.', 'danger');
    });
}

// Load trainer settings
function loadTrainerSettings() {
    // Get settings from server
    fetch('/api/settings')
    .then(response => response.json())
    .then(settings => {
        // Update general settings UI
        if (document.getElementById('setting-auto-refresh')) {
            document.getElementById('setting-auto-refresh').checked = settings.auto_refresh || false;
        }
        
        if (document.getElementById('setting-start-with-system')) {
            document.getElementById('setting-start-with-system').checked = settings.start_with_system || false;
        }
        
        if (document.getElementById('setting-check-updates')) {
            document.getElementById('setting-check-updates').checked = settings.check_updates || false;
        }
        
        if (document.getElementById('setting-scan-frequency')) {
            document.getElementById('setting-scan-frequency').value = settings.scan_frequency || 30;
        }
        
        if (document.getElementById('setting-theme')) {
            document.getElementById('setting-theme').value = settings.theme || 'dark';
        }
        
        // Update advanced settings UI
        if (document.getElementById('setting-memory-scan-method')) {
            document.getElementById('setting-memory-scan-method').value = settings.memory_scan_method || 'ptrace';
        }
        
        if (document.getElementById('setting-log-level')) {
            document.getElementById('setting-log-level').value = settings.log_level || 'info';
        }
        
        if (document.getElementById('setting-log-path')) {
            document.getElementById('setting-log-path').value = settings.log_path || '~/.cloudedtrainer/logs/';
        }
    })
    .catch(error => {
        console.error('Error loading settings:', error);
        showToast('Error loading settings. Using defaults.', 'warning');
    });
}
