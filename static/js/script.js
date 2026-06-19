// Game functionality
document.addEventListener('DOMContentLoaded', function() {
    console.log('Palm Catch Game loaded successfully!');
    
    // Add smooth scrolling for navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });
});

// Game reset function
function resetGame() {
    fetch('/reset_game')
        .then(response => {
            if (response.ok) {
                showNotification('Game reset successfully!', 'success');
            } else {
                showNotification('Failed to reset game', 'error');
            }
        })
        .catch(error => {
            console.error('Error resetting game:', error);
            showNotification('Error resetting game', 'error');
        });
}

// Notification system
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 80px; right: 20px; z-index: 1050; min-width: 300px;';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto remove after 3 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 3000);
}

// Keyboard shortcuts
document.addEventListener('keydown', function(event) {
    // R key to reset game (when not focused on input fields)
    if ((event.key === 'r' || event.key === 'R') && 
        !event.target.matches('input, textarea, select')) {
        event.preventDefault();
        resetGame();
    }
});