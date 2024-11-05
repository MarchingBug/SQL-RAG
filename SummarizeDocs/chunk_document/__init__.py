import logging

import azure.functions as func
import os
import json

from azure.core.credentials import AzureKeyCredential
import azure.storage.blob
from azure.storage.blob import BlobServiceClient, BlobSasPermissions, generate_blob_sas,generate_container_sas,ContainerClient
from azure.storage.blob import ResourceTypes, AccountSasPermissions, generate_account_sas
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest, AnalyzeResult
from openai import AzureOpenAI
import tiktoken
from langchain.text_splitter import TextSplitter, MarkdownTextSplitter, RecursiveCharacterTextSplitter, PythonCodeTextSplitter

import os
#import sys
import datetime
from datetime import datetime, timedelta,timezone
#import pyodbc
import pandas as pd
from io import BytesIO
from typing import Callable, List, Dict, Optional, Generator, Tuple, Union
from azure.identity import DefaultAzureCredential
import io

AFR_ENDPOINT = os.environ["AFR_ENDPOINT"]
AFR_API_KEY = os.environ["AFR_API_KEY"]
AZURE_ACC_NAME = os.environ["AZURE_ACC_NAME"]

AZURE_PRIMARY_KEY = os.environ["AZURE_PRIMARY_KEY"]
STORAGE_ACCOUNT_CONTAINER = os.environ["STORAGE_ACCOUNT_CONTAINER"]
#DESTINATION_ACCOUNT_CONTAINER = os.environ["DESTINATION_ACCOUNT_CONTAINER"]

SUMMARY_PARQUET_CONTAINER = os.environ["SUMMARY_PARQUET_CONTAINER"]
SUMMARY_CONTAINER = os.environ["SUMMARY_CONTAINER"]

OPENAI_ENDPOINT = os.environ["OPENAI_ENDPOINT"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
OPENAI_EMBEDDING_MODEL = os.environ["OPENAI_EMBEDDING_MODEL"]
OPENAI_API_MODEL =  os.environ["OPENAI_API_MODEL"]


SQL_PASSWORD = os.environ["SQL_SECRET"]
SQL_SERVER = os.environ["SQL_SERVER"]
SQL_DB = os.environ["SQL_DB"]
SQL_USERNAME = os.environ["SQL_USERNAME"]

TEXT_ANALYTICS_KEY = os.environ["TEXT_ANALYTICS_KEY"]
TEXT_ANALYTICS_ENDPOINT = os.environ["TEXT_ANALYTICS_ENDPOINT"]
USE_MANAGED_IDENTITY = os.environ["USE_MANAGED_IDENTITY"]
USER_ASSIGNED_IDENTITY = os.environ["USER_ASSIGNED_IDENTITY"]

SENTENCE_ENDINGS = [".", "!", "?"]
WORDS_BREAKS = list(reversed([",", ";", ":", " ", "(", ")", "[", "]", "{", "}", "\t", "\n"]))
accumulated_summaries = []
document_chunks = []  

driver = '{ODBC Driver 17 for SQL Server}'

client = AzureOpenAI(
  azure_endpoint =  OPENAI_ENDPOINT, 
  api_key= OPENAI_API_KEY , 
  api_version="2024-02-15-preview"
)

class DocumentChunk:
    def __init__(self, filename, chunk_id, document_url, content, page_number, line_number):        
        self.filename = filename
        self.chunk_id = chunk_id
        self.document_url = document_url
        self.content = content
        self.page_number = page_number 
        self.line_number = line_number

    def convert_to_dict(self):
        result = {}        
        result = {
                'filename': self.filename,
                'chunk_id': self.chunk_id,
                'document_url': self.document_url,
                'content': self.content,
                'page_number': self.page_number,
                'line_number': self.line_number
          }
        return result


def generate_file_sas(file_name,container_name):
    sas_token = generate_blob_sas(
            account_name=AZURE_ACC_NAME,
            container_name=container_name,
            blob_name=file_name,
            account_key=AZURE_PRIMARY_KEY,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=2)
        )
    
    filewithsas=  "https://"+AZURE_ACC_NAME+".blob.core.windows.net/"+container_name+"/"+file_name+"?"+sas_token  
    return filewithsas


def save_array_to_azure(array, file_name, container_name):
    # Convert the array to a pandas DataFrame    
    
    json_value = json.dumps(array)
    print(json_value)

    # Load the JSON data into a DataFrame
    df = pd.read_json(json_value, orient='records')
    final_file_name = file_name.replace(".", "-") + ".parquet"        
    storage_account_connection_string = "DefaultEndpointsProtocol=https;AccountName="+AZURE_ACC_NAME+";AccountKey="+AZURE_PRIMARY_KEY+";EndpointSuffix=core.windows.net"

    try:    
  
        parquet_file = BytesIO()
        df.to_parquet(parquet_file, engine='pyarrow')   
        parquet_file.seek(0)

        if USE_MANAGED_IDENTITY == "0":
            blob_service_client = BlobServiceClient.from_connection_string(storage_account_connection_string)
            blob_client = blob_service_client.get_blob_client(container=container_name, blob=final_file_name)
        else:
            client_id = USER_ASSIGNED_IDENTITY
            credential = DefaultAzureCredential(managed_identity_client_id=client_id)
            blob_service_client = BlobServiceClient(account_url=f"https://{AZURE_ACC_NAME}.blob.core.windows.net", credential=credential)
            blob_client = blob_service_client.get_blob_client(container=container_name, blob=final_file_name)
        
        
        blob_client.upload_blob(
             data=parquet_file,overwrite=True
        )

        return final_file_name

    except Exception as e:             
        errors = [ { "message": "Failure during save_array_to_azure e: " + str(e)}]
        print(errors)
        return None

class TokenEstimator(object):
    GPT2_TOKENIZER = tiktoken.get_encoding("gpt2")

    def estimate_tokens(self, text: Union[str, List]) -> int:

        return len(self.GPT2_TOKENIZER.encode(text, allowed_special="all"))

    def construct_tokens_with_size(self, tokens: str, numofTokens: int) -> str:
        newTokens = self.GPT2_TOKENIZER.decode(
            self.GPT2_TOKENIZER.encode(tokens, allowed_special="all")[:numofTokens]
        )
        return newTokens 
    
def read_parquet_from_blob(storage_account_name, container_name, blob_path):
    """Reads a Parquet file from Azure Blob Storage using a managed identity."""

    # Create a credential object using the managed identity
    client_id = USER_ASSIGNED_IDENTITY
    credential = DefaultAzureCredential(managed_identity_client_id=client_id)
   
    # Create a BlobServiceClient using the credential
    blob_service_client = BlobServiceClient(
        account_url=f"https://{storage_account_name}.blob.core.windows.net",
        credential=credential
    )

    # Get a reference to the blob
    blob_client = blob_service_client.get_blob_client(container_name, blob_path)

    # Download the blob as bytes
    blob_data = blob_client.download_blob().readall()

    # Read the Parquet data into a Pandas DataFrame
    df = pd.read_parquet(io.BytesIO(blob_data))

    return df



def get_afr_result(file_name,chunck_size=1024):
    
    try:      
        logging.info(f"Processing {file_name}...")         


        endpoint = AFR_ENDPOINT
        key = AFR_API_KEY

        document_intelligence_client = DocumentIntelligenceClient(endpoint=endpoint, credential=AzureKeyCredential(key))

        if(file_URL != ""):
           print(f"Analyzing form from URL {file_URL}...")
        
        poller = document_intelligence_client.begin_analyze_document(
            "prebuilt-layout", AnalyzeDocumentRequest(url_source=file_URL)
        )    
        
        result = ""

        if USE_MANAGED_IDENTITY == "0":
            file_URL = generate_file_sas(file_name,SUMMARY_CONTAINER)
            logging.info(file_URL)
            if(file_URL != ""):
               print(f"Analyzing form from URL {file_URL}...")
               poller = document_intelligence_client.begin_analyze_document(
                       "prebuilt-layout", AnalyzeDocumentRequest(url_source=file_URL)
                        ) 
               result = poller.result()       
        else:
             logging.info("reading file from storage account " + file_name)       
             file_content = read_parquet_from_blob(AZURE_ACC_NAME,SUMMARY_PARQUET_CONTAINER,file_name)

             poller = document_intelligence_client.begin_read_in_stream(file_content)
            
             result = poller.result() 
       
        return result   
    except Exception as e:
        errors = "message: Fget_arf_result" + str(e)    


def process_file(filename,chunck_size=1024):
    try:      
        logging.info(f"Processing {filename}...")
        document_chunks = []         
               
        result =  get_afr_result(filename,chunck_size=1024)    
        return process_afr_result(result, filename)   
    
    except Exception as e:
        errors = "message: Failure during process_file" + str(e)


def process_afr_result(result, filename, content_chunk_overlap=100):   
   
   try:
        
        URL = generate_file_sas(filename,SUMMARY_CONTAINER)

        print(f"Processing {filename } with {len(result.pages)} pages into database...this might take a few minutes depending on number of pages...")
        chunk_id = 1 
        TOKEN_ESTIMATOR = TokenEstimator()
        for page_idx in range(len(result.pages)):
            docs = []
            #pageinfo = result.pages[page_idx]
            print(f"Processing page {page_idx} of {len(result.pages)}...")
            content_chunk = ""       
            
            for line_idx, line in enumerate(result.pages[page_idx].lines):            
                print("...Line # {} has text content '{}'".format(line_idx,line.content.encode("utf-8")))
                # Assuming `line.content` is your text
                encoded_content = line.content.encode("utf-8")  # This will give you bytes
                decoded_content = encoded_content.decode("utf-8")  # This will give you string
                # Now you can add it to your content_chunk
                content_chunk += decoded_content + "\n"

                
                
            #now split the chunk        
            content_chunk_size=TOKEN_ESTIMATOR.estimate_tokens(content_chunk)
            content_chunk_size = 1024;
            if content_chunk_size > content_chunk_overlap:
               chunk_list = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
                                    separators=SENTENCE_ENDINGS + WORDS_BREAKS,
                                    chunk_size=content_chunk_size, chunk_overlap=content_chunk_overlap).split_text(content_chunk)
            else:
                chunk_list = [content_chunk]
            
            for chunked_content in chunk_list:
                chunk_size = TOKEN_ESTIMATOR.estimate_tokens(chunked_content)
                print(f"content {chunked_content} with size {chunk_size}")                       
                #sql_statement = f"exec dbo.InsertIntoDocuments '{filename}', '{URL}', {chunk_id}, '{clean_content}', 'title...', '{datetime.now()}', '{page_idx}', '{line_idx}', '{embeddings}'"
                #print(sql_statement)
                item = DocumentChunk(filename=filename, chunk_id=chunk_id, document_url=URL, content=chunked_content, page_number=page_idx, line_number=line_idx).convert_to_dict()
                print (item.content)
                document_chunks.append(item)

                #add_document_to_table(filename, URL, chunk_id, chunked_content, datetime.now(),  page_idx, line_idx)
                chunk_id += 1
                # if chunk_id != 1:
                #    break

            # if chunk_id != 1:
            #        break    
    
        return document_chunks
   
   except Exception as e:             
        errors = "message: Failure during process_afr_result" + str(e)
        return errors



def main(req: func.HttpRequest,context: func.Context) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:

        #TOKEN_ESTIMATOR = TokenEstimator()
        file_name = req.params.get('file_name')
        if not file_name:
            try:
                req_body = req.get_json()
            except ValueError:
                pass
            else:
                file_name = req_body.get('file_name')

        final_file_name = file_name
        #URL = "https://useducsapocdatalake.blob.core.windows.net/document-summarization/NEJMoa2404881.pdf?sp=racw&st=2024-07-01T19:06:38Z&se=2025-06-02T03:06:38Z&sv=2022-11-02&sr=b&sig=PGbQWGOTIXET6ViOf9roTxFRWq5wItvCZxOURKARGGw%3D"
        file_name = "NEJMoa2404881.pdf"
      
        document_chunks = process_file(file_name)
        #if this is a string, then it is an error
        if isinstance(document_chunks, str) or document_chunks is None:
             return func.HttpResponse(
             document_chunks, status_code=500
        )

        final_file_name = save_array_to_azure(document_chunks, file_name, SUMMARY_PARQUET_CONTAINER)
        
        result = { "file_name": final_file_name, "file_url": generate_file_sas(final_file_name,SUMMARY_PARQUET_CONTAINER) }
        result_str = json.dumps(result)
        logging.info(result_str)
        logging.info(result)
        
        return func.HttpResponse(result_str, mimetype="application/json",status_code=200)
    
    except Exception as e:             
        errors = "message: Failure during chunk document" + str(e)
        return func.HttpResponse(
             errors, status_code=500
        )


