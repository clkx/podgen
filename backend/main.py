from fastapi import FastAPI, UploadFile, File, HTTPException, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
import json
import os
import pdfplumber
import io
import shutil
import unicodedata
import re
from pathlib import Path
from fastapi.responses import FileResponse, StreamingResponse, HTMLResponse
from dotenv import load_dotenv
from datetime import datetime
import azure.cognitiveservices.speech as speechsdk

from backend.graphs.pdf_graph import create_pdf_graph
from backend.graphs.arxiv_graph import create_arxiv_graph
from backend.graphs.research_graph import create_research_graph
from backend.graphs.scriptwriting_graph import create_scriptwriting_graph
from backend.graphs.summarizing_graph import create_summarizing_graph
from backend.graphs.prompt_graph import create_prompt_graph
from backend.schema import *
from backend.speech_synthesis import synthesize_podcast, PodcastSynthesizer
from backend.database.qdrant_manager import QdrantManager
from backend.models.embedding import EMBEDDING_MODEL

load_dotenv()

writing_graph = create_scriptwriting_graph()
summarizing_graph = create_summarizing_graph()
pdf_graph = create_pdf_graph()
arxiv_graph = create_arxiv_graph()
research_graph = create_research_graph()
prompt_graph = create_prompt_graph()

app = FastAPI()

# 修改 CORS 設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # 明確指定前端的來源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# 修改存儲路徑定義
BASE_DIR = Path(__file__).resolve().parent
REFERENCES_PATH = BASE_DIR / "stores" / "references"
TEMP_PATH = BASE_DIR / "stores" / "temp"
AUDIO_DIR = BASE_DIR / "stores" / "audio"

# 確保目錄存在
TEMP_PATH.mkdir(parents=True, exist_ok=True)
REFERENCES_PATH.mkdir(parents=True, exist_ok=True)
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

# 掛載靜態檔案服務
app.mount("/audio", StaticFiles(directory=str(AUDIO_DIR)), name="audio")

# 請求模型
class PromptInput(BaseModel):
    topic: str = Field(examples = ["寫一段關於LLM Agent的介紹"], description="使用者所輸入的Prompt，作為Podcast生成的主題")
    max_analysts: int = Field(examples = [3], description="使用多少位research agent來蒐集這主題的參考資料")
    host_name: str = Field(examples = ["主持人"], description="主持人名字")
    host_background: str = Field(examples = ["主持人是一位資深記者，擁有豐富的新聞採訪經驗，擅長以輕鬆有趣的方式採訪嘉賓，並將複雜的議題轉化為聽眾容易理解的內容。"], description="主持人背景")
    guest_name: str = Field(examples = ["來賓"], description="來賓名字")
    guest_background: str = Field(examples = ["來賓是一位資深的領域專家，擁有豐富的研究經驗，擅長以輕鬆有趣的方式解釋複雜的議題，並將其轉化為聽眾容易理解的內容。"], description="來賓背景")

class PdfInput(BaseModel):
    pdf_file: UploadFile = File(...)
    host_name: str = Field(examples = ["主持人"], description="主持人名字")
    host_background: str = Field(examples = ["主持人是一位資深的領域學者，擁有豐富的研究經驗，擅長以輕鬆有趣的方式採訪嘉賓，並將複雜的議題轉化為聽眾容易理解的內容。"], description="主持人背景")
    guest_name: str = Field(examples = ["來賓"], description="來賓名字")
    guest_background: str = Field(examples = ["來賓是一位資深的領域學者，擁有豐富的研究經驗，擅長以輕鬆有趣的方式解釋雜的議題，並將其轉化為聽眾容易理解的內容。"], description="來賓背景")


class ArxivInput(BaseModel):
    arxiv_url: str = Field(examples = ["https://arxiv.org/abs/2405.04434"], description="想要作為Podcast生成依據的Arxiv URL")
    host_name: str = Field(examples = ["主持人"], description="主持人名字")
    host_background: str = Field(examples = ["主持人是一位資深的領域學者，擁有豐富的研究經驗，擅長以輕鬆有趣的方式採訪嘉賓，並將複雜的議題轉化為聽眾容易理解的內容。"], description="主持人背景")
    guest_name: str = Field(examples = ["來賓"], description="來賓名字")
    guest_background: str = Field(examples = ["來賓是一位資深的領域學者，擁有豐富的研究經驗，擅長以輕鬆有趣的方式解釋複雜的議題，並將其轉化為聽眾容易理解的內容。"], description="來賓背景")


class AudioDialogueSegment(BaseModel):
    speaker: str
    content: str
    audio_file: Optional[str] = None

class AudioScript(BaseModel):
    dialogue: List[AudioDialogueSegment]
    host_name: str
    guest_name: str
    host_background: Optional[str] = None
    guest_background: Optional[str] = None
    full_audio: Optional[str] = None

class VoiceSettings(BaseModel):
    host_voice: str = "zh-TW-HsiaoChenNeural"
    guest_voice: str = "zh-TW-YunJheNeural"
    host_speed: float = 1.0
    guest_speed: float = 1.0
    host_pitch: int = 0
    guest_pitch: int = 0

class PodcastScript(BaseModel):
    dialogue: List[dict]
    host_name: str
    guest_name: str
    host_background: Optional[str] = None
    guest_background: Optional[str] = None

class PreviewRequest(BaseModel):
    text: str
    voice: str
    service: str = "azure"  # 預設使用 Azure

class RequestData(BaseModel):
    script: PodcastScript
    voice_settings: Optional[VoiceSettings] = None

# 確保參考資料目錄存在
REFERENCES_PATH.mkdir(parents=True, exist_ok=True)

def create_reference_folder(folder_name: str) -> Path:
    """建立參考資料資料夾"""
    folder_path = REFERENCES_PATH / folder_name
    folder_path.mkdir(parents=True, exist_ok=True)
    return folder_path

def sanitize_filename(filename):
    """清理檔案名稱，移除特殊字元並轉換空格"""
    # 將檔案名稱分成名稱和副檔名
    name, ext = os.path.splitext(filename)
    
    # 將 Unicode 字元正規化
    name = unicodedata.normalize('NFKC', name)
    
    # 將空格替換為底線，移除其他特殊字元
    name = re.sub(r'[^\w\s-]', '', name)
    name = re.sub(r'[-\s]+', '_', name)
    
    return name  # 返回不帶副檔名的檔案名稱

def pdf_to_markdown(pdf_content):
    """將 PDF 內容轉換為 Markdown 格式"""
    try:
        markdown_content = []
        with pdfplumber.open(pdf_content) as pdf:
            # 處理每一頁
            for i, page in enumerate(pdf.pages, 1):
                text = page.extract_text() or ""
                if text.strip():  # 如果頁面有內容
                    # 添加頁碼標題
                    markdown_content.append(f"\n## Page {i}\n")
                    # 處理段落
                    paragraphs = text.split('\n\n')
                    for para in paragraphs:
                        if para.strip():
                            markdown_content.append(para.strip() + "\n\n")
                            
        return "".join(markdown_content)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"PDF 轉換失敗：{str(e)}")

def pdf_to_text(pdf_content):
    """將 PDF 內容轉換為純文字"""
    with pdfplumber.open(pdf_content) as pdf:
        return "\n".join(page.extract_text() for page in pdf.pages)



@app.post("/api/upload/pdf")
async def upload_pdf(
    pdf_file: UploadFile = File(...),
    is_temporary: bool = Form(False)  # 新增參來區分是否為臨時上傳
):
    """上傳 PDF 並生成摘要，可選擇是否為臨時檔案(若為臨時檔案則不作摘要僅暫存)"""

    MAX_FILE_SIZE = 10 * 1024 * 1024 # 10MB in bytes
    
    try:
        # 檢查檔案大小
        file_size = 0
        content = bytearray()
        
        while chunk := await pdf_file.read(8192):
            file_size += len(chunk)
            if file_size > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=413,
                    detail="檔案大小超過限制（最大 10MB）"
                )
            content.extend(chunk)
        
        # 重置檔案指針
        await pdf_file.seek(0)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if is_temporary:
            # 臨時儲存
            temp_path = TEMP_PATH / timestamp
            temp_path.mkdir(parents=True, exist_ok=True)
            file_path = temp_path / f"{timestamp}_original.pdf"
            
            with file_path.open("wb") as f:
                f.write(content)
            
            return {
                "status": "success",
                "message": "臨時 PDF 檔案已上傳",
                "temp_folder": timestamp,
                "file_path": str(file_path)
            }
        else:
            # 長期儲存
            clean_filename = sanitize_filename(pdf_file.filename)
            folder_path = create_reference_folder(timestamp)
            
            # 儲存 PDF 檔案 - 使用{時間}_original格式
            pdf_path = folder_path / f"{timestamp}_original.pdf"
            with pdf_path.open("wb") as f:
                f.write(content)
            
            # 將 PDF 轉換為 Markdown
            markdown_content = pdf_to_markdown(io.BytesIO(content))
            
            # 在 Markdown 檔案開頭添加 metadata
            metadata = f"""---
            title: {clean_filename}
            original_filename: {pdf_file.filename}
            date_converted: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            file_size: {file_size / 1024 / 1024:.2f}MB
            ---

            """
            # 儲存 Markdown 檔案 - 使用時間_markdown格式
            markdown_path = folder_path / f"{timestamp}_content.md"
            with markdown_path.open("w", encoding="utf-8") as f:
                f.write(metadata + markdown_content)
            
            # 生成論文摘要
            try:
                # 將 PDF 轉換為純文本以利於用於摘要處理
                text_content = pdf_to_text(io.BytesIO(content))
                
                # 使��� summarizing_workflow 生成總結
                summary_input = {"content": text_content}
                summary_output = summarizing_graph.invoke(summary_input)
                
                # 解析 JSON 格式的總結內容
                summary_dict = summary_output if isinstance(summary_output, dict) else json.loads(summary_output)
                
                # 組合 Markdown 格式的總結
                summary_md = summary_dict.get('content', '無內容')
                
                # 儲存摘要到 summary.md - 使用{時間}_summary格式
                summary_path = folder_path / f"{timestamp}_summary.md"
                with summary_path.open("w", encoding="utf-8") as f:
                    f.write(summary_md)
                
                # 將摘要存入向量資料庫
                qdrant_manager = QdrantManager(EMBEDDING_MODEL)
                qdrant_manager.split_and_add_summary(summary_md, folder_name=timestamp)

            except Exception as e:
                print(f"生成摘要時發生錯誤：{str(e)}")
                # 繼續執行，不中斷上傳流程
            
            print(f"參考資料儲存至：{folder_path}")
            
            return {
                "status": "success",
                "message": "PDF 和 Markdown 檔案已成功儲存",
                "folder_name": timestamp,
                "folder_path": str(folder_path),
                "pdf_path": str(pdf_path),
                "markdown_path": str(markdown_path),
                "summary_path": str(summary_path),
                "file_size_mb": f"{file_size / 1024 / 1024:.2f}MB"
            }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"處理失敗：{str(e)}"
        )



@app.delete("/api/reference/{folder_name}")
async def delete_reference(folder_name: str):
    """移除參考資料資料夾(包含原始上傳的PDF檔案、Markdown、摘要)"""
    try:
        folder_path = REFERENCES_PATH / folder_name
        
        # 確認資料夾存在
        if not folder_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"找不到資料夾：{folder_name}"
            )
        
        # 刪除資料夾及其內容
        shutil.rmtree(folder_path)
        
        # 刪除向量資料庫中的摘要
        qdrant_manager = QdrantManager(EMBEDDING_MODEL)
        qdrant_manager.delete_summary(folder_name)
        
        return {
            "status": "success",
            "message": f"已成功刪除資料夾：{folder_name}",
            "deleted_path": str(folder_path)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"刪除失敗：{str(e)}"
        )



@app.get("/api/references")
async def list_references():
    """列出所有參考資料(包含所有原始上傳的PDF檔案、Markdown、摘要)"""
    try:
        references = []
        for folder_path in REFERENCES_PATH.iterdir():
            if folder_path.is_dir():
                # 取得資料夾內的檔案
                files = list(folder_path.glob("*"))
                references.append({
                    "folder_name": folder_path.name,
                    "folder_path": str(folder_path),
                    "files": [str(f) for f in files],
                    "created_time": datetime.fromtimestamp(folder_path.stat().st_ctime).strftime("%Y-%m-%d %H:%M:%S")
                })
        
        return {
            "status": "success",
            "references": sorted(references, key=lambda x: x["created_time"], reverse=True)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"獲取參考資料列表失敗：{str(e)}"
        )



@app.post("/api/generate/script/prompt")
async def generate_from_prompt(inputs: PromptInput) -> PodcastScript:
    """從 Prompt 生成 Podcast 對話腳本"""

    output = prompt_graph.invoke({
        "topic": inputs.topic,  
        "max_analysts": inputs.max_analysts,
        "host_name": inputs.host_name,
        "host_background": inputs.host_background,
        "guest_name": inputs.guest_name,
        "guest_background": inputs.guest_background
    })

    return output


@app.post("/api/generate/script/pdf")
async def generate_from_pdf(
    pdf_file: UploadFile = File(...),
    host_name: str = Form(...),
    host_background: str = Form(...),
    guest_name: str = Form(...),
    guest_background: str = Form(...)
) -> PodcastScript:
    """從 PDF 生成 Podcast"""
    try:
        # 先上傳為臨時檔案
        upload_response = await upload_pdf(pdf_file, is_temporary=True)
        
        if upload_response["status"] != "success":
            raise HTTPException(status_code=500, detail="PDF 上傳失敗")
            
        temp_file_path = upload_response["file_path"]
        temp_folder = upload_response["temp_folder"]
        
        try:
            # 使用臨時檔案路徑呼叫 pdf_graph
            output = pdf_graph.invoke({
                "pdf_path": temp_file_path,
                "host_name": host_name,
                "host_background": host_background,
                "guest_name": guest_name,
                "guest_background": guest_background
            })
            
            return output
            
        finally:
            # 處理完成後刪除臨時檔案
            await delete_temp(temp_folder)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.post("/api/generate/script/arxiv")
async def generate_script_from_arxiv(request: ArxivScriptRequest):
    """從 arXiv 論文生成 Podcast 腳本"""
    try:
        print(f"收到 arXiv 請求: {request}")
        
        # 驗證 URL 格式
        if not request.arxiv_url.startswith('https://arxiv.org/abs/'):
            raise HTTPException(
                status_code=400,
                detail="無效的 arXiv URL 格式"
            )
        
        try:
            # 使用 arxiv_graph 生成腳本
            output = arxiv_graph.invoke({
                "arxiv_url": request.arxiv_url,
                "host_name": request.host_name,
                "host_background": request.host_background,
                "guest_name": request.guest_name,
                "guest_background": request.guest_background
            })
            
            # 驗證輸出格式
            if not isinstance(output, dict) or 'dialogue' not in output:
                print(f"非預期的輸出格式: {output}")
                raise ValueError("生成的腳本格式不正確")
                
            print(f"生成的腳本: {output}")
            return output
            
        except ValueError as e:
            print(f"生成腳本時發生錯誤: {str(e)}")
            raise HTTPException(
                status_code=400,
                detail=str(e)
            )
        except Exception as e:
            print(f"生成腳本時發生未預期錯誤: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"生成腳本時發生錯誤: {str(e)}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"處理請求時發生未預期錯誤: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"處理請求時發生錯誤: {str(e)}"
        )



@app.delete("/api/temp/{folder_name}")
async def delete_temp(folder_name: str):
    """刪除臨時檔案資料夾"""
    try:
        folder_path = TEMP_PATH / folder_name
        if folder_path.exists():
            shutil.rmtree(folder_path)
        return {
            "status": "success",
            "message": f"臨時檔案已刪除：{folder_name}"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"刪除失敗：{str(e)}"
        )



@app.get("/api/reference/{folder_name}/pdf")
async def get_pdf(folder_name: str):
    """提供 PDF 檔案的存取"""
    try:
        folder_path = REFERENCES_PATH / folder_name
        if not folder_path.exists():
            raise HTTPException(status_code=404, detail="資料夾不存在")
            
        pdf_files = list(folder_path.glob("*_original.pdf"))
        if not pdf_files:
            raise HTTPException(status_code=404, detail="找不到 PDF 檔案")
            
        pdf_file = pdf_files[0]
        
        if not pdf_file.is_file():
            raise HTTPException(status_code=404, detail="PDF 檔案不存在")
            
        headers = {
            'Content-Disposition': f'inline; filename="{folder_name}.pdf"',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
            'Access-Control-Allow-Headers': '*'
        }
            
        return FileResponse(
            path=pdf_file,
            media_type="application/pdf",
            filename=f"{folder_name}.pdf",
            headers=headers
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"PDF 檔案存取失敗：{str(e)}"
        )



@app.post("/api/synthesize/stream")
async def synthesize_script_stream(request_data: RequestData):
    """串流式生成 Podcast 語音"""
    try:
        # 使用預設或自訂的語音設定
        voice_settings = request_data.voice_settings
        print(f"收到的語音設定: {voice_settings}")
        
        if not voice_settings:
            print("使用預設語音設定")
            voice_settings = VoiceSettings()
        
        # 建立語音合成器並設定語音
        synthesizer = PodcastSynthesizer(
            host_voice=voice_settings.host_voice,
            guest_voice=voice_settings.guest_voice
        )
        
        print(f"使用語音設定 - 主持人: {voice_settings.host_voice}, 來賓: {voice_settings.guest_voice}")

        async def generate():
            async for result in synthesizer.process_segments(request_data.script.dict()):
                yield json.dumps(result, ensure_ascii=False).encode('utf-8') + b'\n'

        return StreamingResponse(
            generate(),
            media_type='application/x-ndjson'
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"語音合成錯誤：{str(e)}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@app.post("/api/synthesize/preview")
async def preview_voice(request: PreviewRequest):
    try:
        if request.service == "azure":
            # 檢查環境變數
            speech_key = os.getenv("SPEECH_KEY")  # 改用與其他地方相同的環境變數名稱
            speech_region = os.getenv("SPEECH_REGION")
            
            if not speech_key or not speech_region:
                raise HTTPException(
                    status_code=500,
                    detail="未設定 Azure 語音服務的認證資訊"
                )
            
            print(f"使用 Azure 設定 - Region: {speech_region}")
            
            # 設定 Azure 語音服務
            speech_config = speechsdk.SpeechConfig(
                subscription=speech_key,
                region=speech_region
            )
            
            # 設定語音合成器
            speech_config.speech_synthesis_voice_name = request.voice
            synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=speech_config,
                audio_config=None
            )
            
            # 使用 SSML 合成語音
            ssml = f"""
            <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="zh-TW">
                <voice name="{request.voice}">
                    {request.text}
                </voice>
            </speak>
            """
            
            print(f"開始合成語音預覽 - Voice: {request.voice}")
            
            # 合成語音
            result = synthesizer.speak_ssml_async(ssml).get()
            
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                # 將音頻數據轉換為 BytesIO 對象
                audio_stream = io.BytesIO(result.audio_data)
                audio_stream.seek(0)
                
                print("語音預覽合成成功")
                
                # 返回音頻串流
                return StreamingResponse(
                    audio_stream,
                    media_type="audio/wav",
                    headers={
                        "Content-Disposition": "attachment; filename=preview.wav"
                    }
                )
            else:
                error_msg = f"語音合成失敗: {result.reason}"
                if result.reason == speechsdk.ResultReason.Canceled:
                    cancellation_details = result.cancellation_details
                    error_msg += f"\n取消原因: {cancellation_details.reason}"
                    error_msg += f"\n錯誤詳情: {cancellation_details.error_details}"
                
                print(f"語音合成失敗: {error_msg}")
                raise HTTPException(
                    status_code=500,
                    detail=error_msg
                )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"不支援的語音服務: {request.service}"
            )
            
    except Exception as e:
        error_msg = f"語音預覽失敗: {str(e)}"
        print(error_msg)
        import traceback
        print(f"詳細錯誤:\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=error_msg
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)