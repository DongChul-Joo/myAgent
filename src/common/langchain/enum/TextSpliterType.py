from enum import Enum

class LanguageType(Enum):
  CPP = 'cpp'
  GO = 'go'
  JAVA = 'java'
  KOTLIN = 'kotlin'
  JS = 'js'
  TS = 'ts'
  PHP = 'php'
  PROTO = 'proto'
  PYTHON = 'python'
  RST = 'rst'
  RUBY = 'ruby'
  RUST = 'rust'
  SCALA = 'scala'
  SWIFT = 'swift'
  MARKDOWN = 'markdown'
  LATEX = 'latex'
  HTML = 'html'
  SOL = 'sol'
  CSHARP = 'csharp'
  COBOL = 'cobol'
  
class SplitterType(Enum):
    NONE = 0
    CHARACTOR_SPLITTER = 1
    RECULSIVE_CHARACTOR_SPLITTER = 2
    SEMANTIC_CHUNKER = 3

    @classmethod
    def _missing_(cls, value):
        if isinstance(value, int):
            for member in cls:
                if member.value == value:
                    return member
        raise ValueError(f'{value} is not a valid {cls.__name__}')
    
class SplitOptionType(Enum):
    LENGTH = 0
    TOKENS = 1
    
    @classmethod
    def _missing_(cls, value):
        if isinstance(value, int):
            for member in cls:
                if member.value == value:
                    return member
        raise ValueError(f'{value} is not a valid {cls.__name__}')
      
class SemanticChunkerType(Enum):
    PERCENTILE = 0
    INTERQUARTILE = 1
    STANDART_DEVIATION = 2
    
    @classmethod
    def _missing_(cls, value):
        if isinstance(value, int):
            for member in cls:
                if member.value == value:
                    return member
        raise ValueError(f'{value} is not a valid {cls.__name__}')