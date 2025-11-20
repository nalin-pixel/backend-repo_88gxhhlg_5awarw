import os
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional
from pydantic import BaseModel

from database import create_document, get_documents, db

app = FastAPI(title="Interior Studio API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Interior Studio API running"}


# Health + DB test
@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:80]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"
    return response


# -------- Models ---------
class ContactSubmission(BaseModel):
    name: str
    phone: str
    email: str
    city: Optional[str] = None
    project_type: str
    notes: Optional[str] = None
    summary: Optional[str] = None
    budget_range: Optional[str] = None


class ChatbotRequest(BaseModel):
    room: str
    style: str
    budget: str
    measurements: Optional[str] = None


class ChatbotResponse(BaseModel):
    title: str
    recommendations: List[str]
    estimate: str
    timeline: str
    palette: List[str]


# -------- Static data endpoints (materials, projects, rooms) ---------
@app.get("/api/materials")
def get_materials():
    return {
        "categories": [
            {
                "name": "Woods",
                "items": [
                    {"title": "Walnut", "look": "Rich, deep brown with straight grain", "use": "Cabinetry, feature walls", "durability": "High", "budget": "$$$", "alternatives": ["Teak", "Oak"], "image": "https://images.unsplash.com/photo-1616628188460-20b6b3f5ad5b"},
                    {"title": "Oak", "look": "Warm beige-brown, visible grain", "use": "Flooring, furniture", "durability": "High", "budget": "$$", "alternatives": ["Ash", "Maple"], "image": "https://images.unsplash.com/photo-1533090368676-1fd25485db88"}
                ]
            },
            {
                "name": "Marbles",
                "items": [
                    {"title": "Calacatta", "look": "Bold veining on white base", "use": "Countertops, bathroom", "durability": "Medium", "budget": "$$$$", "alternatives": ["Carrara", "Quartz"], "image": "https://images.unsplash.com/photo-1523419409543-8ce8a06673f6"}
                ]
            },
            {
                "name": "Fabrics",
                "items": [
                    {"title": "Bouclé", "look": "Soft looped texture", "use": "Sofas, ottomans", "durability": "Medium", "budget": "$$$", "alternatives": ["Chenille", "Velvet"], "image": "https://images.unsplash.com/photo-1610312275356-8e9aa9e8cf9e"}
                ]
            },
            {
                "name": "Lighting",
                "items": [
                    {"title": "Linear LED", "look": "Minimal continuous glow", "use": "Cove, task lighting", "durability": "High", "budget": "$$", "alternatives": ["COB Strip", "Track"], "image": "https://images.unsplash.com/photo-1550226891-ef816aed4a47"}
                ]
            }
        ]
    }


@app.get("/api/projects")
def get_projects():
    return {
        "projects": [
            {
                "id": "p1",
                "title": "Skyline Living Room",
                "before": "https://images.unsplash.com/photo-1505692794403-34d4982fa0bd",
                "after": "https://images.unsplash.com/photo-1505691938895-1758d7feb511",
                "story": {
                    "challenge": "Dark, cramped living area lacking identity.",
                    "moodboard": [
                        "https://images.unsplash.com/photo-1493666438817-866a91353ca9",
                        "https://images.unsplash.com/photo-1524758631624-e2822e304c36"
                    ],
                    "sketch": "https://images.unsplash.com/photo-1529088743536-4bc3ee39c1ff",
                    "materials": ["Walnut", "Calacatta Marble", "Matte Black"],
                    "testimonial": "They turned our apartment into a sanctuary in the sky."
                }
            },
            {
                "id": "p2",
                "title": "Minimal Chef Kitchen",
                "before": "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267",
                "after": "https://images.unsplash.com/photo-1519710164239-da123dc03ef4",
            }
        ]
    }


@app.get("/api/rooms")
def get_rooms():
    return {
        "rooms": [
            {
                "name": "Living Room",
                "hotspots": [
                    {"title": "Material Used", "text": "Walnut wood + linen fabric"},
                    {"title": "Lighting Technique", "text": "Layered: cove + accent + task"},
                    {"title": "Color Theme", "text": "Warm neutrals with matte black"}
                ]
            },
            {
                "name": "Bedroom",
                "hotspots": [
                    {"title": "Material Used", "text": "Bouclé headboard + oak floor"}
                ]
            }
        ]
    }


# -------- AI-like features (mocked) ---------
@app.post("/api/redesign")
async def ai_redesign(style: Optional[str] = Form(None), file: UploadFile = File(...)):
    styles = [
        {"name": "Modern Minimal", "image": "https://images.unsplash.com/photo-1505691723518-36a5ac3b2dba"},
        {"name": "Luxury Classic", "image": "https://images.unsplash.com/photo-1484154218962-a197022b5858"},
        {"name": "Urban Cozy", "image": "https://images.unsplash.com/photo-1519710164239-da123dc03ef4"},
    ]
    return {"input_filename": file.filename, "variants": styles}


@app.post("/api/chatbot", response_model=ChatbotResponse)
def chatbot(payload: ChatbotRequest):
    style_notes = {
        "Minimal": ["Clean planes", "Hidden storage", "Warm neutral palette"],
        "Luxury": ["Layered lighting", "Stone accents", "Bronze details"],
        "Boho": ["Natural textures", "Eclectic patterns", "Plants"],
        "Modern": ["Matte finishes", "Sharp lines", "Smart controls"],
    }
    key = "Minimal" if "minimal" in payload.style.lower() else (
        "Luxury" if "lux" in payload.style.lower() else (
            "Modern" if "modern" in payload.style.lower() else "Boho"
        )
    )
    recos = [
        f"Space planning for {payload.room} with functional zones",
        f"Material palette aligned to {key} sensibility",
        "Lighting plan with dimmable scenes",
        "3D visualization + 2 revisions",
    ]
    palette = ["#EAE7E2", "#C8C3BD", "#A8957B", "#1E1E1E"] if key != "Boho" else ["#F3E8D3", "#D8C4A0", "#6B705C", "#2B2D2F"]
    return ChatbotResponse(
        title=f"Concept for {payload.room} — {key}",
        recommendations=recos,
        estimate="₹ 6–9L (turnkey) | ₹ 2–3L (design only)",
        timeline="6–10 weeks",
        palette=palette,
    )


@app.post("/api/contact")
def contact(submission: ContactSubmission):
    try:
        inserted_id = create_document("contactsubmission", submission.dict())
        return {"status": "ok", "id": inserted_id}
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})
