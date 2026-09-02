from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import shutil
import os
import uuid
from tiktok_quality import transform
import tempfile

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def home():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/patch")
async def patch_video(file: UploadFile = File(...)):
    if not file.filename.lower().endswith((".mp4", ".mov")):
        raise HTTPException(status_code=400, detail="Only MP4 and MOV files are allowed")

    # Use temporary directory (better for cloud)
    with tempfile.TemporaryDirectory() as temp_dir:
        input_path = os.path.join(temp_dir, "input.mp4")
        output_path = os.path.join(temp_dir, "patched.mp4")

        # Save uploaded file
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        try:
            # Run the patcher
            transform(
                input_path,
                output_path,
                multiplier=10,
                comment="AJ and RS Upload Method"
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Patching failed: {str(e)}")

        # Return the file
        return FileResponse(
            output_path,
            media_type="video/mp4",
            filename="AJ_RS_Patched.mp4",
            background=None  # important so file isn't deleted too early
        )