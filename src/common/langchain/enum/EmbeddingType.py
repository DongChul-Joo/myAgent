from enum import Enum

class HuggingFaceEmbeddingModelName(Enum):
    MULTILINGUAL_E5_BASE = 'intfloat/multilingual-e5-base'
    MULTILINGUAL_E5_LARGE = 'intfloat/multilingual-e5-large'
    KO_SROBERTA_MULTITASK = 'jhgan/ko-sroberta-multitask'
    KO_SBERT_NLI = 'jhgan/ko-sbert-nli'
    LABSE = 'sentence-transformers/LaBSE'
    
class EmbeddingDeviceType(Enum):
    CPU = 'cpu'
    GPU = 'gpu'
    
class EmbeddingModelType(Enum):
    OPENAI = "OpenAI"
    HUGGINGFACE = "Huggingface"

    @classmethod
    def _missing_(cls, value):
        # Custom logic to handle string inputs and convert them to enum members
        if isinstance(value, str):
            value = value.upper()
            if value in cls.__members__:
                return cls.__members__[value]
        raise ValueError(f'{value} is not a valid {cls.__name__}')