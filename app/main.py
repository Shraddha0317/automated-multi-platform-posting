import uvicorn
from fastapi import FastAPI, Depends

from app.schemas import PostRequest, PostResponse
from app.config import Settings, get_settings
from app.services.posting_service import publish_to_all


app = FastAPI(
    title="Automated Multi-Platform Posting System"
)


@app.post("/posting", response_model=PostResponse)
async def post_message(
    request: PostRequest,
    settings: Settings = Depends(get_settings)
):
    cta_link = request.extract_cta_link()

    results = await publish_to_all(
        message=request.message,
        cta_link=cta_link,
        settings=settings
    )

    overall_success = any(r.status == "success" for r in results)

    return PostResponse(success=overall_success, results=results)


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=4000, reload=True)
