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


---

## Usage

1. Fill in your preferences:
   - Select content type (Movies/Web Series/Any)
   - Choose your preferred genre
   - Select your current mood
   - Pick language preference
   - Choose format (Dubbed/Subtitled/Original)
   - Select OTT platform
   - Set year range
2. Click "Get Recommendations"
3. View your 6 personalized recommendations with titles, years, and reasons!

## Technologies Used

- **Backend**: Flask (Python)
- **AI**: Google Gemini 3.0 Flash API & OMDB API
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Styling**: Custom CSS with gradient backgrounds and animations
- **Environment**: python-dotenv for configuration

## API Integration

The application uses the Gemini 2.0 Flash API (`gemini-2.0-flash-exp`) with a carefully crafted prompt that ensures:
- Strict adherence to user criteria
- JSON-formatted responses
- Exactly 5 recommendations
- Title, year, and compelling reason for each suggestion

---

## Contributing

Feel free to fork this project and submit pull requests for any improvements!

---

## License

This project is open source and available for personal and educational use.

---

**Enjoy discovering your next favorite movie or series! 🎬🍿**
