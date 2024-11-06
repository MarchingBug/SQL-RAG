# SQL RAG Front End Application

   - Download the application
   - In the Summarize-parquet.razor, update the SAS keys for the documents listed in the page

## Enviromental Variables:

```
     "NLP_URL": "https://<YOUR_SQL_RAG_FUNCTION>/api/SQLNLP?<FUNCTION_KEY>",
     "Ask_Question_URL": "https://<YOUR_SQL_RAG_FUNCTION>/api/AskDocumentQuestion?<FUNCTION_KEY>",
     "OpenAICall_URL": "https://<YOUR_SQL_RAG_FUNCTION>/api/CallOpenAI?<FUNCTION_KEY>",
     "Parquet_URL": "https://<YOUR_DOCUMENT_SUMMARIZATION_FUNCTION>/api/read_chuncked_file?<FUNCTION_KEY>"
```
     


