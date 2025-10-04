// Form submission handler
document.getElementById('recommendationForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // Get form values
    const formData = {
        contentType: document.getElementById('contentType').value,
        genre: document.getElementById('genre').value,
        language: document.getElementById('language').value,
        format: document.getElementById('format').value,
        ottPlatform: document.getElementById('ottPlatform').value,
        fromYear: document.getElementById('fromYear').value
    };
    
    // Validate year
    const currentYear = new Date().getFullYear();
    if (parseInt(formData.fromYear) > currentYear) {
        showError(`From Year cannot be greater than ${currentYear}`);
        return;
    }
    
    // Show loading state
    showLoading(true);
    hideResults();
    hideError();
    
    try {
        // Make API call to Flask backend
        const response = await fetch('/get-recommendations', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayRecommendations(data.recommendations);
        } else {
            showError(data.error || 'Something went wrong. Please try again later.');
        }
    } catch (error) {
        showError('Something went wrong. Please try again later.');
        console.error('Error:', error);
    } finally {
        showLoading(false);
    }
});

// Display recommendations
function displayRecommendations(recommendations) {
    const resultsSection = document.getElementById('resultsSection');
    const recommendationsList = document.getElementById('recommendationsList');
    
    // Clear previous results
    recommendationsList.innerHTML = '';
    
    // Create recommendation cards
    recommendations.forEach((rec, index) => {
        const card = document.createElement('div');
        card.className = 'recommendation-card';
        card.style.animationDelay = `${index * 0.1}s`;
        
        // Handle poster image with placeholder
        let posterHtml = '';
        if (rec.poster && rec.poster !== 'N/A') {
            posterHtml = `<img src="${rec.poster}" alt="${rec.title} poster" class="movie-poster" onerror="this.src='data:image/svg+xml,%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 width=%27300%27 height=%27450%27%3E%3Crect width=%27300%27 height=%27450%27 fill=%27%23222%27/%3E%3Ctext x=%2750%25%27 y=%2750%25%27 dominant-baseline=%27middle%27 text-anchor=%27middle%27 font-family=%27Arial%27 font-size=%2724%27 fill=%27%23ffd700%27%3E${encodeURIComponent(rec.title)}%3C/text%3E%3C/svg%3E'">`;
        } else {
            // Create a placeholder with movie title
            posterHtml = `<div class="movie-poster-placeholder">
                <div class="placeholder-icon">🎬</div>
                <div class="placeholder-title">${rec.title}</div>
            </div>`;
        }
        
        // Create title HTML with or without IMDb link
        let titleHtml = '';
        if (rec.imdb_id && rec.imdb_id !== 'N/A') {
            titleHtml = `<a href="https://www.imdb.com/title/${rec.imdb_id}/" target="_blank" rel="noopener noreferrer" class="movie-title-link">${rec.title}</a>`;
        } else {
            titleHtml = rec.title;
        }
        
        card.innerHTML = `
            ${posterHtml}
            <div class="card-content">
                <h3>
                    <span class="number">${index + 1}</span>
                    ${titleHtml}
                    <span class="year">${rec.year}</span>
                </h3>
                <div class="rating">
                    <span class="imdb-icon">⭐</span>
                    <span class="imdb-score">${rec.imdb}</span>
                    <span class="imdb-text">IMDb</span>
                </div>
                <p class="reason">${rec.summary}</p>
            </div>
        `;
        
        recommendationsList.appendChild(card);
    });
    
    // Show results section
    resultsSection.style.display = 'block';
    
    // Smooth scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Show loading state
function showLoading(isLoading) {
    const submitBtn = document.getElementById('submitBtn');
    const btnText = submitBtn.querySelector('.btn-text');
    const btnLoader = submitBtn.querySelector('.btn-loader');
    
    if (isLoading) {
        submitBtn.disabled = true;
        btnText.style.display = 'none';
        btnLoader.style.display = 'inline-flex';
    } else {
        submitBtn.disabled = false;
        btnText.style.display = 'inline';
        btnLoader.style.display = 'none';
    }
}

// Show error message
function showError(message, errorType = 'general') {
    const errorSection = document.getElementById('errorSection');
    const errorTitle = document.getElementById('errorTitle');
    const errorMessage = document.getElementById('errorMessage');
    
    // Set appropriate title based on error type
    if (message.includes("API limit") || message.includes("😔")) {
        errorTitle.textContent = "😔 API Limit Reached";
    } else {
        errorTitle.textContent = "⚠️ Oops!";
    }
    
    errorMessage.textContent = message;
    errorSection.style.display = 'block';
    
    // Smooth scroll to error
    errorSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Hide error message
function hideError() {
    const errorSection = document.getElementById('errorSection');
    errorSection.style.display = 'none';
}

// Hide results
function hideResults() {
    const resultsSection = document.getElementById('resultsSection');
    resultsSection.style.display = 'none';
}

// Add animation to cards
const style = document.createElement('style');
style.textContent = `
    .recommendation-card {
        animation: slideIn 0.5s ease-out forwards;
        opacity: 0;
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
`;
document.head.appendChild(style);
