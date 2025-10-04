import os
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import json
import requests
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
OMDB_API_KEY = os.getenv('OMDB_API_KEY')

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

genai.configure(api_key=GEMINI_API_KEY)

# Initialize Flask app
app = Flask(__name__)

# For Vercel deployment
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

def get_movie_details_from_omdb(title, year=None):
    """Fetch movie/series details from OMDB API including poster and IMDb rating"""
    if not OMDB_API_KEY:
        return None
    
    try:
        # Remove any season information from the title for better matching
        base_title = re.sub(r'\s*[-–(]?\s*(?:Season|S)\s*\d+.*$', '', title, flags=re.IGNORECASE).strip()
        
        # Try 1: Search with year if provided
        if year:
            params = {
                'apikey': OMDB_API_KEY,
                't': title,
                'y': year,
                'plot': 'short'
            }
            response = requests.get('http://www.omdbapi.com/', params=params, timeout=5)
            data = response.json()
            
            if data.get('Response') == 'True':
                return {
                    'poster': data.get('Poster', 'N/A'),
                    'imdb_rating': data.get('imdbRating', 'N/A'),
                    'plot': data.get('Plot', 'N/A'),
                    'imdb_id': data.get('imdbID', 'N/A')
                }
        
        # Try 2: Search without year
        params = {
            'apikey': OMDB_API_KEY,
            't': title,
            'plot': 'short'
        }
        response = requests.get('http://www.omdbapi.com/', params=params, timeout=5)
        data = response.json()
        
        if data.get('Response') == 'True':
            return {
                'poster': data.get('Poster', 'N/A'),
                'imdb_rating': data.get('imdbRating', 'N/A'),
                'plot': data.get('Plot', 'N/A'),
                'imdb_id': data.get('imdbID', 'N/A')
            }
        
        # Try 3: Use base title for web series (without season info)
        if base_title != title:
            params = {
                'apikey': OMDB_API_KEY,
                't': base_title,
                'type': 'series',
                'plot': 'short'
            }
            response = requests.get('http://www.omdbapi.com/', params=params, timeout=5)
            data = response.json()
            
            if data.get('Response') == 'True':
                return {
                    'poster': data.get('Poster', 'N/A'),
                    'imdb_rating': data.get('imdbRating', 'N/A'),
                    'plot': data.get('Plot', 'N/A'),
                    'imdb_id': data.get('imdbID', 'N/A')
                }
        
        # Try 4: Search API to find closest match
        search_params = {
            'apikey': OMDB_API_KEY,
            's': base_title,
            'plot': 'short'
        }
        search_response = requests.get('http://www.omdbapi.com/', params=search_params, timeout=5)
        search_data = search_response.json()
        
        if search_data.get('Response') == 'True' and search_data.get('Search'):
            first_result = search_data['Search'][0]
            imdb_id = first_result.get('imdbID')
            
            if imdb_id:
                detail_params = {
                    'apikey': OMDB_API_KEY,
                    'i': imdb_id,
                    'plot': 'short'
                }
                detail_response = requests.get('http://www.omdbapi.com/', params=detail_params, timeout=5)
                detail_data = detail_response.json()
                
                if detail_data.get('Response') == 'True':
                    return {
                        'poster': detail_data.get('Poster', 'N/A'),
                        'imdb_rating': detail_data.get('imdbRating', 'N/A'),
                        'plot': detail_data.get('Plot', 'N/A'),
                        'imdb_id': detail_data.get('imdbID', 'N/A')
                    }
        
        return None
        
    except Exception as e:
        print(f"Error fetching from OMDB: {str(e)}")
        return None

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/get-recommendations', methods=['POST'])
def get_recommendations():
    """Get movie/series recommendations from Gemini API"""
    try:
        user_selections = request.json
        
        # Create the prompt using the user's selections
        content_type = user_selections.get('contentType', 'any')
        
        # Build strict content type instruction
        if content_type == 'movies':
            content_instruction = "CRITICAL: Recommend ONLY movies (feature films). Do NOT recommend web series, TV shows, or episodic content."
        elif content_type == 'web series':
            content_instruction = "CRITICAL: Recommend ONLY web series or TV shows (episodic content). Do NOT recommend movies or feature films."
        else:
            content_instruction = "You may recommend both movies and web series."
        
        # Get the from year
        from_year = user_selections.get('fromYear', '1950')
        
        prompt = f"""
You are a world-class movie and web series recommendation engine. Your task is to provide exactly 6 recommendations based on the user's specific criteria.

**CRITICAL INSTRUCTION #1 - Content Type (NON-NEGOTIABLE):**
{content_instruction}

**CRITICAL INSTRUCTION #2 - Only Existing Content:**
Only recommend content that has ACTUALLY been released and exists. Do NOT recommend upcoming, unreleased, or hypothetical content. Verify the content exists before recommending it. If you're not certain about a 2025 release, recommend something from 2024 or earlier that you know exists.

**CRITICAL INSTRUCTION #3 - Well-Known Titles:**
Prioritize well-known, popular, and widely-recognized titles that are more likely to be found in movie databases.

**User Criteria:**
- **I want to watch:** {user_selections.get('contentType', 'any')}
- **Preferred Genre:** {user_selections.get('genre', 'any')}
- **Language:** {user_selections.get('language', 'any')}
- **Format:** {user_selections.get('format', 'any')}
- **OTT Platform:** {user_selections.get('ottPlatform', 'Any Platform')}
- **Release Year Range:** From {from_year} to 2025

**Instructions:**
1. Adhere strictly to all the user's criteria. If a filter is set to 'any', you have creative freedom for that category.
2. Provide your response as a single, minified JSON array of objects.
3. Do NOT include any explanatory text, greetings, or markdown formatting (like ```json) before or after the JSON array. Your entire output must be only the JSON data itself.
4. Each object in the array must have the following four keys exactly: "title", "year", "imdb", and "summary".
5. For web series/TV shows, recommend the SERIES NAME ONLY without mentioning specific seasons (e.g., "Breaking Bad" not "Breaking Bad Season 5").
6. The "imdb" value should be the actual IMDb rating (use real ratings only from the IMDb database, formatted as a number like 8.5).
7. The "summary" value should be a concise plot summary (2-3 sentences, under 50 words) describing what the movie/series is about.

**Example Output Format (DO NOT include this text, only output the JSON):**
[{{"title":"Movie Name","year":2023,"imdb":"8.5","summary":"Brief plot description here."}},{{"title":"Another Title","year":2022,"imdb":"7.8","summary":"Another brief plot here."}}]
"""
        
        # Initialize Gemini model
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Generate recommendations
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Remove markdown code blocks if present
        if response_text.startswith('```'):
            response_text = response_text.split('```')[1]
            if response_text.startswith('json'):
                response_text = response_text[4:]
            response_text = response_text.strip()
        
        # Parse JSON response
        recommendations = json.loads(response_text)
        
        # Enhance each recommendation with OMDB data
        enhanced_recommendations = []
        for rec in recommendations:
            title = rec.get('title', '')
            year = rec.get('year', '')
            
            # Get OMDB details
            omdb_data = get_movie_details_from_omdb(title, year)
            
            if omdb_data:
                rec['poster'] = omdb_data['poster']
                rec['imdb_id'] = omdb_data['imdb_id']
                # Use OMDB rating if available and valid, otherwise keep Gemini's rating
                if omdb_data['imdb_rating'] != 'N/A' and omdb_data['imdb_rating'] != 'N/A':
                    rec['imdb'] = omdb_data['imdb_rating']
            else:
                rec['poster'] = 'N/A'
                rec['imdb_id'] = 'N/A'
            
            enhanced_recommendations.append(rec)
        
        return jsonify(enhanced_recommendations)
    
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {str(e)}")
        return jsonify({'error': 'Something went wrong. Please try again later.'}), 500
    
    except Exception as e:
        error_message = str(e).lower()
        print(f"Error: {error_message}")
        
        # Check if it's an API limit error
        if any(keyword in error_message for keyword in ['quota', 'limit', 'rate limit', 'resource exhausted', '429', 'too many requests']):
            return jsonify({'error': 'Sorry 😔 We\'ve reached the API limit for today. Please wait before trying again.'}), 429
        
        return jsonify({'error': 'Something went wrong. Please try again later.'}), 500

# For Vercel
if __name__ == '__main__':
    app.run(debug=False)