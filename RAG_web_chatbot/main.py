from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse, FileResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from starlette.requests import Request
from rag_model import process_file, initialize_rag, initialize_llm
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.mount("/static", StaticFiles(directory="templates"), name="static")

templates = Jinja2Templates(directory="templates")

# API 키를 직접 코드에 포함 (주의: 실제 서비스에서는 환경 변수를 사용하는 것이 안전함)
openai_api_key = "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"

# 템플릿 렌더링
@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# 파일 업로드 처리
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    vectorstore = await process_file(file)
    global qa_chain
    llm = initialize_llm(openai_api_key)
    qa_chain = initialize_rag(vectorstore, llm)
    return JSONResponse(content={"success": True})

# 챗봇 상호작용 엔드포인트
class Query(BaseModel):
    question: str

@app.post("/chat")
async def chat(query: Query):
    if not qa_chain:
        return JSONResponse(content={"error": "No data loaded"}, status_code=400)
    result = qa_chain({"query": query.question})
    return JSONResponse(content={"response": result['result']})

# 전역 변수
qa_chain = None

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)