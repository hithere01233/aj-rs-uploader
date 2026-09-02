python
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import shutil
import os
import uuid
from tiktok_quality import transform

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

# Render's temporary storage
UPLOAD_DIR = "/tmp/tiktok_patcher"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def cleanup(path: str):
    try:
        if os.path.exists(path):
            os.remove(path)
    except Exception:
        pass


@app.get("/", response_class=HTMLResponse)
async def home():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()


@app.post("/patch")
async def patch_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    if not file.filename.lower().endswith((".mp4", ".mov")):
        raise HTTPException(
            status_code=400,
            detail="Only MP4 and MOV files are allowed"
        )

    file_id = str(uuid.uuid4())

    input_path = os.path.join(
        UPLOAD_DIR,
        f"{file_id}_input.mp4"
    )

    output_path = os.path.join(
        UPLOAD_DIR,
        f"{file_id}_patched.mp4"
    )

    try:
        # Save uploaded video
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Run the patcher
        transform(
            input_path=input_path,
            output_path=output_path,
            multiplier=10,
            comment="AJ and RS Upload Method",
            verbose=False
        )

        # Make absolutely sure the patcher created the file
        if not os.path.isfile(output_path):
            raise RuntimeError(
                f"Patcher did not create the output file: {output_path}"
            )

        # Original upload is no longer needed
        cleanup(input_path)

        # Delete patched video AFTER it has been downloaded
        background_tasks.add_task(cleanup, output_path)

        return FileResponse(
            path=output_path,
            media_type="video/mp4",
            filename="AJ_RS_Patched.mp4",
            background=background_tasks
        )

    except Exception as e:
        cleanup(input_path)
        cleanup(output_path)

        raise HTTPException(
            status_code=500,
            detail=f"Patching failed: {str(e)}"
        )
