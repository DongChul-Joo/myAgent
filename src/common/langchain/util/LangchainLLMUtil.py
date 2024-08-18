
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableLambda, RunnablePassthrough

from . import LangchainFileUtil

class MyAgentOpenAI:
    llm : ChatOpenAI
    def __init__(self, modelName : str, temperature : int):
        self.llm = ChatOpenAI(model = modelName , temperature = temperature)
    
    def getLLM(self):
        return self.llm
    
    @staticmethod    
    def splitDocumentImageAndText(docs):
        """
        base64로 인코딩된 이미지와 텍스트 분리
        """
        base64ImageList = []
        textList = []
        for doc in docs:
            # 문서가 Document 타입인 경우 page_content 추출
            if isinstance(doc, Document):
                doc = doc.page_content
            if LangchainFileUtil.checkBase64Format(doc) and LangchainFileUtil.checkBase64FormatImage(doc):
                doc = LangchainFileUtil.resizeBase64Image(doc, size=(1300, 600))
                base64ImageList.append(doc)
            else:
                textList.append(doc)
        return {"base64ImageList": base64ImageList, "textList": textList}

    # 텍스트 요소의 요약 생성

    def generateTextSummaries(self , contentList : list[str] , maxConcurrency : int , prompt : str = None):
        """
        텍스트 요소 요약
        contentList: 문자열 리스트
        prompt: 요약 프롬프트
        maxConcurrency: 병렬처리수
        """

        if not prompt:
            # 프롬프트 설정
            prompt_text = """You are an assistant tasked with summarizing tables and text for retrieval. \
            These summaries will be embedded and used to retrieve the raw text or table elements. \
            Give a concise summary of the table or text that is well optimized for retrieval. Table or text: {element} """
            prompt = ChatPromptTemplate.from_template(prompt_text)

        # 텍스트 요약 체인
        summarize_chain = {"element": lambda x: x} | prompt | self.llm | StrOutputParser()

        # 요약을 위한 빈 리스트 초기화
        summariesContentList = []

        # 제공된 contentList에 대해 요약이 요청되었을 경우 적용
        if contentList:
            summariesContentList = summarize_chain.batch(contentList, {"max_concurrency": maxConcurrency})

        return summariesContentList

    def generateMultiModal(self , imageBase64 : str, prompt : str):
        # 이미지 요약을 생성합니다.

        msg = self.llm.invoke(
            [
                HumanMessage(
                    content=[
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{imageBase64}"},
                        },
                    ]
                )
            ]
        )
        return msg.content


    def generateImageSummaries(self , imageBase64List : list[str] , prompt : str = None):
        """
        이미지에 대한 요약과 base64 인코딩된 문자열을 생성합니다.
        path: Unstructured에 의해 추출된 .jpg 파일 목록의 경로
        """

        # 이미지 요약을 저장할 리스트
        imageSummariesList = []

        # 요약을 위한 프롬프트
        if not prompt:     
            prompt = """You are an assistant tasked with summarizing images for retrieval. \
            These summaries will be embedded and used to retrieve the raw image. \
            Give a concise summary of the image that is well optimized for retrieval."""

        # 이미지 요약 생성
        for imageBase64 in imageBase64List:
            imageSummariesList.append(self.generateMultiModal(imageBase64, prompt))

        return imageSummariesList
    
    @staticmethod  
    def createMyAgentMultiModalPrompt(splitDocumentImageAndTextDict):
        """
        컨텍스트를 단일 문자열로 결합
        """
        context = "\n".join(splitDocumentImageAndTextDict["context"]["texts"])
        contentList = []

        # 이미지가 있으면 메시지에 추가
        if splitDocumentImageAndTextDict["context"]["images"]:
            for image in splitDocumentImageAndTextDict["context"]["images"]:
                image_message = {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{image}"},
                }
                contentList.append(image_message)

        # 분석을 위한 프롬프트 추가
        analysisPrompt = {
            "type": "text",
            "text": (
                "You are financial analyst tasking with providing investment advice.\n"
                "You will be given a mixed of text, tables, and image(s) usually of charts or graphs.\n"
                "Use this information to provide investment advice related to the user question. Answer in Korean. Do NOT translate company names.\n"
                f"User-provided question: {splitDocumentImageAndTextDict['question']}\n\n"
                "Text and / or tables:\n"
                f"{context}"
            ),
        }
        contentList.append(analysisPrompt)
        return [HumanMessage(content=contentList)]


    def getMultiModalRagChain(self , retriever):
        """
        멀티모달 RAG 체인
        """

        # RAG 파이프라인
        chain = (
            {
                "context": retriever | RunnableLambda(MyAgentOpenAI.splitDocumentImageAndText),
                "question": RunnablePassthrough(),
            }
            | RunnableLambda(MyAgentOpenAI.createMyAgentMultiModalPrompt)
            | self.llm
            | StrOutputParser()
        )

        return chain