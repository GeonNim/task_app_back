import os # 파일 경로 설정 등에 사용
import sys # 한글 출력 인코딩에 사용
import io # 한글 출력 인코딩에 사용
from langchain import hub
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader, TextLoader
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from collections import Counter
# from langchain.schema import Document  # Document 클래스 임포트
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv

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

# 다양한 파일 형식 로더를 적용할 수 있도록 CustomDirectoryLoader 정의
class CustomDirectoryLoader:
    def __init__(self, directory):
        self.directory = directory
        self.loader_map = {
            ".pdf": PyPDFLoader,
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



text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200) # 분할 토큰수(chunk, 오버랩 정도)
texts = text_splitter.split_documents(documents)
# print(f"분할된 텍스트 뭉치의 갯수: {len(texts)}")

# OpenAIEmbeddings 클래스를 사용하여 백터스토어 생성
embedding = OpenAIEmbeddings()
# 벡터스토어를 생성합니다.
vectorstore = FAISS.from_documents(documents=texts, embedding=embedding)
retriever = vectorstore.as_retriever()
# print(texts[0])

# query = "신혼부부를 위한 정책을 알려주세요."
# docs = retriever.invoke(query)  # 변경된 메서드 사용
# print("유사도가 높은 텍스트 개수: ", len(docs))
# print("--" * 20)
# print("유사도가 높은 텍스트 중 첫 번째 텍스트 출력: ", docs[0])
# print("--" * 20)
# print("유사도가 높은 텍스트들의 문서 출처: ")
# for doc in docs:
#   print(doc.metadata["source"])
#   pass

# OpenAPI를 사용하여 대화 모델 생성 사전 주문
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

llm=ChatOpenAI(model_name="gpt-4o", temperature=0)

# 체인을 생성합니다.
# RunnablePassthrough() : 데이터를 그래도 전달하는 역할. invoke() 메서드를 통해 입력된 데이터를 그대로 반환
# StrOutputParser() : LLM이나 chatModel에서 나오는 언어 몸델의 출력을 문자열 형식으로 변환
rag_chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

from langchain_teddynote.messages import stream_response

recieved_question = sys.argv[1];
# print("질문: ", recieved_question)

answer = rag_chain.stream(recieved_question)
stream_response(answer)

# print(answer)

docs = loader.load()
# print(f"문서의 수: {len(docs)}")
docs