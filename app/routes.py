from pathlib import Path
from urllib.parse import urlparse

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

from app.config import BASE_DIR
from app.schemas import PromptRequest
from app.services.exporters import save_pdf
from app.services.gemini_flash import generate_outline
from app.services.gemini_pro import generate_story
from app.services.image_generator import generate_image
from app.services.layout_builder import build_comic_layout

router = APIRouter()
templates = Jinja2Templates(directory=str(BASE_DIR / "app" / "templates"))


def _generate_comic(request_data: PromptRequest):
    outline = generate_outline(request_data)
    story = generate_story(request_data, outline)
    image_paths = [generate_image(panel.image_prompt) for panel in story]
    layout = build_comic_layout(story, image_paths)
    pdf_path = save_pdf(layout, title=f"{request_data.character_name}'s Comic")
    return layout, pdf_path


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"request": request},
    )


@router.post("/generate", response_class=HTMLResponse)
async def generate(
    request: Request,
    story_prompt: str = Form(...),
    character_name: str = Form(...),
    setting: str = Form(...),
    tone: str = Form(...),
    art_style: str = Form(...),
):
    data = PromptRequest(
        story_prompt=story_prompt,
        character_name=character_name,
        setting=setting,
        tone=tone,
        art_style=art_style,
    )

    try:
        layout, pdf_path = _generate_comic(data)
    except Exception as exc:
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={"request": request, "error": str(exc), "form": data.model_dump()},
            status_code=500,
        )

    return templates.TemplateResponse(
        request=request,
        name="comic_preview.html",
        context={
            "request": request,
            "layout": layout,
            "pdf_path": pdf_path,
            "download_name": Path(urlparse(pdf_path).path).name,
        },
    )


@router.post("/generate-comic/json")
async def generate_comic_json(payload: PromptRequest):
    try:
        layout, pdf_path = _generate_comic(payload)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return {
        "success": True,
        "layout": [panel.model_dump() for panel in layout],
        "pdf_path": pdf_path,
    }


@router.get("/test-image")
async def test_image(prompt: str = "A brave fox exploring an enchanted forest, vibrant comic book art"):
    try:
        image_path = generate_image(prompt)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return {"success": True, "prompt": prompt, "image_path": image_path}


@router.get("/download/{filename}")
async def download_pdf(filename: str):
    safe_name = Path(filename).name
    file_path = BASE_DIR / "app" / "static" / "exports" / safe_name
    if not file_path.exists() or file_path.suffix.lower() != ".pdf":
        raise HTTPException(status_code=404, detail="PDF not found")
    return FileResponse(file_path, media_type="application/pdf", filename=safe_name)


@router.get("/export-success", response_class=HTMLResponse)
async def export_success(request: Request, filename: str = ""):
    return templates.TemplateResponse(
        request=request,
        name="export_success.html",
        context={"request": request, "filename": filename},
    )
