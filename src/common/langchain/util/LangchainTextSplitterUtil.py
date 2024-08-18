from langchain.text_splitter import (
    RecursiveCharacterTextSplitter,
    CharacterTextSplitter,
    Language
)
from langchain_experimental.text_splitter import SemanticChunker

from langchain.schema import Document
import tiktoken

from ..enum.TextSpliterType import *

from fastapi import HTTPException , status
    
tokenizer = tiktoken.get_encoding("cl100k_base")

def tiktoken_len(text : str):
    tokens = tokenizer.encode(text)
    return len(tokens)

def getContentTextSplit(                         
                        splitterType : int , 
                        textList : list[str] , 
                        chunkSize : int = None, 
                        chunkOverlapSize : int = None, 
                        splitOptionType : SplitOptionType = SplitOptionType.LENGTH, 
                        separator : str = None, 
                        embeddingModel : str = None,
                        semanticChunkerType : int = None,
                        semanticChunkerThreshold : float = None):
    result = None
    if splitterType == SplitterType.CHARACTOR_SPLITTER.value:
        if not chunkSize or separator: 
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Charactor ChunkSize or separator parameter missing")
        result = getCharacterTextSplit(textList , separator , chunkSize , chunkOverlapSize ,splitOptionType)
    elif splitterType == SplitterType.RECULSIVE_CHARACTOR_SPLITTER.value:
        if not chunkSize : 
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Reculsive ChunkSize parameter missing")
        result = getRecursiveCharacterTextSplit(textList , chunkSize , chunkOverlapSize , splitOptionType)
    elif splitterType == SplitterType.SEMANTIC_CHUNKER.value:
        if not embeddingModel or semanticChunkerType is None or semanticChunkerThreshold is None:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="SemanticChunker parameter missing")
        thresholdType = SemanticChunkerType(semanticChunkerType).name.lower()
        result = getSemanticChunkerTextSplit(embeddingModel,thresholdType,semanticChunkerThreshold,textList)
    return result

def getDocumentTextSplit( 
                        splitterType : int , 
                        documentList : list[Document] , 
                        chunkSize : int = None, 
                        chunkOverlapSize : int = None, 
                        splitOptionType : SplitOptionType = SplitOptionType.LENGTH, 
                        separator : str = None, 
                        embeddingModel : str = None,
                        semanticChunkerType : int = None,
                        semanticChunkerThreshold : float = None):
    
    #print(f"Function getDocumentTextSplit called with parameters: {locals()}")
    
    result = None
    if splitterType == SplitterType.CHARACTOR_SPLITTER.value:
        if not chunkSize or not separator: 
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Charactor ChunkSize or separator parameter missing")
        result = getCharacterDocumentSplit(documentList , separator , chunkSize , chunkOverlapSize , splitOptionType)
    
    elif splitterType == SplitterType.RECULSIVE_CHARACTOR_SPLITTER.value:
        if not chunkSize : 
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Reculsive ChunkSize parameter missing")
        result = getRecursiveCharacterDocumentSplit(documentList , chunkSize , chunkOverlapSize , splitOptionType)
    
    elif splitterType == SplitterType.SEMANTIC_CHUNKER.value:
        
        if not embeddingModel or semanticChunkerType is None or semanticChunkerThreshold is None:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="SemanticChunker parameter missing")
        
        thresholdType = SemanticChunkerType(semanticChunkerType).name.lower()
        result = getSemanticChunkerDocumentSplit(embeddingModel,thresholdType,semanticChunkerThreshold,documentList)
    return result

#RecursiveCharacterTextSplitter : 내부적으로 줄바꿈,마침표,쉼표 순으로 재귀적으로 분할하므로 Chunk Size 지켜서 분할됨 ----------------------------------------------------------------------

def getRecursiveCharacterTextSplitter( chunkSize : int , chunkOverlapSize : int , splitType: str ):
    
    length_function = len if splitType == SplitOptionType.TOKENS.value else tiktoken_len if splitType == SplitOptionType.LENGTH.value else len
    
    result = RecursiveCharacterTextSplitter(
        chunk_size = chunkSize,
        chunk_overlap = chunkOverlapSize,
        length_function = length_function,
        add_start_index = True
        #Strip_whitespace = True / True:시작,끝 공백 제거
    )
    
    return result


"""
text 청킹
return : List[str]
"""
def getRecursiveCharacterTextSplit( content : str , chunkSize : int , chunkOverlapSize : int , splitType: str):
    
    text_splitter = getRecursiveCharacterTextSplitter(chunkSize , chunkOverlapSize , splitType )
    
    result = text_splitter.split_text(content)
    
    return result

"""
문서 청킹
return : List[langchain.schema.Document]
"""
def getRecursiveCharacterDocumentSplit( document , chunkSize : int , chunkOverlapSize : int , splitType: str):  

    text_splitter = text_splitter = getRecursiveCharacterTextSplitter(chunkSize , chunkOverlapSize , splitType )
    
    result = []
    chunks = text_splitter.split_documents(document)
    result.extend(chunks)
    
    return result

#CharacterTextSplitter : 인자로 받는 구분자 하나로만 분할하여 Chunk Size over 발생 가능 ----------------------------------------------------------------------

"""
"""
def getCharacterTextSplitter(separator : str , chunkSize : int , chunkOverlapSize : int , splitType: str):
    
    length_function = len if splitType == SplitOptionType.TOKENS.value else tiktoken_len if splitType == SplitOptionType.LENGTH.value else len
    
    result = CharacterTextSplitter(
        separator=separator,
        chunk_size=chunkSize,     
        chunk_overlap=chunkOverlapSize,   
        length_function=length_function,
        is_separator_regex=False, #무슨 옵션인지 당최 안나옴
    )
    
    return result

"""
text 청킹
return : List[str]
"""
def getCharacterTextSplit(content : str , separator : str , chunkSize : int , chunkOverlapSize : int , splitType: str):
        
    text_splitter = getCharacterTextSplitter(separator , chunkSize , chunkOverlapSize , splitType)
    
    result = text_splitter.split_text(content)
    
    return result

"""
문서 청킹
return : List[langchain.schema.Document]
"""
def getCharacterDocumentSplit(document , separator : str , chunkSize : int , chunkOverlapSize : int , splitType: str):
    
    text_splitter = getCharacterTextSplitter(separator , chunkSize , chunkOverlapSize , splitType)
    
    result = []
    chunks = text_splitter.split_documents(document)
    result.extend(chunks)
    
    return result

#SemanticChunker : 유사도 기반 문맥 분할기 정해진 청크 사이즈가 없음 ----------------------------------------------------------------------
def getSemanticChunker(embeddingModel , thresholdType , threshold):
    result = SemanticChunker(
        embeddingModel,
        breakpoint_threshold_type = thresholdType,
        breakpoint_threshold_amount = threshold
    )
    return result

def getSemanticChunkerTextSplit(embeddingModel , thresholdType , threshold , textList : list):
    text_splitter = getSemanticChunker(embeddingModel , thresholdType , threshold)
    return text_splitter.create_documents(textList)

def getSemanticChunkerDocumentSplit(embeddingModel , thresholdType , threshold , documentList : list[Document]):
    text_splitter = getSemanticChunker(embeddingModel , thresholdType , threshold)
    return text_splitter.split_documents(documentList)

