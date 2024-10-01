import os
import sys
import io
import requests
from bs4 import BeautifulSoup
import pandas as pd
from langchain import hub
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader, TextLoader
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from io import BytesIO

load_dotenv()
os.getenv("OPENAI_API_KEY")

# 경로 추적을 위한 설정
os.environ["PWD"] = os.getcwd()

# 출력 인코딩을 UTF-8로 설정
sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding='utf-8')

# UTF-8로 인코딩된 텍스트 로더 클래스 정의
class UTF8TextLoader(TextLoader):
    def __init__(self, file_path: str):
        super().__init__(file_path, encoding="utf-8")

# URL로부터 파일을 다운로드하여 텍스트로 처리하는 함수 추가
class URLLoader:
    def __init__(self, url):
        self.url = url

    def load(self):
        response = requests.get(self.url)
        if response.status_code == 200:
            # PDF 파일 처리
            if self.url.endswith(".pdf"):
                return PyPDFLoader(BytesIO(response.content)).load()
            # 텍스트 파일 처리
            elif self.url.endswith(".txt"):
                return [response.text]
            # 일반 웹 페이지 처리 (HTML)
            else:
                soup = BeautifulSoup(response.content, "html.parser")
                # 페이지에서 텍스트만 추출
                text = soup.get_text(separator="\n")
                return [text]
        else:
            print(f"Failed to fetch data from {self.url}")
            return []

# CSV 파일 로더 추가
class CSVLoader:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def load(self):
        try:
            # pandas를 사용하여 CSV 파일을 읽음
            df = pd.read_csv(self.file_path)
            # 모든 데이터를 텍스트로 변환
            text_data = df.to_string(index=False)
            return [text_data]
        except Exception as e:
            print(f"Error loading CSV file: {e}")
            return []

# 다양한 파일 형식 로더를 적용할 수 있도록 CustomDirectoryLoader 정의
class CustomDirectoryLoader:
    def __init__(self, directory):
        self.directory = directory
        self.loader_map = {
            ".pdf": PyPDFLoader,
            ".txt": UTF8TextLoader,  # 텍스트 파일 처리
            ".csv": CSVLoader,       # CSV 파일 처리 추가
        }

    def load(self):
        documents = []
        for filename in os.listdir(self.directory):
            filepath = os.path.join(self.directory, filename)
            ext = os.path.splitext(filename)[1].lower()  # 파일 확장자 추출

            if ext in self.loader_map:
                loader_cls = self.loader_map[ext]
                loader = loader_cls(filepath)
                documents.extend(loader.load())  # 로드된 문서를 추가
            else:
                pass
        
        return documents

# 사용자로부터 질문을 입력받음
recieved_question = input("질문을 입력하세요: ")

# 로컬 디렉토리의 데이터를 로드
loader = CustomDirectoryLoader("./data")
documents = loader.load()

# URL에서 데이터를 추가로 로드
url = input("참조할 URL을 입력하세요: ")
if url:
    url_loader = URLLoader(url)
    documents.extend(url_loader.load())

# 텍스트 분할 설정
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
texts = text_splitter.split_documents(documents)

# OpenAIEmbeddings 클래스를 사용하여 벡터스토어 생성
embedding = OpenAIEmbeddings()
vectorstore = FAISS.from_documents(documents=texts, embedding=embedding)
retriever = vectorstore.as_retriever()

# 프롬프트 템플릿 생성
from langchain_core.prompts import PromptTemplate

prompt = PromptTemplate.from_template(
    """당신은 질문-답변(Question-Answering)을 수행하는 친절한 AI 어시스턴트입니다. 당신의 임무는 주어진 문맥(context) 에서 주어진 질문(question) 에 답하는 것입니다.
검색된 다음 문맥(context) 을 사용하여 질문(question) 에 답하세요. 만약, 주어진 문맥(context) 에서 답을 찾을 수 없다면, 답을 모른다면 `주어진 정보에서 질문에 대한 정보를 찾을 수 없습니다` 라고 답하세요.
한글로 답변해 주세요. 단, 기술적인 용어나 이름은 번역하지 않고 그대로 사용해 주세요. 답변은 3줄 이내로 요약해 주세요.

#Question:
{question}

#Context:
{context}

#Answer:"""
)

llm = ChatOpenAI(model_name="gpt-4", temperature=0)

# 체인 생성
rag_chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# 질문을 처리하고 답변을 스트리밍
answer = rag_chain.invoke(recieved_question)
print(answer)