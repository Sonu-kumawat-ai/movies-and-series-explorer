from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import os
import json
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure Gemini API
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# OMDB API Key
OMDB_API_KEY = os.getenv('OMDB_API_KEY')

def get_movie_details_from_omdb(title, year):
    """Fetch movie/series details from OMDB API"""
    try:
        # Extract base series name if it contains season information
        base_title = title
        # Remove season patterns like "Season 1", "Season One", "S1", etc.
        import re
        season_patterns = [
            r'\s+Season\s+\d+',
            r'\s+Season\s+[IVX]+',
            r'\s+Season\s+\w+',
            r'\s+S\d+',
            r'\s+-\s+Season\s+\d+',
            r'\s+\(Season\s+\d+\)',
        ]
        for pattern in season_patterns:
            base_title = re.sub(pattern, '', base_title, flags=re.IGNORECASE)
        base_title = base_title.strip()
        
        # Try exact match first with original title
        url = f"http://www.omdbapi.com/?t={title}&y={year}&apikey={OMDB_API_KEY}"
        response = requests.get(url, timeout=5)
        data = response.json()
        
        if data.get('Response') == 'True':
            return {
                'poster': data.get('Poster', 'N/A'),
                'imdb_rating': data.get('imdbRating', 'N/A'),
                'imdb_id': data.get('imdbID', 'N/A'),
                'plot': data.get('Plot', 'N/A'),
                'director': data.get('Director', 'N/A'),
                'actors': data.get('Actors', 'N/A'),
                'runtime': data.get('Runtime', 'N/A')
            }
        
        # If original title fails and we extracted a base title, try with base title
        if base_title != title:
            url = f"http://www.omdbapi.com/?t={base_title}&y={year}&type=series&apikey={OMDB_API_KEY}"
            response = requests.get(url, timeout=5)
            data = response.json()
            
            if data.get('Response') == 'True':
                return {
                    'poster': data.get('Poster', 'N/A'),
                    'imdb_rating': data.get('imdbRating', 'N/A'),
                    'imdb_id': data.get('imdbID', 'N/A'),
                    'plot': data.get('Plot', 'N/A'),
                    'director': data.get('Director', 'N/A'),
                    'actors': data.get('Actors', 'N/A'),
                    'runtime': data.get('Runtime', 'N/A')
                }
        
        # If exact match fails, try without year
        url = f"http://www.omdbapi.com/?t={base_title}&apikey={OMDB_API_KEY}"
        response = requests.get(url, timeout=5)
        data = response.json()
        
        if data.get('Response') == 'True':
            return {
                'poster': data.get('Poster', 'N/A'),
                'imdb_rating': data.get('imdbRating', 'N/A'),
                'imdb_id': data.get('imdbID', 'N/A'),
                'plot': data.get('Plot', 'N/A'),
                'director': data.get('Director', 'N/A'),
                'actors': data.get('Actors', 'N/A'),
                'runtime': data.get('Runtime', 'N/A')
            }
        
        # If still not found, try search API
        url = f"http://www.omdbapi.com/?s={base_title}&apikey={OMDB_API_KEY}"
        response = requests.get(url, timeout=5)
        data = response.json()
        
        if data.get('Response') == 'True' and data.get('Search'):
            # Get the first result
            first_result = data['Search'][0]
            imdb_id = first_result.get('imdbID')
            
            # Fetch details using IMDb ID
            url = f"http://www.omdbapi.com/?i={imdb_id}&apikey={OMDB_API_KEY}"
            response = requests.get(url, timeout=5)
            data = response.json()
            
            if data.get('Response') == 'True':
                return {
                    'poster': data.get('Poster', 'N/A'),
                    'imdb_rating': data.get('imdbRating', 'N/A'),
                    'imdb_id': data.get('imdbID', 'N/A'),
                    'plot': data.get('Plot', 'N/A'),
                    'director': data.get('Director', 'N/A'),
                    'actors': data.get('Actors', 'N/A'),
                    'runtime': data.get('Runtime', 'N/A')
                }
        
        return None
    except Exception as e:
        print(f"Error fetching OMDB data for {title}: {str(e)}")
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
            content_instruction = "You may recommend either movies or web series."
        
        prompt = f"""
You are a world-class movie and web series recommendation engine. Your task is to provide exactly 6 recommendations based on the user's specific criteria.

**User Criteria:**
- **Content Type:** {content_type}
- **Preferred Genre:** {user_selections.get('genre', 'any')}
- **Language:** {user_selections.get('language', 'any')}
- **Format:** {user_selections.get('format', 'any')}
- **OTT Platform:** {user_selections.get('ottPlatform', 'Any Platform')}
- **Release Year Range:** From {user_selections.get('fromYear', '1950')} to 2025

**STRICT CONTENT TYPE RULE:**
{content_instruction}

**Instructions:**
1. STRICTLY adhere to the content type requirement above. This is NON-NEGOTIABLE.
2. CRITICAL: Only recommend content that has ACTUALLY been released and exists. Do NOT recommend upcoming, unreleased, or hypothetical content. Verify the content exists before recommending it.
3. IMPORTANT: Prioritize well-known, popular titles that are widely recognized and likely to be found in major movie databases (like IMDb/OMDB). Avoid obscure or very niche content.
4. Only recommend content released between {user_selections.get('fromYear', '1950')} and 2025. If you're not certain about a 2025 release, recommend something from 2024 that you know exists.
5. For web series/TV shows, recommend the SERIES NAME ONLY without mentioning specific seasons (e.g., "Breaking Bad" not "Breaking Bad Season 5"). Use the series' original release year.
6. Adhere strictly to all other user criteria. If a filter is set to 'any', you have creative freedom for that category.
7. Provide your response as a single, minified JSON array of objects.
8. Do NOT include any explanatory text, greetings, or markdown formatting (like ```json) before or after the JSON array. Your entire output must be only the JSON data itself.
9. Each object in the array must have the following four keys exactly: "title", "year", "imdb", and "summary".
10. The "imdb" value should be the actual IMDb rating from the IMDb database. Use real ratings only.
11. The "summary" value should be a concise plot summary (2-3 sentences, under 50 words) describing what the movie/series is about. Focus on the main premise and story.
12. Ensure all recommendations are currently available or were available on the specified OTT platform.
"""
        
        # Initialize the Gemini model (using gemini-2.0-flash-exp)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Generate recommendations
        response = model.generate_content(prompt)
        
        # Parse the response text as JSON
        recommendations_text = response.text.strip()
        
        # Remove markdown code blocks if present
        if recommendations_text.startswith('```'):
            recommendations_text = recommendations_text.split('```')[1]
            if recommendations_text.startswith('json'):
                recommendations_text = recommendations_text[4:]
            recommendations_text = recommendations_text.strip()
        
        recommendations = json.loads(recommendations_text)
        
        # Enhance recommendations with OMDB data
        enhanced_recommendations = []
        for rec in recommendations:
            omdb_data = get_movie_details_from_omdb(rec.get('title'), rec.get('year'))
            
            enhanced_rec = rec.copy()
            if omdb_data:
                # Use OMDB rating if available and valid
                if omdb_data['imdb_rating'] != 'N/A':
                    enhanced_rec['imdb'] = omdb_data['imdb_rating']
                
                # Add poster and additional info
                enhanced_rec['poster'] = omdb_data['poster']
                enhanced_rec['imdb_id'] = omdb_data['imdb_id']
                enhanced_rec['plot'] = omdb_data['plot']
                enhanced_rec['director'] = omdb_data['director']
                enhanced_rec['actors'] = omdb_data['actors']
                enhanced_rec['runtime'] = omdb_data['runtime']
            else:
                # Fallback if OMDB data not available
                enhanced_rec['poster'] = 'N/A'
                enhanced_rec['imdb_id'] = 'N/A'
            
            enhanced_recommendations.append(enhanced_rec)
        
        return jsonify({
            'success': True,
            'recommendations': enhanced_recommendations
        })
    
    except json.JSONDecodeError as e:
        print(f"JSON Decode Error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Something went wrong. Please try again later.',
            'error_type': 'parse_error'
        }), 500
    
    except Exception as e:
        error_message = str(e).lower()
        print(f"Error: {str(e)}")
        
        # Check if it's an API limit/quota error
        if any(keyword in error_message for keyword in ['quota', 'limit', 'rate limit', 'resource exhausted', '429', 'too many requests']):
            return jsonify({
                'success': False,
                'error': "Sorry 😔 We've reached the API limit for today. Please wait before trying again.",
                'error_type': 'api_limit'
            }), 429
        else:
            # Generic error for other issues
            return jsonify({
                'success': False,
                'error': 'Something went wrong. Please try again later.',
                'error_type': 'general_error'
            }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
