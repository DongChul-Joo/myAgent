import os
import shutil
import uuid
from langchain_community.vectorstores import Chroma
from langchain.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from langchain.schema import Document
from langchain_community.document_transformers import LongContextReorder
from langchain.storage import LocalFileStore
from langchain.retrievers.multi_vector import MultiVectorRetriever


CHROMA_SAVE_PATH = "/workspace/resource/index/chroma"
CHROMA_TEMP_SAVE_PATH = "/workspace/resource/tempindex/chroma"

DOCSTORE_PATH = "/workspace/resource/tempindex/docstore"

MULTI_VECTOR_ID_KEY = "doc_id"

def getIndexSaveDir():
    return CHROMA_SAVE_PATH

def getIndexSaveTempDir():
    return CHROMA_TEMP_SAVE_PATH

def getDocStore():
    return LocalFileStore(directory_path=DOCSTORE_PATH)

def getVectorStore(indexId: str, embeddingModel):
    indexPath = os.path.join(CHROMA_SAVE_PATH, indexId)
    return Chroma(persist_directory=indexPath, embedding_function=embeddingModel)

def getMultiVectorRetriever(indexId: str, embeddingModel):
    retriever = MultiVectorRetriever(
        vectorstore=getVectorStore(indexId, embeddingModel),
        docstore=getDocStore(),
        id_key=MULTI_VECTOR_ID_KEY,
    )
    
    return retriever

def mergeVectorStore(vectorStoreA, vectorStoreB):
    documents_b = vectorStoreB.get_all_documents()
    vectorStoreA.add_documents(documents_b)
    # vectorStoreA는 자동으로 persist_directory에 저장됨

def deleteVectorStore(indexId: str):
    operatePath = os.path.join(CHROMA_SAVE_PATH, indexId)
    
    try:
        if os.path.exists(operatePath):
            if os.path.isdir(operatePath):
                shutil.rmtree(operatePath)  # 디렉토리와 그 하위 파일들 모두 삭제
            else:
                os.remove(operatePath)  # 파일 삭제
    except Exception as e:
        return
    
# 문서를 벡터 저장소와 문서 저장소에 추가하는 MultiVector
def addSummariesMultiVectorDocument(retriever, childContentsList, parentContentsList):

    doc_ids = [
        str(uuid.uuid4()) for _ in parentContentsList
    ]  # 문서 내용마다 고유 ID 생성
    childDocumentList = [
        Document(page_content=childContents, metadata={MULTI_VECTOR_ID_KEY: doc_ids[i]})
        for i, childContents in enumerate(childContentsList)
    ]
    retriever.vectorstore.add_documents(
        childDocumentList
    )  # 요약 문서를 벡터 저장소에 추가
    retriever.docstore.mset(
        list(zip(doc_ids, parentContentsList))
    )  # 문서 내용을 문서 저장소에 추가
    
    return retriever
        
"""
Vector store 색인 파일 생성
"""
def createIndexing(
    embeddingModel, 
    documentList: list[Document], 
    indexId: str
):
    try:
        vectorstore = Chroma.from_documents(
            documents=documentList, 
            embedding_function=embeddingModel, 
            persist_directory=os.path.join(CHROMA_SAVE_PATH, indexId)
        )
        # 자동으로 persist_directory에 저장됨
        return vectorstore
    except Exception as e:
        raise e
    
"""
Vector store 임시 색인 파일 생성
"""
def createTempIndexing(
    embeddingModel, 
    documentList: list[Document], 
    indexId: str
):
    try:
        vectorstore = Chroma.from_documents(
            documents=documentList, 
            embedding_function=embeddingModel, 
            persist_directory=os.path.join(CHROMA_TEMP_SAVE_PATH, indexId)
        )
        # 자동으로 persist_directory에 저장됨
        return vectorstore
    except Exception as e:
        raise e

def getEnsembleRetrieverSearch(
    vectorStore,
    sparseSearchCnt : int,     
    densePassageSearchCnt : int, 
    sparseRetrieverWeights : float,
    densePassageRetrieverWeights : float,
    query : str,
    longContextReorderSortFlag : bool):
    

    allSearch_vector_retriever = vectorStore.as_retriever(search_kwargs={"k": len(vectorStore.index_to_docstore_id)}) 
    
    allDocument = allSearch_vector_retriever.invoke(query)

    bm25_retriever = BM25Retriever.from_documents(
        allDocument
    )

    bm25_retriever.k = sparseSearchCnt
    
    vector_retriever = vectorStore.as_retriever(search_kwargs={"k": densePassageSearchCnt})
    
    ensemble_retriever = EnsembleRetriever(
        retrievers=[bm25_retriever , vector_retriever] , weights = [sparseRetrieverWeights , densePassageRetrieverWeights]
    )

    searchResult = ensemble_retriever.get_relevant_documents(query)
    
    if longContextReorderSortFlag : 
        searchResult = LongContextReorder().transform_documents(searchResult)
    
    return searchResult

def getSimilarityRetrieverSearch(
    vectorStore,
    searchCnt : int,
    query : str,
    longContextReorderSortFlag : bool):
    
    vector_retriever = vectorStore.as_retriever(search_kwargs={"k": searchCnt})

    searchResult = vector_retriever.get_relevant_documents(query)
    
    if longContextReorderSortFlag : 
        searchResult = LongContextReorder().transform_documents(searchResult)
    
    return searchResult

def getSimilarityRetrieverSearchScore(
    vectorStore,
    searchCnt : int,
    query : str,
    longContextReorderSortFlag : bool):
    
    #vector_retriever = vectorStore.as_retriever(search_kwargs={"k": searchCnt})

    searchResult = vectorStore.similarity_search_with_score(query)
    
    if longContextReorderSortFlag : 
        searchResult = LongContextReorder().transform_documents(searchResult)
    
    return searchResult

def getKeywortRetrieverSearch(
    vectorStore,
    searchCnt : int,
    query : str,
    longContextReorderSortFlag : bool):
    

    allSearch_vector_retriever = vectorStore.as_retriever(search_kwargs={"k": len(vectorStore.index_to_docstore_id)}) 
    
    allDocument = allSearch_vector_retriever.get_relevant_documents(query)

    bm25_retriever = BM25Retriever.from_documents(
        allDocument
    )

    bm25_retriever.k = searchCnt

    searchResult = bm25_retriever.get_relevant_documents(query)
    
    if longContextReorderSortFlag : 
        searchResult = LongContextReorder().transform_documents(searchResult)
    
    return searchResult
    