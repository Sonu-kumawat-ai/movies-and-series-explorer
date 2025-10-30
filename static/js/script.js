// Genre selection management
let selectedGenres = [];

const genreSelect = document.getElementById('genre');
const selectedGenresDisplay = document.getElementById('selectedGenresDisplay');
const genreDisplayBox = document.getElementById('genreDisplayBox');

// Prevent dropdown from opening when clicking on tags
genreDisplayBox.addEventListener('click', function(e) {
    if (e.target.classList.contains('remove-btn') || e.target.closest('.genre-tag')) {
        e.preventDefault();
        e.stopPropagation();
    }
});

// Handle genre selection
genreSelect.addEventListener('change', function() {
    const selectedValue = this.value;
    const selectedText = this.options[this.selectedIndex].text;
    
    if (!selectedValue) return; // Empty selection
    
    // If "Any" is selected, clear all other selections
    if (selectedValue === 'any') {
        selectedGenres = ['any'];
        renderGenreTags();
        this.value = ''; // Reset dropdown
        return;
    }
    
    // Remove "Any" if other genre is selected
    selectedGenres = selectedGenres.filter(g => g !== 'any');
    
    // Add genre if not already selected
    if (!selectedGenres.includes(selectedValue)) {
        selectedGenres.push(selectedValue);
        renderGenreTags();
    }
    
    // Reset dropdown to default
    this.value = '';
});

// Render genre tags inside the display box
function renderGenreTags() {
    selectedGenresDisplay.innerHTML = '';
    
    if (selectedGenres.length === 0) {
        // Show placeholder if no genres selected
        selectedGenresDisplay.innerHTML = '<span class="placeholder-text">Select genres...</span>';
    } else {
        // Show selected genres as tags
        selectedGenres.forEach(genre => {
            const tag = document.createElement('div');
            tag.className = 'genre-tag';
            
            // Get the display text for the genre
            const option = Array.from(genreSelect.options).find(opt => opt.value === genre);
            const displayText = option ? option.text : genre;
            
            tag.innerHTML = `
                <span>${displayText}</span>
                <span class="remove-btn" data-genre="${genre}">✕</span>
            `;
            
            selectedGenresDisplay.appendChild(tag);
        });
        
        // Add click handlers to all remove buttons after rendering
        selectedGenresDisplay.querySelectorAll('.remove-btn').forEach(btn => {
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                removeGenre(this.getAttribute('data-genre'));
            });
        });
    }
}

// Remove a genre
function removeGenre(genre) {
    selectedGenres = selectedGenres.filter(g => g !== genre);
    renderGenreTags();
}
function removeGenre(genre) {
    selectedGenres = selectedGenres.filter(g => g !== genre);
    renderGenreTags();
}

// Form submission handler
document.getElementById('recommendationForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // Get form values
    const formData = {
        contentType: document.getElementById('contentType').value,
        genre: selectedGenres.length > 0 ? selectedGenres.join(', ') : 'any',
        language: document.getElementById('language').value,
        country: document.getElementById('country').value,
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
        
        // Create language and dubbed info
        let languageInfoHtml = '';
        if (rec.original_language) {
            const dubbedBadge = rec.is_dubbed ? '<span class="dubbed-badge">🎙️ Dubbed</span>' : '';
            languageInfoHtml = `
                <div class="language-info">
                    <span class="original-language">🌐 ${rec.original_language}</span>
                    ${dubbedBadge}
                </div>
            `;
        }
        
        // Create genre info
        let genreInfoHtml = '';
        if (rec.main_genre) {
            const subGenreDisplay = rec.sub_genre ? `<span class="sub-genre">📂 ${rec.sub_genre}</span>` : '';
            genreInfoHtml = `
                <div class="genre-info">
                    <span class="main-genre">🎬 ${rec.main_genre}</span>
                    ${subGenreDisplay}
                </div>
            `;
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
                ${languageInfoHtml}
                ${genreInfoHtml}
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
