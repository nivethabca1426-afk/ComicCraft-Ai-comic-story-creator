# ComicCraft — AI Comic Story Creator

ComicCraft is a FastAPI web application based on the supplied project specification. It accepts a story prompt, character name, setting, tone and art style, then runs this pipeline:

1. Gemini Flash → exactly 5 connected panel outlines.
2. Gemini Pro → narration, captions and dialogue for the five panels.
3. Stable Diffusion through Hugging Face Inference → one illustration per panel.
4. Layout builder → matches each image with its story panel.
5. FPDF → exports the complete comic to a PDF.
6. Jinja2 → renders the interactive comic preview.

The specification describes Gemini 1.5 Flash/Pro. The code defaults to current configurable Gemini model IDs (`gemini-2.5-flash` and `gemini-2.5-pro`) but you can change them in `.env`.

## Project structure

```text
ComicCraft/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── routes.py
│   ├── config.py
│   ├── schemas.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── gemini_flash.py
│   │   ├── gemini_pro.py
│   │   ├── image_generator.py
│   │   ├── layout_builder.py
│   │   └── exporters.py
│   ├── templates/
│   │   ├── index.html
│   │   ├── comic_preview.html
│   │   └── export_success.html
│   └── static/
│       ├── css/style.css
│       ├── js/app.js
│       ├── panels/.gitkeep
│       └── exports/.gitkeep
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## 1. Install Python

Use Python 3.11 or newer.

Check:

```bash
python --version
```

## 2. Open the project in VS Code

Open the `ComicCraft` folder in VS Code.

## 3. Create a virtual environment

### Windows PowerShell

```powershell
python -m venv comiccraft-env
.\comiccraft-env\Scripts\Activate.ps1
```

If PowerShell blocks activation, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\comiccraft-env\Scripts\Activate.ps1
```

### Windows CMD

```cmd
python -m venv comiccraft-env
comiccraft-env\Scripts\activate
```

### macOS/Linux

```bash
python3 -m venv comiccraft-env
source comiccraft-env/bin/activate
```

## 4. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 5. Create the `.env` file

Copy `.env.example` to `.env`.

Windows:

```powershell
Copy-Item .env.example .env
```

macOS/Linux:

```bash
cp .env.example .env
```

Then put your real keys in `.env`:

```env
GEMINI_API_KEY=your_real_gemini_key
HF_API_KEY=your_real_huggingface_token
GEMINI_FLASH_MODEL=gemini-2.5-flash
GEMINI_PRO_MODEL=gemini-2.5-pro
HF_IMAGE_MODEL=runwayml/stable-diffusion-v1-5
IMAGE_BACKEND=hf
```

Never upload `.env` to GitHub.

## 6. Start ComicCraft

From the project root:

```bash
uvicorn app.main:app --reload
```

Open:

- Website: http://127.0.0.1:8000
- API documentation: http://127.0.0.1:8000/docs
- Health check: http://127.0.0.1:8000/health

## 7. Test the application

### Test 1 — Health check

Open `/health`. You should see:

```json
{"status":"ok","app":"ComicCraft"}
```

### Test 2 — Image generation

Open `/docs`, select `GET /test-image`, click **Try it out**, enter a prompt and execute it.

The generated image will be saved under:

```text
app/static/panels/
```

### Test 3 — Full browser workflow

On the homepage enter:

- Story Prompt: `A brave fox discovers a glowing secret beneath an enchanted forest.`
- Main Character: `Luna`
- Setting: `Forest`
- Tone: `Adventurous`
- Art Style: `Comic book`

Click **Generate My Comic**.

The server will generate five panels, display them, create the PDF, and show the PDF download button.

### Test 4 — JSON API

In `/docs`, use `POST /generate-comic/json` with:

```json
{
  "story_prompt": "A brave fox discovers a glowing secret beneath an enchanted forest.",
  "character_name": "Luna",
  "setting": "Forest",
  "tone": "Adventurous",
  "art_style": "Comic book"
}
```

## Image generation backends

The default backend is Hugging Face hosted inference because it avoids downloading a large Stable Diffusion model to the student's computer. The code still supports local Diffusers as an alternative.

### Hugging Face hosted inference

Use:

```env
IMAGE_BACKEND=hf
HF_API_KEY=your_token
```

### Local Diffusers

Change:

```env
IMAGE_BACKEND=local
LOCAL_IMAGE_MODEL=runwayml/stable-diffusion-v1-5
```

For local mode, install PyTorch and Diffusers appropriate for your machine. A CUDA-capable NVIDIA GPU is strongly recommended for practical generation speed.

## API routes

| Method | Route | Purpose |
|---|---|---|
| GET | `/` | Homepage |
| POST | `/generate` | Browser form → complete comic |
| POST | `/generate-comic/json` | JSON API → complete comic |
| GET | `/test-image` | Image generation test |
| GET | `/download/{filename}` | Download generated PDF |
| GET | `/export-success` | Export confirmation page |
| GET | `/health` | Server health check |

## Troubleshooting

### `GEMINI_API_KEY is missing`
Create `.env` and add a valid Gemini API key.

### Hugging Face authentication error
Check that `HF_API_KEY` is correct and that your selected image model/provider is available to your account. You can change `HF_IMAGE_MODEL` without changing Python code.

### Image generation is slow
Hosted inference can take time, and the full workflow makes five image requests. For local generation, a suitable GPU can improve performance.

### PDF does not show an image
Make sure the image was generated into `app/static/panels/` and that the process has write permission for that directory.

### Gemini returns invalid JSON
Retry the request. The code requests JSON-only output and validates the result with Pydantic. If a model behaves differently, change the configured model in `.env`.

## Security notes

- Keep API keys in `.env`.
- Do not commit `.env` to Git.
- Do not expose your API keys in frontend JavaScript.
- In production, add authentication, rate limiting, request-size limits, persistent storage and background job processing.
