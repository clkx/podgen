import pdfplumber
import os

def pdf_to_markdown(pdf_content):
    """將 PDF 內容轉換為 Markdown 格式"""
    try:
        if not pdf_content or not isinstance(pdf_content, str):
            raise ValueError("PDF 路徑無效")
            
        if not os.path.exists(pdf_content):
            raise FileNotFoundError(f"找不到 PDF 檔案: {pdf_content}")
            
        markdown_content = []
        with pdfplumber.open(pdf_content) as pdf:
            if not pdf.pages:
                raise ValueError("PDF 檔案沒有內容")
                
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
                            
        if not markdown_content:
            raise ValueError("無法從 PDF 提取任何文字內容")
            
        return "".join(markdown_content)
        
    except Exception as e:
        print(f"PDF 處理過程發生錯誤: {str(e)}")
        raise


def pdf_reading_node(state):
    """get the pdf file from the temp folder"""
    try:
        if 'pdf_path' not in state:
            raise KeyError("狀態中缺少 pdf_path")
            
        pdf_path = state['pdf_path']
        print("---PDF READING---")
        pdf_markdown = pdf_to_markdown(pdf_path)
        
        if not pdf_markdown.strip():
            raise ValueError("轉換後的 Markdown 內容為空")
            
        return {"content": pdf_markdown}
        
    except Exception as e:
        print(f"PDF 讀取節點發生錯誤: {str(e)}")
        raise


if __name__ == "__main__":

    def print_pdf(pdf_path):
        pdf_markdown = pdf_to_markdown(pdf_path)
        print(pdf_markdown)

    print_pdf(r"backend\stores\temp\20241125_131213\20241125_131213_original.pdf")

