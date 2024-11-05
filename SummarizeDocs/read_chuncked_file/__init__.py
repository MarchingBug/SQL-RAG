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
import io

from openai import AzureOpenAI
import tiktoken
from typing import Callable, List, Dict, Optional, Generator, Tuple, Union

from azure.identity import DefaultAzureCredential


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
USE_MANAGED_IDENTITY = os.environ["USE_MANAGED_IDENTITY"]
USER_ASSIGNED_IDENTITY = os.environ["USER_ASSIGNED_IDENTITY"]

accumulated_summaries = []
document_chunks = []  

client = AzureOpenAI(
  azure_endpoint =  OPENAI_ENDPOINT, 
  api_key= OPENAI_API_KEY , 
  api_version="2024-02-15-preview"
)

class TokenEstimator(object):
    GPT2_TOKENIZER = tiktoken.get_encoding("gpt2")

    def estimate_tokens(self, text: Union[str, List]) -> int:

        return len(self.GPT2_TOKENIZER.encode(text, allowed_special="all"))

    def construct_tokens_with_size(self, tokens: str, numofTokens: int) -> str:
        newTokens = self.GPT2_TOKENIZER.decode(
            self.GPT2_TOKENIZER.encode(tokens, allowed_special="all")[:numofTokens]
        )
        return newTokens 

def generate_file_sas(file_name,container_name):

    sas_token = generate_blob_sas(
            account_name=AZURE_ACC_NAME,
            container_name=container_name,
            blob_name=file_name,
            account_key=AZURE_PRIMARY_KEY,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.now(tz=timezone.utc) + timedelta(hours=2)
        )
    
    filewithsas=  "https://"+AZURE_ACC_NAME+".blob.core.windows.net/"+container_name+"/"+file_name+"?"+sas_token  
    return filewithsas

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

def summarize_chunk(text: str,                                    
              system_message_content: str            
             ):
        
    chunk = text     
    # Assuming this function gets the completion and works as expected
    response = get_chat_completion(system_message_content,chunk)
    
    return response

def format_final_response(final_summary):
    
    system_message_content = """
    
            Your responses should be in HTML format, well-structured, and easy to read. Follow these guidelines:

        1. **Formatting**:
        - Use `<strong>` for bold text.
        - Use `<em>` for italic text.
        - Use `<code>` for inline code snippets.
        - Use `<pre><code>` for code blocks.
        - Use `<ul>` and `<li>` for bullet points.
        - Use `<ol>` and `<li>` for numbered lists.

        2. **Paragraphs**:
        - Break down text into short, concise paragraphs using `<p>`.
        - Ensure each paragraph covers a single idea or point.

        3. **Headings**:
        - Use headings to organize content.
        - Use `<h1>` for main headings, `<h2>` for subheadings, and `<h3>` for sub-subheadings.

        4. **Links**:
        - Use `<a href="URL">link text</a>` for hyperlinks.

        5. **Tables**:
        - Use `<table>`, `<tr>`, `<th>`, and `<td>` for structured data.

        6. **Quotes**:
        - Use `<blockquote>` for block quotes.

        7. Do not include <head> nor <body> nor <title>

        8. This output will be embedded into a <body> section, exclude that section


        **Example**:


        <h1>Introduction</h1>
        <p>Welcome to the guide on using HTML with ChatGPT. This guide will help you understand how to format your responses effectively.</p>

        <h2>Formatting Basics</h2>
        <ul>
            <li><strong>Bold</strong>: Use the <code>&lt;strong&gt;</code> tag.</li>
            <li><em>Italics</em>: Use the <code>&lt;em&gt;</code> tag.</li>
            <li><code>Code</code>: Use the <code>&lt;code&gt;</code> tag for inline code.</li>
        </ul>

        <h2>Lists</h2>
        <ol>
            <li>First item</li>
            <li>Second item</li>
            <li>Third item</li>
        </ol>
        <ul>
            <li>Bullet point one</li>
            <li>Bullet point two</li>
            <li>Bullet point three</li>
        </ul>

        <h2>Links</h2>
        <p>For more information, visit <a href="https://www.openai.com">OpenAI</a>.</p>

        <h2>Tables</h2>
        <table>
            <tr>
                <th>Syntax</th>
                <th>Description</th>
            </tr>
            <tr>
                <td>Header</td>
                <td>Title</td>
            </tr>
            <tr>
                <td>Row</td>
                <td>Data</td>
            </tr>
        </table>

        <blockquote>This is a block quote.</blockquote>

        <h2>Conclusion</h2>
        <p>By following these guidelines, you can create well-structured and readable HTML content with ChatGPT.</p>
        """

    response = get_chat_completion(system_message_content, final_summary)
    return response



def summarize_document(chunks,summarize_recursively=False,system_message_content="Rewrite this text in summarized form.",additional_instructions=None,tokens_per_chunk=OPENAI_MODEL_MAX_TOKENS):
    
    try:
        TOKEN_ESTIMATOR = TokenEstimator()
        

        accumulated_summaries = []
        make_the_call = False
        user_message_content = ""

        document_tokens_per_chunk = int(tokens_per_chunk)

        if additional_instructions is not None:
            system_message_content += f"\n\n{additional_instructions}"  

        for index,chunk in chunks.iterrows():
            #print(f"Summarizing chunk {chunk['content']}...")
            if summarize_recursively and accumulated_summaries:
                # Creating a structured prompt for recursive summarization
                ##########################################
                accumulated_summaries_string = '\n\n'.join(accumulated_summaries)
                content_chunk_size=TOKEN_ESTIMATOR.estimate_tokens(f"Previous summaries:\n\n{accumulated_summaries_string}\n\nText to summarize next:\n\n{chunk['content']}")
                if content_chunk_size < document_tokens_per_chunk:
                    user_message_content = f"Previous summaries:\n\n{accumulated_summaries_string}\n\nText to summarize next:\n\n{chunk['content']}"
                else:
                    make_the_call = True
                ###########################################
            else:
                # Directly passing the chunk for summarization without recursive context                      
                content_chunk_size=TOKEN_ESTIMATOR.estimate_tokens(user_message_content + chunk['content'])
                if content_chunk_size < document_tokens_per_chunk:
                    user_message_content = user_message_content + chunk['content']
                else:
                    make_the_call = True

            if index == len(chunks) - 1:          
               make_the_call = True

            if make_the_call:
                # Constructing messages based on whether recursive summarization is applied
                messages = [
                    {"role": "system", "content": system_message_content},
                    {"role": "user", "content": user_message_content}
                ]

                # Assuming this function gets the completion and works as expected
                response = get_chat_completion(system_message_content, user_message_content)
                accumulated_summaries.append(response)
                if not summarize_recursively:
                    user_message_content = ""

                make_the_call = False

        # Compile final summary from partial summaries
        final_summary = '\n\n'.join(accumulated_summaries)    
        final_summary = format_final_response(final_summary)

        return final_summary
    
    except Exception as e: 
        errors = "message: Failure during summarize_document" + str(e)
        return func.HttpResponse(
             errors, status_code=500
        ) 
    

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

def read_file_contents(file_name):
    if USE_MANAGED_IDENTITY == "0":       
       file_url = generate_file_sas(file_name,SUMMARY_PARQUET_CONTAINER)
       logging.info("Generated SAS token " + file_url)               
       return pd.read_parquet(file_url)
    else:
       logging.info("reading file from storage account " + file_name)       
       return read_parquet_from_blob(AZURE_ACC_NAME,SUMMARY_PARQUET_CONTAINER,file_name)


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:


        file_name = req.params.get('file_name')
        file_url = req.params.get('file_url')
        system_message_content = req.params.get('system_message')
        additional_instructions = req.params.get('additional_instructions')
        summarize_recursively = req.params.get('summarize_recursively')
        tokens_per_chunk = req.params.get('tokens_per_chunk')

        if not file_name:
            try:
                req_body = req.get_json()
            except ValueError:
                pass
            else:
                file_name = req_body.get('file_name')
                #file_url = req_body.get('file_url')
                system_message_content = req_body.get('system_message')
                additional_instructions = req_body.get('additional_instructions')
                summarize_recursively = req_body.get('summarize_recursively') 
                tokens_per_chunk = req_body.get('tokens_per_chunk')               

        

        if not system_message_content or system_message_content == "":
            system_message_content = "Rewrite this text in summarized form."

        if not summarize_recursively or summarize_recursively == "":
            summarize_recursively = False

        if not additional_instructions or additional_instructions == "":
            additional_instructions = None

        if not tokens_per_chunk or tokens_per_chunk == "":
            tokens_per_chunk = OPENAI_MODEL_MAX_TOKENS

        df = read_file_contents(file_name)
        logging.info("Read parquet file")   
        final_summary = summarize_document(df,summarize_recursively=summarize_recursively,system_message_content=system_message_content,additional_instructions=additional_instructions,tokens_per_chunk=tokens_per_chunk)
        logging.info("Summarized document " + final_summary)        
        result = { "file_name": file_name, "summary": final_summary }
        result_str = json.dumps(result)

        return func.HttpResponse(result_str, mimetype="application/json",status_code=200)
        
    except Exception as e: 
        errors = "message: Failure during read_chunked_file" + str(e)
        return func.HttpResponse(
             errors, status_code=500
        ) 
