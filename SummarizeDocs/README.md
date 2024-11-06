# Long Documents & Large Language Models

When working with long documents and large language models (LLMs), whether for summarization or content creation, it's crucial to consider the token limitations of the model you are using. RAG (Retrieval-Augmented Generation) is often not the most efficient approach for handling documents, as it typically returns a fixed number of records based on a search query.

To effectively summarize lengthy documents, you must account for the entire content, which can frequently exceed the token limits of your LLM. Here are two primary methods for summarization:

1. **Overlapping Text Requests:** This involves sending requests to the LLM with overlapping sections of text and storing the results in an array. For example, if you have a document of 5,000 words, you might break it into chunks of 1,000 words, overlapping the last 200 words of each chunk with the next. This method can be effective, but if the document is excessively long, it may miss important context. For instance, if a key point is made in the transition between two chunks, it might not be captured in either summary.

2. **Recursive Summarization:** This technique entails attaching the previous summary to the new text, allowing for a more cohesive and concise result. For example, if you summarize the first 1,000 words and then summarize the next 1,000 words while including the previous summary, you create a more comprehensive overview. This method tends to yield better outcomes by maintaining context throughout the summarization process, ensuring that important connections between ideas are preserved.


## Comparison of Summarization Methods

| **Aspect**                     | **Overlapping Text Requests**                             | **Recursive Summarization**                             |
|--------------------------------|----------------------------------------------------------|--------------------------------------------------------|
| **Process**                    | Breaks the document into chunks with overlapping text.   | Summarizes sections while incorporating previous summaries. |
| **Context Preservation**       | May lose context between chunks, especially in transitions. | Better at maintaining context as it builds on previous summaries. |
| **Complexity**                 | Simpler to implement; straightforward chunking.         | More complex; requires careful integration of summaries. |
| **Efficiency**                 | Can be less efficient with very long documents due to potential context loss. | More efficient for long documents, as it synthesizes information progressively. |
| **Output Quality**             | May produce fragmented summaries that lack cohesion.     | Tends to yield more coherent and concise summaries.     |
| **Use Case**                   | Useful for quick, initial summaries where context is less critical. | Ideal for comprehensive summaries where understanding the whole is essential. |

### Example Scenarios:

- **Overlapping Text Requests**: If you have a lengthy research paper, you might summarize each section independently. This could work well for extracting key points but might miss the nuances of how those points relate to each other.

- **Recursive Summarization**: For a complex report with interrelated themes, this method would allow you to summarize each section while continuously integrating insights from previous summaries, resulting in a more holistic understanding of the document.

Both methods have their merits, and the choice between them often depends on the specific requirements of the task at hand.

## Deployment Steps

- Deploy the Azure function
- On your Azure Storage Account, create a container named "document-summarization-parquet"
- Upload the sample parquet files under the sampleDocuments folder to the "document-summarization-parquet" container
- Create the enviromental variables for the Function APP

## Azure Function Overview
This azure function app has 3 functions:

     - chunk_file
     - read_chunked_file
     - CallOpenAI

## Enviromental Variables for the function

```
    "AFR_ENDPOINT": "https://<YOUR_DOCUMENT_INTELLIGENCE_SERVICE>.cognitiveservices.azure.com/",
    "AFR_API_KEY": "<YOUR_DOCUMENT_INTELLIGENCE_SERVICE_KEY>",
    "AZURE_ACC_NAME": "<YOUR_AZURE_STORAGE_ACCOUNT_NAME>",
    "AZURE_PRIMARY_KEY": "<YOUR_AZURE_STORAGE_ACCOUNT_KEY>,
    "STORAGE_ACCOUNT_CONTAINER": "nasa-files",
    "SUMMARY_CONTAINER": "document-summarization",
    "SUMMARY_PARQUET_CONTAINER": "document-summarization-parquet",
    "SQL_SERVER": "<YOUR_SQL_SERVER_NAME>.database.windows.net",
    "SQL_DB": "nasa-documents",
    "SQL_USERNAME": "<YOUR_SQL_SERVER_USER>",
    "SQL_SECRET": "<YOUR_SQL_SERVER_PASSWORD>",
    "OPENAI_ENDPOINT": "https://<YOUR_OPEN_AI_SERVICE>.openai.azure.com/",
    "OPENAI_API_KEY": "<YOUR_OPEN_AI_SERVICE_KEY>",
    "OPENAI_EMBEDDING_MODEL": "text-embedding-ada-002",
    "TEXT_ANALYTICS_ENDPOINT": "https://<YOUR_TEXT_ANALYTICS_SERVICE>.cognitiveservices.azure.com/",
    "TEXT_ANALYTICS_KEY": "<YOUR_TEXT_ANALYTICS_SERVICE_KEY>",
    "OPENAI_API_MODEL": "gpt-4o",
    "OPENAI_MODEL_MAX_TOKENS": "100000",
    "USE_MANAGED_IDENTITY": "1",
    "USER_ASSIGNED_IDENTITY": "<YOUR_MANAGED_IDENTITY_CLIENT_ID>"  ---> IF YOU ARE USING MANAGED IDENTITY

```

## read_chunked_file Function Overview

This Azure Function reads a Parquet file from Azure Blob Storage, summarizes its content using OpenAI's GPT model, and returns the summarized content in an HTTP response. Here's a high-level summary of the code:

### Key Components

1. **Helper Classes and Functions:**
   - **TokenEstimator:** Estimates the number of tokens in a text.
   - **generate_file_sas:** Generates a SAS token for accessing a file in Azure Blob Storage.
   - **get_chat_completion:** Gets a completion from OpenAI's GPT model.
   - **summarize_chunk:** Summarizes a text chunk using OpenAI.
   - **format_final_response:** Formats the final summary in HTML.
   - **summarize_document:** Summarizes the entire document by breaking it into chunks and optionally using recursive summarization.
   - **read_parquet_from_blob:** Reads a Parquet file from Azure Blob Storage using a managed identity.
   - **read_file_contents:** Reads the contents of a Parquet file using either a SAS token or a managed identity.

2. **Main Function:**
   - Handles HTTP requests, extracts parameters, reads the Parquet file, summarizes the document, and returns the summary in the response.

### Error Handling
- The function includes error handling to catch exceptions and return an appropriate HTTP response with a status code of 500 in case of failures.

### Usage
- Send an HTTP request with the required parameters (e.g., file name, system message) to the function's endpoint. The function reads the specified Parquet file, summarizes its content, and returns the summary in the response.

## Chunk_document Function Overview

This Azure Function processes a document, splits it into chunks, and saves the processed chunks to Azure Blob Storage in Parquet format. Here's a summary of its functionality:


### 1. Classes and Helper Functions
- **DocumentChunk**: Represents a chunk of a document.
- **TokenEstimator**: Estimates the number of tokens in a text and constructs tokens with a specified size.
- **generate_file_sas**: Generates a SAS token for a file in Azure Blob Storage.
- **save_array_to_azure**: Converts an array to a Pandas DataFrame, saves it as a Parquet file, and uploads it to Azure Blob Storage.
- **read_parquet_from_blob**: Reads a Parquet file from Azure Blob Storage.
- **get_afr_result**: Analyzes a document using Azure Form Recognizer and returns the result.
- **process_file**: Processes a file by calling `get_afr_result` and then processes the AFR result.
- **process_afr_result**: Processes the AFR result, splits the content into chunks, and returns a list of `DocumentChunk` objects.

### 2. Main Function
- Entry point for the Azure Function.
- Retrieves the `file_name` parameter from the HTTP request.
- Calls `process_file` to process the document and split it into chunks.
- Saves the chunks to Azure Blob Storage using `save_array_to_azure`.
- Returns the result as an HTTP response.

### Summary
This Azure Function processes a document by analyzing it with Azure Form Recognizer, splitting it into manageable chunks, and storing the processed data in Azure Blob Storage. It handles large documents efficiently and provides easy access to the processed data.



