from dataclasses import dataclass,asdict
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import ContentFormat
from langchain_openai.chat_models import AzureChatOpenAI
from langchain_huggingface.embeddings import HuggingFaceEmbeddings

print("Loading Configurations...")

@dataclass
class OpenAI4oConfig:
    api_key:str = "312ff50d6d954023b8748232617327b6"
    azure_endpoint:str = "https://openai-lh.openai.azure.com"
    azure_deployment:str = "GPT4o"
    api_version:str = "2024-02-01"

@dataclass
class ChromaClientDEV:
    host:str="http://52.172.103.119:6062"
    port:int=8000
    
    
@dataclass
class DocIntelligence:
    endpoint:str="https://ikegaidocint.cognitiveservices.azure.com/"
    api_key:str="75c1d85d65be420aa7da6e4ed0a80ad0"
    

llm=AzureChatOpenAI(**asdict(OpenAI4oConfig()))
doc_intelligence=DocumentIntelligenceClient(endpoint=DocIntelligence().endpoint,
                                                    credential=AzureKeyCredential(DocIntelligence().api_key))
embedding=HuggingFaceEmbeddings(model_name="mixedbread-ai/mxbai-embed-large-v1")

all_config={
    "llm":llm,
    "doc_intelligence":doc_intelligence,
    "embedding":embedding
}
ENV="WIN"#"MAC"



print("Configurations Loaded!!!")
