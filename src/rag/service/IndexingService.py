import uuid
import os

from fastapi import UploadFile , File

from ...common.langchain.util import LangchainFileUtil
from ...common.langchain.util import LangchainVectorStoreUtil
from ...common.langchain.util import LangchainEmbeddingUtil
from ...common.langchain.util import LangchainFileUtil
from ...common.langchain.util import LangchainTextSplitterUtil

from ...common.langchain.enum.EmbeddingType import EmbeddingModelType
from ...common.langchain.enum.TextSpliterType import SplitOptionType ,SemanticChunkerType

from ..dto.IndexingDto import *

async def postParentDocumentIndexing(fileList: list[UploadFile] = File(...)):
    indexId = str(uuid.uuid4())
    fileInfoList = []
    saveVectorStore = None
    for file in fileList:
      fileId = str(uuid.uuid4())
      fileName, extension = os.path.splitext(file.filename)
          
      await LangchainFileUtil.saveFile(fileId,file)

      documentList = LangchainFileUtil.readFileByLoader(      
        fileId= fileId , 
        fileName = file.filename ,
        loader='readPyPDF2'
      )
            
      embeddingModel = LangchainEmbeddingUtil.getEmbeddingModel(modelType = EmbeddingModelType.HUGGINGFACE , modelName = "intfloat/multilingual-e5-large" , normalizeEmbeddings = True)

      splitDocumentList = LangchainTextSplitterUtil.getSemanticChunkerDocumentSplit(
        embeddingModel=embeddingModel , 
        thresholdType=SemanticChunkerType.PERCENTILE.name.lower() , 
        threshold=90 , 
        documentList=documentList
      )
          
      vectorstore = LangchainVectorStoreUtil.getVectorStore(embeddingModel)
      
      childSplitter = LangchainTextSplitterUtil.getRecursiveCharacterTextSplitter(
        chunkSize=300 , 
        chunkOverlapSize=0 , 
        splitType=SplitOptionType.TOKENS.value
      )
      
      # 부모문서 검색기 생성및 저장
      retriever = LangchainVectorStoreUtil.getParentDocumentRetriever(vectorstore , childSplitter)
      retriever.add_documents(splitDocumentList)
      
      if saveVectorStore : 
        saveVectorStore = LangchainVectorStoreUtil.mergeVectorStore(saveVectorStore , retriever.vectorstore)
      else:
        saveVectorStore = retriever.vectorstore

      fileInfo = FileInfo(
          uuid = fileId,
          fullName = file.filename,
          name = fileName,
          extension= extension,
      )
      
      fileInfoList.append(fileInfo)    
    LangchainVectorStoreUtil.saveVectorStore( indexId , saveVectorStore)
    return ParentDocumentIndexingResponseDto(uuid = indexId , fileInfoList = fileInfoList)
