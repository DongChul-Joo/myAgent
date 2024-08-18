import uuid
import os
from fastapi import UploadFile , File

from ...common.langchain.util import LangchainFileUtil
from ...common.langchain.util import LangchainVectorStoreUtil
from ...common.langchain.util import LangchainEmbeddingUtil
from ...common.langchain.util import LangchainFileUtil
from ...common.langchain.util import LangchainTextSplitterUtil
from ...common.langchain.util.LangchainLLMUtil import MyAgentOpenAI

from ...common.langchain.enum.EmbeddingType import EmbeddingModelType
from ...common.langchain.enum.TextSpliterType import SplitOptionType

from ..dto.IndexingDto import *

async def postMultiVectorIndexing(fileList: list[UploadFile] = File(...)):
    indexId = str(uuid.uuid4())
    fileInfoList = []
    for file in fileList:
      fileId = str(uuid.uuid4())
      fileName, extension = os.path.splitext(file.filename)
          
      await LangchainFileUtil.saveFile(fileId,file)
      print('readMultiModalPDFLoader init@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')

      textList, tableList = LangchainFileUtil.readMultiModalPDFLoader(      
        fileId= fileId , 
        fileName = file.filename , 
        maxPartitionSize = 4000 , 
        newPartitionSize = 3800 , 
        combinePartitionSize = 2000
      )
      
      print(dict(textList))

      print(dict(tableList))
      
      textSplitter = LangchainTextSplitterUtil.getCharacterTextSplitter(
        separator=None , 
        chunkSize=4000 , 
        chunkOverlapSize=0 , 
        splitType=SplitOptionType.TOKENS.value
      )
      
      combineText = " ".join(textList)
      text4kTokenList = textSplitter.split_text(combineText)
      print(dict(text4kTokenList))

      fileContentsImageDirPath = LangchainFileUtil.getFileContentsImageDirPath(fileId)
      imageBase64List = LangchainFileUtil.getDirImageListToBase64(fileContentsImageDirPath)
      print(dict(imageBase64List))
      myAgentLLM = MyAgentOpenAI(modelName="gpt-4" , temperature=0)
    
      #summariesTestList = myAgentLLM.generateTextSummaries(contentList=text4kTokenList , maxConcurrency=5)
      #summariesTableList = myAgentLLM.generateTextSummaries(contentList=tableList , maxConcurrency=5)
      #summariesImageList = myAgentLLM.generateImageSummaries(imageBase64List=imageBase64List)
      
      #요약을 색인화하지만 원본 이미지나 텍스트를 반환하는 검색기를 생성합니다.
      embeddingModel = LangchainEmbeddingUtil.getEmbeddingModel(modelType = EmbeddingModelType.HUGGINGFACE , modelName = "intfloat/multilingual-e5-large" , normalizeEmbeddings = True)
      # 멀티 벡터 검색기 생성
      retriever = LangchainVectorStoreUtil.getMultiVectorRetriever(indexId , embeddingModel)
      
      #retriever = LangchainVectorStoreUtil.addSummariesMultiVectorDocument(retriever , summariesTestList, text4kTokenList)
      #retriever = LangchainVectorStoreUtil.addSummariesMultiVectorDocument(retriever , summariesTableList, tableList)
      #retriever = LangchainVectorStoreUtil.addSummariesMultiVectorDocument(retriever , summariesImageList, imageBase64List)
      
      fileInfo = FileInfo(
          uuid = fileId,
          fullName = file.filename,
          name = fileName,
          extension= extension,
      )
      
      fileInfoList.append(fileInfo)    
      
    return MultiVectorIndexingResponseDto(uuid = indexId , fileInfoList = fileInfoList)
