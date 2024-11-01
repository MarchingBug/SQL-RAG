
# SQL Rag Azure Functions Overview

The workspace includes two C# files, each defining an Azure Function that processes HTTP requests and interacts with a SQL database. Below is a summary of the functionality of each file:

## File: AskDocumentQuestion.cs
**Namespace:** Company.Function  
**Class:** AskDocumentQuestion  

- **Purpose:** Handles HTTP requests to execute a stored procedure in a SQL database and return the results in JSON format.
- **Key Methods:**
  - **Run:** The main entry point for the Azure Function. Processes HTTP GET and POST requests, retrieves parameters from the query string or request body, calls `ExecuteStoredProcedure`, and returns the result.
  - **GetConnectionString:** Constructs the SQL connection string using environment variables.
  - **ExecuteStoredProcedure:** Executes the stored procedure `[dbo].[AskDocumentQuestion]` with parameters `system_message` and `question`, reads the result into a DataTable, and returns it as JSON.

## File: SQLNLP.cs
**Namespace:** SQLRAGAzureFunction  
**Class:** SQLNLP  

- **Purpose:** Handles HTTP requests to execute a stored procedure in a SQL database and return the results in JSON format.
- **Key Methods:**
  - **Run:** The main entry point for the Azure Function. Processes HTTP GET and POST requests, retrieves parameters from the query string or request body, calls `ExecuteStoredProcedure`, and returns the result.
  - **GetConnectionString:** Constructs the SQL connection string using environment variables.
  - **ExecuteStoredProcedure:** Executes the stored procedure `[dbo].[SQLNLP]` with parameters `question` and `schema`, reads the result into a DataTable, and returns it as JSON.

## Common Characteristics
- Both files target .NET 8.
- Both functions use managed identities for secure database access.
- Both functions handle exceptions and log errors, returning a 500 status code in case of failures.
- Both functions use `DefaultAzureCredential` to obtain an access token for the SQL connection.
