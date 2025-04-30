// CloudedTrainer - Main JavaScript

// Initialize the application when the DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('CloudedTrainer initialized');
    
    // Setup game list refresh button
    const refreshButton = document.getElementById('refresh-games-btn');
    if (refreshButton) {
        refreshButton.addEventListener('click', function() {
            // Show loading spinner
            toggleLoadingSpinner(true);
            
            // Redirect to refresh endpoint
            window.location.href = '/refresh_games';
        });
    }
    
    // Setup game cards to be clickable
    const gameCards = document.querySelectorAll('.game-card');
    gameCards.forEach(card => {
        card.addEventListener('click', function() {
            const gameName = this.getAttribute('data-game-name');
            if (gameName) {
                window.location.href = `/game/${encodeURIComponent(gameName)}`;
            }
        });
    });
    
    // Dark mode toggle functionality
    const darkModeToggle = document.getElementById('dark-mode-toggle');
    if (darkModeToggle) {
        // Check if user has a preference stored
        const darkModePreference = localStorage.getItem('darkMode');
        
        // Set initial state based on preference or default to dark
        if (darkModePreference === 'light') {
            document.documentElement.setAttribute('data-bs-theme', 'light');
            darkModeToggle.checked = false;
        } else {
            document.documentElement.setAttribute('data-bs-theme', 'dark');
            darkModeToggle.checked = true;
        }
        
        // Toggle dark mode when the switch is clicked
        darkModeToggle.addEventListener('change', function() {
            if (this.checked) {
                document.documentElement.setAttribute('data-bs-theme', 'dark');
                localStorage.setItem('darkMode', 'dark');
            } else {
                document.documentElement.setAttribute('data-bs-theme', 'light');
                localStorage.setItem('darkMode', 'light');
            }
        });
    }
    
    // Setup tooltips
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
    
    // Hide alerts after 5 seconds
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert-dismissible');
        alerts.forEach(alert => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
});

// Toggle loading spinner
function toggleLoadingSpinner(show) {
    const spinner = document.getElementById('loading-spinner');
    if (spinner) {
        spinner.style.display = show ? 'flex' : 'none';
    }
}

// Filter games in the list
function filterGames() {
    const searchInput = document.getElementById('game-search');
    const filter = searchInput.value.toLowerCase();
    const gameCards = document.querySelectorAll('.game-card');
    
    gameCards.forEach(card => {
        const gameName = card.getAttribute('data-game-name').toLowerCase();
        if (gameName.includes(filter)) {
            card.style.display = '';
        } else {
            card.style.display = 'none';
        }
    });
    
    // Show or hide "no games found" message
    const noGamesFound = document.getElementById('no-games-found');
    if (noGamesFound) {
        let visibleCount = 0;
        gameCards.forEach(card => {
            if (card.style.display !== 'none') {
                visibleCount++;
            }
        });
        
        noGamesFound.style.display = visibleCount ? 'none' : 'block';
    }
}

// Show confirmation dialog
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// Show toast notification
function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toast-container');
    if (!toastContainer) return;
    
    // Create a new toast element
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    // Initialize and show the toast
    const bsToast = new bootstrap.Toast(toast, {
        autohide: true,
        delay: 3000
    });
    bsToast.show();
    
    // Remove the toast from the DOM after it's hidden
    toast.addEventListener('hidden.bs.toast', function() {
        toastContainer.removeChild(toast);
    });
}

// Handle tab switching
function switchTab(event, tabId) {
    event.preventDefault();
    
    // Hide all tab contents
    const tabContents = document.querySelectorAll('.tab-content');
    tabContents.forEach(content => {
        content.style.display = 'none';
    });
    
    // Deactivate all tabs
    const tabs = document.querySelectorAll('.nav-link');
    tabs.forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Show the selected tab content
    document.getElementById(tabId).style.display = 'block';
    
    // Activate the current tab
    event.target.classList.add('active');
}
