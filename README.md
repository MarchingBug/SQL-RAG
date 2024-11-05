# Intelligent Applications with Azure SQL

Azure SQL can be used to build intelligent applications. **To see this solution in action navigate to this <a href="https://smartchatapp-tsp-fsi.azurewebsites.net/" target="_blank">website</a>**

![SQL Intelligent applications](images/architecture.jpg)

## Overview  - Asking questions, different kinds of questions
Combine the power of Azure SQL and OpenAI and use familiar tools to create enhanced intelligent database solutions.
 

![beyond RDBMS](images/Slide7.PNG)


## Part I - Ask questions on your documents

In this code, using a python Jupyter Notebook we ingest a large number of documents from a storage account (or you can use a SharePoint Site, code is there), save the chunked information into an Azure SQL database using a stored procedure.

![data ingestion](images/Slide11.PNG)

The stored procedure saves data to the documents table, saves the embeddings and creates similarity vector table, as well as saving key phrases into a graph table for searching.

![documents](images/Slide10.PNG)

You can use the AskDocumentQuestion Stored procedure that takes system message and question as parameters to answer question about your data.

![ask](images/Slide12.PNG)


![ask](images/Slide13.PNG)
![ask](images/Slide14.PNG)
![ask](images/Slide15.PNG)

## Part II - SQL + NLP - get data insights 

Using vanilla AdventureWorks Database, you can ask insightful questions about your data, right inside your SQL server

![nlp](images/Slide17.PNG)

## Key Concepts

To implement this solution the following components were used

- Azure SQL Database features:
    - <a href="https://learn.microsoft.com/en-us/sql/relational-databases/graphs/sql-graph-overview?view=sql-server-ver16" target="_blank">Graph Tables</a>
    - <a href="https://devblogs.microsoft.com/azure-sql/azure-sql-database-external-rest-endpoints-integration-public-preview/" target="_blank">   Rest Point Call functionality</a>
    - <a href="https://learn.microsoft.com/en-us/azure/azure-sql/database/json-features?view=azuresql" target="_blank"> JSON Features </a>

- Azure AI Services
    - <a href="https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/overview?view=doc-intel-4.0.0" target="_blank">   Azure Document Intelligence </a>
    - <a href="https://learn.microsoft.com/en-us/azure/ai-services/openai/concepts/models" target="_blank" >Azure OpenAI Chat model</a>
    - <a href="https://learn.microsoft.com/en-us/azure/ai-services/openai/concepts/models#embeddings-models" target="_blank" >Azure OpenAI Embeddings model</a>

## Assets

This repository containes the following assets and code:

- Azure SQL Database bacpac file
- Requirements.txt
- SQLGraphRag Jupiter Notebook with code needed to ingest documents into your database
- Sample documents

## Services used for this solution

Listed below are the services needed for this solution, if you don't have an azure subscription, you can create a free one. If you already have an subscription, please make sure that your administration has granted access to the services below:

* Azure Subscription
* [Azure SQL Serverless](https://learn.microsoft.com/en-us/azure/azure-sql/database/serverless-tier-overview?view=azuresql)
* [Azure OpenAI Services](https://learn.microsoft.com/en-us/azure/ai-services/openai/overview)
* [Azure Document Intelligence](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/overview?view=doc-intel-4.0.0)
* [Azure AI Language ](https://learn.microsoft.com/en-us/azure/ai-services/language-service/overview)

Programming Tools needed:

* [VS Code](https://code.visualstudio.com/)

## Expected time to completion
This project should take about 1 hour to complete

# Part I - Ask questions on documents 

## Part I - Setup Steps

> [!IMPORTANT] 
> Before you begin, clone this repository to your local drive

1. [Azure account - login or create one](#task-1---azure-account)
2. [Create a resource group](#task-2---create-a-resource-group)
3. [Create a Storage Account](#task-3---create-a-storage-account)
4. [Create the Azure SQL Database](#task-4---create-the-sql-server-database)
5. [Create OpenAI Account and Deploy Models](#task-5---create-openai-account-and-deploy-models)
6. [Create Azure Document Intelligence Service](#task-6---create-azure-document-intelligence-service)
7. [Create Azure AI Language Service](#task-7---create-azure-ai-language-service)
8. [Upload documents to storage account](#task-8---upload-documents-to-storage-account)
9. [Configure Stored Procedure](#task-9---configure-stored-procedure)

## Ingestion and SQL Configuration

1. [Set up enviromental variables](#task-1---set-up-enviromental-variables)
2. [Run Notebook to ingest](#task-2---run-notebook-to-ingest)
3. [Ask Question](#task-3---ask-question)

### Task 1 - Azure Account

First, you will need an Azure account.  If you don't already have one, you can start a free trial of Azure [here](https://azure.microsoft.com/free/).  

Log into the [Azure Portal](https://azure.portal.com) using your credentials


### Task 2 - Create a resource group

If you are new to Azure, a resource group is a container that holds related resources for an Azure solution. The resource group can include all the resources for the solution, or only those resources that you want to manage as a group, click [here](https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/manage-resource-groups-portal#create-resource-groups) to learn how to create a group

> Write the name of your resource group on a text file, we will need it later

### Task 3 - Create a Storage Account

If you don't have a storage account yet, please create one, to learn more about creating a storage account, click 
  [here](https://learn.microsoft.com/en-us/azure/storage/common/storage-account-create?tabs=azure-portal).

  Create a container name, you can use `nasa-documents` or create your own name

  > Note the storage account name and access key and the container name in your text file.

### Task 4 - Create the SQL Server Database

Upload the file `nasa-documents.bacpac` located under the folder `data-files` to a storage account in your subscription.

  Import the database package to a serverless database, for more information on how to do this click [here](https://learn.microsoft.com/en-us/azure/azure-sql/database/database-import?view=azuresql&tabs=azure-powershell).

  > [!IMPORTANT] Configure your database as a `Hyperscale - Serverless database`
  
<!-- <details>
  <summary>   If you have never done this expand this section for detailed steps  </summary>

Click on create new resource and search for SQL Server (logical server) and select that option

![Create a SQL Server](images/sql-1.png)

Click the create button

![Create a SQL Database resourse](images/sql-2.png)

Select the resource group you previously created

Enter a name for the server and a location that matches the location of your resource group. Select use both SQL and Azure AD authentication, add yourself as Azure AD admin. Enter a not easy to guess user name and password for the server. Click Networking

![Create a SQL Database resourse](images/sql-3.png)

Under firewall rules select Allow Azure Services and resources to access this server. Click Review + create

![Create a SQL Database resourse](images/sql-4.png)

Verify all information is correct, click on "Create"

![Create a SQL Database resourse](images/sql-5.png)

Once your database is created, navigate to your new SQL Server and click on Import Database

![Create a SQL Database resourse](images/sql-6.png)

Once on the Import dabase select backup

![Create a SQL Database resourse](images/sql-7.png)

Select the storage account where you uploaded the database file and navigate to the file. Click Select

![Create a SQL Database resourse](images/sql-8.png)

Next click configure database

![Create a SQL Database resourse](images/sql-9.png)

Under computer tier, select serverless, click ok

![Create a SQL Database resourse](images/sql-10.png)

Enter a data base name, select SQL server authentication and enter the user name & password you defined for the SQL Server, click ok

![Create a SQL Database resourse](images/sql-11.png)

Navigate to your SQL server, and select import/export history to see the progress of your import, once completed, navigate to databases to look at your new imported database

![Create a SQL Database resourse](images/sql-12.png)

Once on your imported database, select Query editor and enter your user credentials. Loging will fail as you need to grant access to your IP address. Click on Allow IP server and then login

![Create a SQL Database resourse](images/sql-13.png)

Once on the query screen copy and paste this sql statement and click Run to verify data was imported

```sql
Select * from documents
 
```

![Create a SQL Database resourse](images/sql-14.png)

</details>


> Write the name of your sql server, database, username and password on a text file, we will need it later -->

### Task 5 - Create OpenAI Account and Deploy Models

If you do not have an OpenAI account, create one, you have your Azure OpenAI service, make suru have or deploy two models

    1. Completions model, we used `gtp-4o` for this demo,if you can, please use this model.
    2. Embeddings model, use text-embedding-ada-002 for this demo.    
    
   
If the models are alredy deployed, use those, if not, for more information on how to deploy this service and models click [here](https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/create-resource?pivots=web-portal)


 > Note the Azure OpenAI service endpoint, API key and the model name on your text file


 ### Task 6 - Create Azure Document Intelligence Service

Document intelligence will be used to chunk documents using top notch technologies to read your documents.

If you do not have a document intelligence service account, create one, for more information click [here](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/create-document-intelligence-resource?view=doc-intel-4.0.0)


`Do not use the free SKU.`

 > Note the document intelligence service endpoint, API key on your text file

 ### Task 7 - Create Azure AI Language Service

Azure AI Language Service will be used to extract key phrases from each document chunk, you can also use Azure AI Language Service to extract sentiment analysis, Entities and more.

If you do not have a Azure AI Language Service , create one:

1. In the Azure Portal, search for “Azure AI services” and select “Create” under Language Service1.
2. Fill in the required details such as the resource name, subscription, resource group, and location. Choose the pricing tier that suits your needs (you can start with the Free tier).


 > Note the Azure AI Language service endpoint, API key on your text file

 ### Task 8 - Upload documents to storage account

Download the file [nasa-documents.zip](https://ustspdevpocdatalake.blob.core.windows.net/nasa-github/nasa-documents.zip?sp=r&st=2024-07-10T22:39:41Z&se=2026-07-31T06:39:41Z&sv=2022-11-02&sr=b&sig=2PISrTdV%2FIJ%2FSqESEK7t22uJ7jQXFp37Bgk0Y5L6BxI%3D) to your local computer, extract the files and load them to the container you created on step 3

### Task 9 - Configure Stored Procedure

Log into the Azure Portal, navigate to your sql database and open the query editor for the `nasa-documents` database (or you can use SQL Server Management Studio).

![Query Editor](images/query-editor.png)

Once logged in expand the stored procedure sections, click on the elipsis and select View Definition

![Query Editor 1](images/query-editor-1.png)

scroll down to line 33, you will need to update your OpenAI configuration there

![Query Editor 2](images/query-editor-2.png)

Once you make the changes, click on run.

-------------------------------------------------------------------

## Data Ingestion 

### Task 1 - Set up enviromental variables

 Using VS Studio, open the project folder.

 Provide settings for Open AI and Database.You can either create a file named `secrets.env` file in the root of this folder and use VS Code app's UI later (*easier*).
    

        AFR_ENDPOINT=https://YOUR-DOCUMENT-INTELLIGENCE-SERIVCE-NAME.cognitiveservices.azure.com/
        AFR_API_KEY=YOUR-DOCUMENT-INTELLIGENCE-API-KEY
        AZURE_ACC_NAME=YOUR-STORAGE-ACCOUNT-NAME
        AZURE_PRIMARY_KEY=YOUR-STORAGE-ACCOUNT-KEY
        STORAGE_ACCOUNT_CONTAINER=nasa-files 
        SQL_SERVER = YOUR-AZURE-SQL-SERVER.database.windows.net
        SQL_DB = nasa-documents
        SQL_USERNAME=YOUR-SQL-USER-NAME
        SQL_SECRET= YOUR-SQL-USER-PWD
        OPENAI_ENDPOINT=https://YOUR-OPEN-AI-RESOURCE-NAME.openai.azure.com/
        OPENAI_API_KEY=YOUR-OPEN-AI-API-KEY
        OPENAI_EMBEDDING_MODEL=text-embedding-ada-002
        TEXT_ANALYTICS_ENDPOINT=https://YOUR-AZURE-LANGUAGE-SERVICE-NAME.cognitiveservices.azure.com/
        TEXT_ANALYTICS_KEY=YOUR-AZURE-LANGUAGE-SERVICE-KEY

    

        

> [!IMPORTANT] 
> If you are a Mac user, please follow [this](https://learn.microsoft.com/en-us/sql/connect/odbc/linux-mac/install-microsoft-odbc-driver-sql-server-macos?view=sql-server-ver16) to install ODBC for PYODBC


## Task 2 - Run notebook to ingest

Open the SQLGraphRag Notebook and run it! 

## Task 3 - Ask a question

Go back to the query editor, create a new query and run the following tests:

### Test 1
```
declare @systemMessage varchar(max)
declare @text varchar(max)

set @systemMessage = 'Summarize the document content'
set @text  = 'Give me a summary in laymans terms, only search for the document with name silkroads.pdf'
execute [dbo].[AskDocumentQuestion] @text,@systemMessage,0
```
### Test 2
```
declare @systemMessage varchar(max)
declare @text varchar(max)

set @systemMessage = 'you are a helpful assistant that helps people find information'
set @text  = 'What are the main innovations of Nasa Science Mission Directorate?'
execute [dbo].[AskDocumentQuestion] @text,@systemMessage,0
```
### Test 3
```
declare @systemMessage varchar(max)
declare @text varchar(max)

set @systemMessage = 'Summarize the document content'
set @text  = 'what are the main topics of this database content?'
execute [dbo].[AskDocumentQuestion] @text,@systemMessage,0
```

# Part II - Get SQL Insights with Natural Language

## Part II - Setup Steps

1. [Deploy Adventure Works Database](#task-1---deploy-adventure-works-database)
2. [Add Stored Procedure](#task-2---add-stored-procedure)
3. [Ask Questions NLP](#task-3---ask-questions-nlp)

 ### Task 1 - Deploy Adventure Works Database

 Nagivate to the Azure Portal, deploy a the Adventure Works sample database. For more information on how to do this click [here](https://learn.microsoft.com/en-us/sql/samples/adventureworks-install-configure?view=sql-server-ver16&tabs=ssms#deploy-to-azure-sql-database)

 > [!IMPORTANT]
 > Make sure to configure your database as serverless to save money

 ### Task 2 - Add Stored Procedure

 Once the database has been deployed, navigate to the query editor, copy and paste the following T-SQL script.

 Make sure you update the Open AI parameters in the T-SQL script.

 > [!IMPORTANT]
 > Make sure to update your OPEN AI information before running this, otherwise you will need to run an alter procedure.

 ```
 SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
-- =============================================
-- Author:      <Author, , Name>
-- Create Date: <Create Date, , >
-- Description: <Description, , >
-- =============================================
Create PROCEDURE [dbo].[SQLNLP] (@question varchar(max), @schema varchar(max))
AS
BEGIN

    declare @text nvarchar(max) =  @question,
	        @schema_name nvarchar(max) = @schema;
			
	

	declare @systemmessage nvarchar(max)
	
	declare @payload2  nvarchar(max)
	declare @top int = 20
	declare @min_similarity decimal(19,16) = 0.75

	declare @retval int, @response nvarchar(max);
	declare @payload nvarchar(max);
	set @payload = json_object('input': @text);

	declare @urlEmbeddings nvarchar(250);
	declare @theHeadings nvarchar(250)
	declare @urlGPT4 nvarchar(250)
	DECLARE @content VARCHAR(MAX);
	DECLARE @document_name VARCHAR(255);
	DECLARE @chunk_id INT;
	declare @previous_summary varchar(max)

	set @previous_summary = ''


	set @urlGPT4 = 'https://YOUR-OPEN-AI-SERVICE-NAME.openai.azure.com/openai/deployments/YOUR-COMPLETIONS-DEPLOYMENT-NAME/chat/completions?api-version=2023-07-01-preview'
	set @theHeadings  = '{"Content-Type":"application/json","api-key":"YOUR-OPEN-AI-API-KEY"}'


	 --=======================  Fetch the database schema
 
	 DECLARE @cols AS NVARCHAR(MAX),
			 @table_name as nvarchar(max),
			 @table_columns varchar(max),			
			 @query AS NVARCHAR(MAX);

	

	-- Declare the cursor
	DECLARE TableCursor CURSOR FOR
	SELECT distinct 
		C.TABLE_NAME       
	FROM 
		INFORMATION_SCHEMA.COLUMNS C  
	JOIN 
		INFORMATION_SCHEMA.TABLES T 
	ON 
		C.TABLE_NAME = T.TABLE_NAME 
		AND C.TABLE_SCHEMA = T.TABLE_SCHEMA  
	WHERE 
		T.TABLE_TYPE = 'BASE TABLE' 
		AND T.TABLE_SCHEMA = @schema_name;


	drop table if exists #tables;
	create table #tables ( theTable nvarchar(max));

	-- Open the cursor
	OPEN TableCursor;

	-- Fetch the first row
	FETCH NEXT FROM TableCursor INTO @table_name;

	-- Loop through the rows
	WHILE @@FETCH_STATUS = 0
	BEGIN
		-- Process each row
		--============================================================================================
	
		-- Generate the column list with data types
		SET @cols = STUFF((SELECT DISTINCT ', ' + QUOTENAME(COLUMN_NAME) + ' - ' + DATA_TYPE
					   FROM INFORMATION_SCHEMA.COLUMNS
					   WHERE TABLE_SCHEMA = @schema_name AND TABLE_NAME = @table_name
					   FOR XML PATH(''), TYPE).value('.', 'NVARCHAR(MAX)'), 1, 2, '');




		set @table_columns = 'TableName: ' + QUOTENAME(@schema_name) + '.' + QUOTENAME(@table_name) + ' Columns: ' + + @cols

		--select @table_columns

		SET @query = 'insert into #tables (theTable) values (''' + @table_columns + ''')'       
		--select @query
		-- Execute the query
		EXEC sp_executesql @query;
	

		--====================================================================================================

		-- Fetch the next row
		FETCH NEXT FROM TableCursor INTO @table_name;
	END

	-- Close the cursor
	CLOSE TableCursor;

	-- Deallocate the cursor
	DEALLOCATE TableCursor;

	declare @finalSchema varchar(max)
	SELECT @finalSchema = STRING_AGG(theTable, ', ')  from #tables
	--select @finalSchema

	--============ Now let's pass that for a question

	set @systemMessage = ''' You are an agent designed to return SQL statements with schema detail in <<data_sources>>.
			Given an input question, create a syntactically correct ODBC Driver 17 for SQL Server query to run.
			You can order the results by a relevant column to return the most interesting examples in the database.
			Never query for all the columns from a specific table, only ask for a the few relevant columns given the question.
			You MUST double check your query. User step by step thought process
			DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.
			Remember to format SQL query as in ODBC Driver 17 for SQL Server  in your response.
			remove any invalid characters and double check that the query will perform correctly, just return SQL statements, skip pleasentries
			return syntactically correct ODBC Driver 17 for SQL Server query ready to run, all fields or agregations that use fields with money type, return them as money type
			return SQL statements only, do not include thought process, do not query sys objects
		
			<<data_sources>>	
			''' +  @finalSchema + ' ## End <<data_sources>> ##'


	set @payload2 = 
						json_object(
							'messages': json_array(
									json_object(
										'role':'system',
										'content':'
											' + @systemMessage + '
										'
									),								
									json_object(
										'role':'user',
										'content': + @text
									)
							),
							'max_tokens': 4096,
							'temperature': 0.5,
							'frequency_penalty': 0,
							'presence_penalty': 0,
							'top_p': 0.95,
							'stop': null
						);


	--select @payload2

	exec @retval = sp_invoke_external_rest_endpoint
		@url =  @urlGPT4,
		@headers = @theHeadings,
		@method = 'POST',   
		@timeout = 120,
		@payload = @payload2,
		@response = @response output;

	--select @response

	drop table if exists #j;
	select * into #j from openjson(@response, '$.result.choices') c;
	--select * from #j

	declare @value varchar(max)

	select @value = [value] from #j


	select @query = [value] from openjson(@value, '$.message') where [key] = 'content'


	SELECT @query = REPLACE(@query, '`', '')
	SELECT @query = REPLACE(@query, 'sql', '')


	-- select @query

	EXEC sp_executesql @query;
END

 ```

 ### Task 3 - Ask Questions NLP

 Create a new query and test

 ```
 declare @text nvarchar(max)
declare @schema nvarchar(250) = 'SalesLT'
set @text = 'Is that true that top 20% customers generate 80% revenue ? What is their percentage of revenue contribution?'
execute [dbo].[SQLNLP] @text, @schema
 ```

 ```
 declare @text nvarchar(max)
declare @schema nvarchar(250) = 'SalesLT'
set @text = 'Is that true that top 20% customers generate 80% revenue ? please list those customers, give me details on their orders, including items they purchased'
execute [dbo].[SQLNLP] @text, @schema
 ```

 ```
 declare @text nvarchar(max)
declare @schema nvarchar(250) = 'SalesLT'
set @text = 'Which products have most seasonality in sales quantity, add the month they are purchased the least'
execute [dbo].[SQLNLP] @text, @schema
 ```
