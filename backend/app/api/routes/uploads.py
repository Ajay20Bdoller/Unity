import base64

from fastapi import APIRouter, Depends, HTTPException, UploadFile

from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/uploads", tags=["uploads"])

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_SIZE_BYTES = 2 * 1024 * 1024  # 2 MB


@router.post("/image")
async def upload_image(
    file: UploadFile, current_user: User = Depends(get_current_user)
) -> dict[str, str]:
    """Accepts an image file and returns a data: URI that can be used
    directly as photo_url anywhere in the app (mentor profiles, About
    Us). Deliberately not stored as a separate file on disk or in
    external object storage: a container platform's filesystem is
    typically ephemeral (wiped on redeploy), and introducing a
    dependency on an external storage service is more infrastructure
    than a pilot-stage platform's photo count justifies. The data URI
    is stored directly in Postgres (which already has durable,
    reliable storage provisioned) -- this trades a larger database
    row for *total* reliability: once uploaded, it can never break
    the way an external link (Google Drive included) can, because
    there is no external link to break.
    """
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Only JPEG, PNG, WEBP, or GIF images are supported.",
        )

    contents = await file.read()
    if len(contents) > MAX_SIZE_BYTES:
        raise HTTPException(status_code=400, detail="Image must be under 2 MB.")
    if len(contents) == 0:
        raise HTTPException(status_code=400, detail="File is empty.")

    encoded = base64.b64encode(contents).decode("ascii")
    data_uri = f"data:{file.content_type};base64,{encoded}"
    return {"url": data_uri}
