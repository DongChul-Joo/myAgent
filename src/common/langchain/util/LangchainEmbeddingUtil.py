import os

from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings

from ..enum.EmbeddingType import *
from ...ComEnv import commonEnvs
from sentence_transformers import SentenceTransformer



WORKDIR_PATH = os.getcwd()

EMBEDDING_MODEL_SAVE_PATH = WORKDIR_PATH+"/resource/embedding-model"

def downloadEmbeddingModel(embeddingModelName : str):
    downloadModel = SentenceTransformer(embeddingModelName)
    embeddingModelPath = os.path.join(EMBEDDING_MODEL_SAVE_PATH, embeddingModelName)
    downloadModel.save(embeddingModelPath)


def existLocalEmbeddingModel(embeddingModelName : str):
    embeddingModelPath = os.path.join(EMBEDDING_MODEL_SAVE_PATH, embeddingModelName)
    return os.path.exists(embeddingModelPath)
    
def getEmbeddingModel(modelType : EmbeddingModelType , modelName : str , normalizeEmbeddings : bool  = True , apiBase : str = None, apikey : str = None):
    embeddingModel = None
        
    if modelType == EmbeddingModelType.OPENAI:
        embeddingModel = getOpenaiEmbeddingModel(apiBase , modelName , apikey)
    elif modelType == EmbeddingModelType.HUGGINGFACE:
        embeddingModel = getFreeEmbeddingModel(EMBEDDING_MODEL_SAVE_PATH + '/' + modelName , commonEnvs.DEVICE , normalizeEmbeddings)
    
    return embeddingModel

def getFreeEmbeddingModel(modelSavePath : str , device : str , normalizeEmbeddings : bool):
    try:
        modelName = modelSavePath
        modelKwargs = {'device' : device}
        encodeKwargs = {'normalize_embeddings' : normalizeEmbeddings}
        
        embeddings = HuggingFaceEmbeddings(
            model_name = modelName ,
            model_kwargs = modelKwargs , 
            encode_kwargs = encodeKwargs
        )
        return embeddings
    except Exception as e:
        raise e

def getOpenaiEmbeddingModel(openaiApiBase : str , modelName : str , apikey : str):
    try:
        #DefaultOpenAI 호출
        if openaiApiBase == None or openaiApiBase == "":
            openaiApiBase = None
            
        if modelName == None or modelName == "":
            modelName = "text-embedding-ada-002"
            
        embeddings = OpenAIEmbeddings(
            openai_api_base=openaiApiBase , 
            model=modelName ,
            openai_api_key=apikey
        )   
        return embeddings
    except Exception as e:
        raise e 

def getFreeEmbeddingQuery(modelSavePath : str , device : str , normalizeEmbeddings : bool , query : str):
    try:        
        embeddingModel = getFreeEmbeddingModel(modelSavePath , device , normalizeEmbeddings)
        return embeddingModel.embed_query(query)
    except Exception as e:
        raise e
        
        
def getOpenaiEmbeddingQuery(openaiApiBase : str , modelName : str , apikey : str , query : str):
    try:
        embeddingModel = getOpenaiEmbeddingModel(openaiApiBase , modelName , apikey)
        return embeddingModel.embed_query(query)
    except Exception as e:
        raise e