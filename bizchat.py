import os  # 파일 경로 설정 등에 사용
import sys  # 한글 출력 인코딩에 사용
import io  # 한글 출력 인코딩에 사용
from langchain import hub
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from collections import Counter
from dotenv import load_dotenv
import pdfplumber

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

# PDF 파일을 빠르게 로드하는 FastPDFLoader 클래스 정의
class FastPDFLoader:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def load(self):
        documents = []
        with pdfplumber.open(self.file_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    documents.append(text)
        return documents

# 다양한 파일 형식 로더를 적용할 수 있도록 CustomDirectoryLoader 정의
class CustomDirectoryLoader:
    def __init__(self, directory):
        self.directory = directory
        self.loader_map = {
            ".pdf": FastPDFLoader,  # FastPDFLoader로 PDF 파일 처리
            ".txt": UTF8TextLoader,  # 텍스트 파일 처리
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
                # print(f"Unsupported file format: {filename}")
                pass
        
        return documents

# ./data 폴더에서 PDF 및 TXT 파일 로드
loader = CustomDirectoryLoader("./data")
documents = loader.load()

# 텍스트 분할 설정
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)  # 분할 토큰수(chunk, 오버랩 정도)
texts = text_splitter.split_documents(documents)

# OpenAIEmbeddings 클래스를 사용하여 벡터스토어 생성
embedding = OpenAIEmbeddings()

# 벡터스토어를 생성합니다.
vectorstore = FAISS.from_documents(documents=texts, embedding=embedding)
retriever = vectorstore.as_retriever()

# 벡터스토어를 디스크에 저장
vectorstore.save_local("vectorstore_data")

# 나중에 벡터스토어를 로드
vectorstore = FAISS.load_local("vectorstore_data", embedding)

# OpenAI를 사용하여 대화 모델 생성
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

llm = ChatOpenAI(model_name="gpt-4o", temperature=0)

# 체인을 생성합니다.
rag_chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

from langchain_teddynote.messages import stream_response

# 질문을 받습니다.
recieved_question = sys.argv[1]

# 답변 생성
answer = rag_chain.stream(recieved_question)
stream_response(answer)

docs = loader.load()
# print(f"문서의 수: {len(docs)}")
docs