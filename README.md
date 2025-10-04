# Movie & Series Suggestion Website

A beautiful and intelligent movie/web series recommendation website powered by Flask and Google's Gemini 2.0 Flash API. Get personalized recommendations based on your preferences including genre, mood, language, format, OTT platform, and release year range.

## Features

- 🎬 **Smart Recommendations**: Get 5 personalized movie/series suggestions using AI
- 🎨 **Beautiful UI**: Modern, responsive design with smooth animations
- 🔍 **Advanced Filtering**: Multiple criteria including:
  - Content Type (Movies/Web Series)
  - Genre (Action, Comedy, Drama, etc.)
  - Mood (Happy, Excited, Relaxed, etc.)
  - Language (English, Hindi, Korean, Spanish, etc.)
  - Format (Dubbed/Subtitled/Original)
  - OTT Platform (Netflix, Prime Video, Disney+, etc.)
  - Year Range (1950-2025)
- ⚡ **Fast & Reliable**: Built with Flask and powered by Gemini 2.0 Flash API

## Project Structure

```
movies suggestion/
│
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── .env                   # Your actual API keys (create this)
│
├── templates/
│   └── index.html         # Main HTML template
│
└── static/
    ├── css/
    │   └── style.css      # Styling
    └── js/
        └── script.js      # Frontend JavaScript
```

## Setup Instructions

### 1. Prerequisites

- Python 3.10 or higher
- A Google Gemini API key

### 2. Get Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy your API key

### 3. Installation

1. **Clone or navigate to the project directory**
   ```bash
   cd "e:\sonu\movies suggestion"
   ```

2. **Create and activate virtual environment** (Already done)
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. **Install dependencies** (Already done)
   ```powershell
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```powershell
   # Copy the example file
   copy .env.example .env
   ```
   
   Then edit `.env` file and add your Gemini API key:
   ```
   GEMINI_API_KEY=your_actual_api_key_here
   ```

### 4. Run the Application

```powershell
# Make sure virtual environment is activated
.\venv\Scripts\Activate.ps1

# Run the Flask app
python app.py
```

The application will start on `http://localhost:5000`

## Usage

1. Open your web browser and go to `http://localhost:5000`
2. Fill in your preferences:
   - Select content type (Movies/Web Series/Any)
   - Choose your preferred genre
   - Select your current mood
   - Pick language preference
   - Choose format (Dubbed/Subtitled/Original)
   - Select OTT platform
   - Set year range
3. Click "Get Recommendations"
4. View your 5 personalized recommendations with titles, years, and reasons!

## Technologies Used

- **Backend**: Flask (Python)
- **AI**: Google Gemini 2.0 Flash API
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Styling**: Custom CSS with gradient backgrounds and animations
- **Environment**: python-dotenv for configuration

## API Integration

The application uses the Gemini 2.0 Flash API (`gemini-2.0-flash-exp`) with a carefully crafted prompt that ensures:
- Strict adherence to user criteria
- JSON-formatted responses
- Exactly 5 recommendations
- Title, year, and compelling reason for each suggestion

## Troubleshooting

### API Key Issues
- Make sure your `.env` file exists and contains the correct API key
- Verify the API key is active in Google AI Studio

### Port Already in Use
- Change the port in `app.py`: `app.run(debug=True, host='0.0.0.0', port=5001)`

### Dependencies Issues
- Reinstall dependencies: `pip install -r requirements.txt --upgrade`

## Contributing

Feel free to fork this project and submit pull requests for any improvements!

## License

This project is open source and available for personal and educational use.

---

**Enjoy discovering your next favorite movie or series! 🎬🍿**
