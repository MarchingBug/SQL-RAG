import logging
import azure.functions as func
from azure.storage.blob import BlobServiceClient, BlobSasPermissions, generate_blob_sas,generate_container_sas,ContainerClient
from azure.storage.blob import ResourceTypes, AccountSasPermissions, generate_account_sas
#from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest, AnalyzeResult
from openai import AzureOpenAI
import os
import json
#import sys
import datetime
from datetime import datetime, timedelta,timezone
import pandas as pd
import os
import json
from pprint import pprint

from openai import AzureOpenAI
import tiktoken
from typing import Callable, List, Dict, Optional, Generator, Tuple, Union




#from azure.core.credentials import AzureKeyCredential
#from azure.core.credentials import AzureKeyCredential
#from azure.ai.formrecognizer import DocumentAnalysisClient
#from azure.ai.documentintelligence import DocumentIntelligenceClient
#from azure.ai.documentintelligence.models import AnalyzeDocumentRequest, AnalyzeResult
from openai import AzureOpenAI
import tiktoken


import os
import datetime
from datetime import datetime, timedelta,timezone

import pandas as pd
from typing import Callable, List, Dict, Optional, Generator, Tuple, Union


AZURE_ACC_NAME = os.environ["AZURE_ACC_NAME"]
AZURE_PRIMARY_KEY = os.environ["AZURE_PRIMARY_KEY"]
STORAGE_ACCOUNT_CONTAINER = os.environ["STORAGE_ACCOUNT_CONTAINER"]
AZURE_PRIMARY_KEY = os.environ["AZURE_PRIMARY_KEY"]
STORAGE_ACCOUNT_CONTAINER = os.environ["STORAGE_ACCOUNT_CONTAINER"]
#DESTINATION_ACCOUNT_CONTAINER = os.environ["DESTINATION_ACCOUNT_CONTAINER"]

SUMMARY_PARQUET_CONTAINER = os.environ["SUMMARY_PARQUET_CONTAINER"]
SUMMARY_CONTAINER = os.environ["SUMMARY_CONTAINER"]

OPENAI_ENDPOINT = os.environ["OPENAI_ENDPOINT"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
OPENAI_EMBEDDING_MODEL = os.environ["OPENAI_EMBEDDING_MODEL"]
OPENAI_API_MODEL =  os.environ["OPENAI_API_MODEL"]
OPENAI_MODEL_MAX_TOKENS = os.environ["OPENAI_MODEL_MAX_TOKENS"]



client = AzureOpenAI(
  azure_endpoint =  OPENAI_ENDPOINT, 
  api_key= OPENAI_API_KEY , 
  api_version="2024-02-15-preview"
)

def get_chat_completion(system_message, text):
    

    completion = client.chat.completions.create(
         model=OPENAI_API_MODEL,
        messages=[
         {"role": "system", "content": system_message},
    {"role": "user", "content": text}
        ]
    )

    print(completion.choices[0].message.content)
    return completion.choices[0].message.content


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    system_message = req.params.get('system_message')
    question = req.params.get('question')    
    
    if not system_message:
            try:
                req_body = req.get_json()
            except ValueError:
                pass
            else:
                system_message = req_body.get('system_message')
                question = req_body.get('question')
    
    if not system_message or system_message == "": 
         return func.HttpResponse(
             "Please pass a system_message and question on the query string or in the request body",
             status_code=400
        )
    else:   
        result = get_chat_completion(system_message, question)
        logging.info("resutls " + result)  
        return func.HttpResponse(result,status_code=200)
  
       