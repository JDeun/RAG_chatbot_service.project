import os
import tempfile
from langchain_community.document_loaders import (
    TextLoader, PDFMinerLoader, Docx2txtLoader, CSVLoader,
    UnstructuredHTMLLoader, UnstructuredMarkdownLoader, UnstructuredODTLoader,
    UnstructuredPowerPointLoader, UnstructuredEPubLoader, UnstructuredImageLoader,
    UnstructuredEmailLoader, JSONLoader, UnstructuredRTFLoader, UnstructuredXMLLoader,
    EverNoteLoader, UnstructuredExcelLoader
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI

# RAG 모델 초기화
def initialize_rag(vectorstore, llm):
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(),
        return_source_documents=True
    )
    return qa_chain

# 파일 포맷별 처리 및 임베딩
async def process_file(file):
    content = await file.read()
    
    loaders = {
        ".txt": TextLoader,
        ".pdf": PDFMinerLoader,
        ".docx": Docx2txtLoader,
        ".csv": CSVLoader,
        ".html": UnstructuredHTMLLoader,
        ".md": UnstructuredMarkdownLoader,
        ".odt": UnstructuredODTLoader,
        ".pptx": UnstructuredPowerPointLoader,
        ".epub": UnstructuredEPubLoader,
        ".jpg": UnstructuredImageLoader,
        ".jpeg": UnstructuredImageLoader,
        ".png": UnstructuredImageLoader,
        ".eml": UnstructuredEmailLoader,
        ".json": JSONLoader,
        ".rtf": UnstructuredRTFLoader,
        ".xml": UnstructuredXMLLoader,
        ".enex": EverNoteLoader,
        ".xlsx": UnstructuredExcelLoader,
        ".xls": UnstructuredExcelLoader,
    }
    
    file_extension = os.path.splitext(file.filename)[1].lower()
    if file_extension in loaders:
        loader_class = loaders[file_extension]
        
        # 임시 파일 생성
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            temp_file.write(content)
            temp_file_path = temp_file.name

        # 로더 생성 및 문서 로드
        loader = loader_class(temp_file_path)
        documents = loader.load()
        
        # 임시 파일 삭제
        os.unlink(temp_file_path)
        
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        texts = text_splitter.split_documents(documents)
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        vectorstore = Chroma.from_documents(texts, embeddings)
        return vectorstore
    else:
        raise ValueError("Unsupported file format")

# LLM 초기화
def initialize_llm(api_key):
    return ChatOpenAI(model_name="gpt-4o-mini", temperature=0, openai_api_key=api_key)