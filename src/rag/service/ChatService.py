from ..dto.ChatDto import *
from ...common.langchain.util.LangchainLLMUtil import MyAgentOpenAI

async def postChat(req):
  myagent = MyAgentOpenAI(modelName="gpt-4o" , temperature=0)
