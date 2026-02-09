# AI Document Summarizer

A modern, full-stack document summarization application powered by Facebook's BART-CNN model via HuggingFace Inference API. Features a beautiful React frontend with multiple summarization styles and support for various file formats including PDFs.

> [View Detailed Technical Documentation →](DEVELOPMENT.md)

![Tech Stack](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-61DAFB?style=flat&logo=react&logoColor=black)
![HuggingFace](https://img.shields.io/badge/HuggingFace-FFD21E?style=flat&logo=huggingface&logoColor=black)
![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Setup Instructions](#setup-instructions)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Development Journey](#development-journey)
- [Design Decisions](#design-decisions)
- [Project Structure](#project-structure)
- [Contributing](#contributing)

> [View Detailed Technical Documentation](DEVELOPMENT.md)

## Features

- **Multiple Summarization Styles**: Brief, Standard, Detailed, and Bullet Points
- **File Upload Support**: .txt, .md, .csv, .json, and .pdf files
- **PDF Text Extraction**: Automatic text extraction from PDF documents
- **Smart Input Validation**: 50-1500 words for text input, 100-4000 words for files
- **Modern UI**: Beautiful gradient design with glassmorphism effects
- **Toast Notifications**: Non-intrusive feedback for user actions
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Real-time Processing**: Fast summarization with HuggingFace Inference API

## Tech Stack

### Backend
- **FastAPI**: Modern Python web framework for building APIs
- **HuggingFace Inference API**: Cloud-based model inference
- **BART-CNN**: Facebook's state-of-the-art summarization model
- **NLTK**: Natural Language Toolkit for sentence tokenization
- **PyPDF2**: PDF text extraction
- **Python-dotenv**: Environment variable management

### Frontend
- **React**: Component-based UI library
- **React Router**: Client-side routing
- **Vite**: Fast build tool and dev server
- **CSS3**: Modern styling with gradients and animations

## Setup Instructions

### Prerequisites

- Python 3.8+
- Node.js 16+
- HuggingFace Account (for API token)

### Backend Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd ai-summarizer
```

2. **Create virtual environment**
```bash
cd backend
python -m venv venv

# On macOS/Linux
source venv/bin/activate

# On Windows
venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Download NLTK data**
```bash
python -c "import nltk; nltk.download('punkt')"
```

5. **Create environment file**
```bash
cp .env.example .env
```

Edit `.env` and add your HuggingFace token:
```env
HF_TOKEN=your_huggingface_token_here
FRONTEND_URL=http://localhost:5174
```

Get your HuggingFace token from: https://huggingface.co/settings/tokens

6. **Run the backend server**
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory**
```bash
cd frontend
```

2. **Install dependencies**
```bash
npm install
```

3. **Run the development server**
```bash
npm run dev
```

The application will be available at `http://localhost:5174`

## Usage

### Web Interface

1. Open `http://localhost:5174` in your browser
2. Choose one of two input methods:
   - **Upload a file**: Click "Choose File" and select a .txt, .md, .csv, .json, or .pdf file
   - **Paste text**: Type or paste text directly into the textarea
3. Select a summarization style:
   - **Brief**: Quick overview (10-60 tokens)
   - **Standard**: Balanced summary (30-140 tokens)
   - **Detailed**: Comprehensive summary (60-230 tokens)
   - **Bullet Points**: Key points formatted as bullets
4. Click "Generate Summary"
5. Copy the summary using the "Copy to Clipboard" button

### API Usage

#### Summarize Text

```bash
curl -X POST http://localhost:8000/api/summarize \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Your long text here...",
    "style": "standard"
  }'
```

#### Summarize File

```bash
curl -X POST http://localhost:8000/api/summarize-file \
  -F "file=@document.pdf" \
  -F "style=detailed"
```

#### Health Check

```bash
curl http://localhost:8000/api/health
```

## API Documentation

### Endpoints

#### `POST /api/summarize`

Summarize text input.

**Request Body:**
```json
{
  "text": "string (required, 50-1500 words, min 3 sentences)",
  "style": "string (optional, default: 'standard')"
}
```

**Response:**
```json
{
  "summary": "string",
  "style": "string",
  "word_count": "integer"
}
```

#### `POST /api/summarize-file`

Summarize uploaded file.

**Form Data:**
- `file`: File (required, .txt/.md/.csv/.json/.pdf)
- `style`: String (optional, default: 'standard')

**Response:** Same as `/api/summarize`

#### `GET /api/health`

Check API health status.

**Response:**
```json
{
  "status": "ok",
  "message": "Summarization API is running"
}
```

### Summarization Styles

| Style | Description | Max Length | Min Length | Use Case |
|-------|-------------|------------|------------|----------|
| `brief` | Quick overview | 60 tokens | 10 tokens | Headlines, previews |
| `standard` | Balanced summary | 140 tokens | 30 tokens | General use (recommended) |
| `detailed` | Comprehensive | 230 tokens | 60 tokens | Research, technical docs |
| `bullet_points` | Key points as bullets | 160 tokens | 30 tokens | Easy scanning, notes |

## Development Journey

### Initial Model Selection: Google Flan-T5

We initially considered using **Google's Flan-T5** model for summarization:

**Why we considered it:**
- Powerful instruction-following capabilities
- Good at various NLP tasks
- Flexible with custom prompts

**Why we switched:**
- ❌ No direct inference API support on HuggingFace
- ❌ Would require self-hosting (complex deployment)
- ❌ Larger model size (resource intensive)
- ❌ Not specifically optimized for summarization

### Final Choice: Facebook BART-CNN

We switched to **facebook/bart-large-cnn** and it proved to be the perfect choice:

**Advantages:**
- ✅ Direct HuggingFace Inference API support
- ✅ Specifically fine-tuned on CNN/DailyMail dataset for summarization
- ✅ Production-ready with no deployment complexity
- ✅ Excellent quality for news articles and documents
- ✅ Well-documented parameters for fine-tuning

**BART vs T5 Comparison:**

According to research comparing T5 and BART for summarization ([detailed analysis](https://medium.com/@gabya06/t5-vs-bart-the-battle-of-the-summarization-models-c1e6d37e56ca)):

| Feature | BART | T5 (Flan-T5) |
|---------|------|--------------|
| **Architecture** | Encoder-decoder with denoising | Encoder-decoder with text-to-text |
| **Training** | Denoising autoencoder | Multi-task learning |
| **Summarization** | Specifically optimized | General-purpose |
| **Inference API** | ✅ Available | ❌ Not available |
| **Deployment** | Easy (cloud API) | Complex (self-host) |
| **Quality** | Excellent for news/docs | Good for instructions |
| **Speed** | Fast (optimized) | Slower (larger model) |

**Key Insight from Research:**
> "BART excels at abstractive summarization tasks, particularly for news articles and documents, due to its denoising pre-training objective which teaches it to reconstruct corrupted text. This makes it naturally suited for generating coherent summaries."

**Model Documentation:**
- HuggingFace Model: https://huggingface.co/facebook/bart-large-cnn
- BART Paper: https://arxiv.org/abs/1910.13461
- Inference API Docs: https://huggingface.co/docs/api-inference/
- BART vs T5 Analysis: https://medium.com/@gabya06/t5-vs-bart-the-battle-of-the-summarization-models-c1e6d37e56ca

### Text Processing Challenges

#### Challenge 1: Sentence Tokenization

**Problem:** Simple regex splitting (`.split('.')`) failed with:
- Abbreviations (Dr., Mr., U.S.A.)
- Decimal numbers (3.14)
- Multiple punctuation marks

**Solution:** Implemented NLTK's `sent_tokenize`
```python
from nltk.tokenize import sent_tokenize

sentences = sent_tokenize(text)  # Handles edge cases properly
```

**NLTK Documentation:** https://www.nltk.org/api/nltk.tokenize.html

#### Challenge 2: BART "Index Out of Range" Error

**Problem:** BART returned `"index out of range in self"` error for certain inputs.

**Root Causes:**
- Text too short (< 3 sentences)
- Missing proper punctuation
- Excessive whitespace or special characters

**Solution:** Implemented robust preprocessing
```python
def _preprocess_text(self, text: str) -> str:
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove control characters
    text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]', '', text)
    
    # Ensure proper punctuation
    text = text.strip()
    if text and text[-1] not in '.!?':
        text += '.'
    
    # Validate minimum sentences
    sentences = re.split(r'[.!?]+', text)
    if len(sentences) < 3:
        raise HTTPException(...)
    
    return text
```

#### Challenge 3: Parameter Tuning for Different Styles

**Problem:** How to achieve different summary lengths and styles with one model?

**Solution:** Discovered BART's generation parameters through documentation:

**Key Parameters:**
- `max_length`: Maximum tokens in output
- `min_length`: Minimum tokens in output
- `num_beams`: Beam search width (higher = better quality, slower)
- `length_penalty`: Controls length preference (>1 = longer, <1 = shorter)
- `early_stopping`: Stop when all beams finish

**Parameter Documentation:** https://huggingface.co/docs/transformers/main_classes/text_generation

**Model Card:** https://huggingface.co/facebook/bart-large-cnn

**Our Optimized Presets:**
```python
{
    "brief": {
        "max_length": 60,
        "min_length": 10,
        "num_beams": 4,
        "length_penalty": 1.2,  # Prefer longer within range
        "early_stopping": True
    },
    "standard": {
        "max_length": 140,
        "min_length": 30,
        "num_beams": 4,
        "length_penalty": 1.0,  # Balanced
        "early_stopping": True
    },
    "detailed": {
        "max_length": 230,
        "min_length": 60,
        "num_beams": 5,  # More beams for quality
        "length_penalty": 0.9,  # Allow flexibility
        "early_stopping": True
    }
}
```

#### Challenge 4: Large Text Handling

**Problem:** BART has a 1024 token limit (~750 words).

**Initial Approach:** Tried chunking and hierarchical summarization
- Split text into chunks
- Summarize each chunk
- Combine and re-summarize

**Issues:**
- Lost context between chunks
- Inconsistent quality
- Slow processing

**Final Solution:** Input validation with clear limits
- Text area: 50-1500 words
- File upload: 100-4000 words
- Minimum 3 complete sentences
- Clear error messages for users

This approach ensures:
- ✅ Quality summaries (no context loss)
- ✅ Fast processing (single API call)
- ✅ Better user experience (clear expectations)

### PDF Support Implementation

**Challenge:** Extract text from PDF files for summarization.

**Solution:** PyPDF2 library
```python
from PyPDF2 import PdfReader

pdf_reader = PdfReader(pdf_file)
text = ""
for page in pdf_reader.pages:
    text += page.extract_text() + "\n"
```

**PyPDF2 Documentation:** https://pypdf2.readthedocs.io/

**Limitations:**
- Only extracts text (not images)
- Scanned PDFs require OCR (not implemented)
- Complex layouts may have formatting issues

## Design Decisions

### Architecture

**Why FastAPI?**
- Modern async support
- Automatic API documentation (Swagger)
- Type hints and validation with Pydantic
- Fast performance

**Why React?**
- Component reusability
- Large ecosystem
- Excellent developer experience
- Virtual DOM for performance

### API Design

**RESTful Principles:**
- Clear endpoint naming (`/api/summarize`, `/api/summarize-file`)
- Proper HTTP methods (POST for mutations)
- Meaningful status codes (400, 502, 504)
- Consistent response format

**Error Handling:**
- User-friendly error messages
- Specific validation errors
- Graceful degradation

### Frontend Design

**Modern UI Principles:**
- Purple gradient theme (professional, modern)
- Glassmorphism effects (navbar, footer)
- Smooth animations (fade-in, slide-up)
- Toast notifications (non-intrusive feedback)
- Responsive design (mobile-first)

**UX Decisions:**
- Word counter for input validation
- Clear file upload with drag-and-drop styling
- Loading states for async operations
- Copy to clipboard with visual feedback
- Multiple input methods (text + file)

### Security

**CORS Configuration:**
- Whitelist specific origins
- Environment-based configuration
- Credentials support for future auth

**Input Validation:**
- File type restrictions
- File size limits (10MB)
- Text length validation
- Sentence structure validation

## Project Structure

```
ai-summarizer/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI app & CORS
│   │   ├── models/                 # Database models (future)
│   │   ├── routers/
│   │   │   └── summary_router.py   # API endpoints
│   │   ├── schemas/
│   │   │   └── summary_schema.py   # Pydantic models
│   │   └── services/
│   │       ├── llm_service.py      # BART-CNN integration
│   │       └── file_service.py     # File handling & PDF
│   ├── .env                        # Environment variables
│   ├── .env.example                # Template
│   ├── requirements.txt            # Python dependencies
│   └── venv/                       # Virtual environment
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   └── Navbar.jsx          # Navigation bar
│   │   ├── pages/
│   │   │   ├── Home.jsx            # Main summarizer UI
│   │   │   ├── About.jsx           # Project info
│   │   │   └── Docs.jsx            # API documentation
│   │   ├── App.jsx                 # Router setup
│   │   ├── App.css                 # Global styles
│   │   └── main.jsx                # Entry point
│   ├── package.json                # Node dependencies
│   └── vite.config.js              # Vite configuration
├── test_api.py                     # API test suite
└── README.md                       # This file
```

## Testing

Run the comprehensive test suite:

```bash
python test_api.py
```

Tests include:
- Health check
- Input validation (too short, too long, valid)
- All summarization styles
- File uploads
- Error handling
- Performance benchmarks

## Deployment

### Deploy to Render

This project includes a `render.yaml` configuration for easy deployment.

**Backend Deployment:**
1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Set root directory to `backend`
4. Build Command: `pip install -r requirements.txt && python download_nltk_data.py`
5. Start Command: `gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT`
6. Add environment variables:
   - `HF_TOKEN`: Your HuggingFace API token
   - `FRONTEND_URL`: Your frontend URL (e.g., `https://your-app.onrender.com`)

**Frontend Deployment:**
1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Set root directory to `frontend`
4. Build Command: `npm install && npm run build`
5. Start Command: `npm run preview -- --host 0.0.0.0 --port $PORT`
6. Add environment variable:
   - `VITE_API_BASE_URL`: Your backend API URL (e.g., `https://your-api.onrender.com/api`)

**Alternative: Use render.yaml**
- Push `render.yaml` to your repository
- Render will automatically detect and deploy both services

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License.

## Acknowledgments

- **HuggingFace** for the Inference API and model hosting
- **Facebook AI** for the BART model
- **NLTK Team** for natural language processing tools
- **FastAPI** and **React** communities for excellent documentation

## Contact

For questions or feedback, please open an issue on GitHub.

---

## Additional Resources

- **[Technical Documentation (DEVELOPMENT.md)](DEVELOPMENT.md)** - Detailed development journey, challenges, and solutions
- **[API Documentation](#api-documentation)** - Complete API reference
- **[Test Suite](test_api.py)** - Comprehensive API tests

---

**Built with using FastAPI, React, and BART-CNN**
