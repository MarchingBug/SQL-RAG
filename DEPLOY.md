# Deployment instructions - How do I put this together

   - Follow the instructions on the root ReadMe file to deploy the SQL server database and chunk the parquet files.
   - Deploy the azure function under the SQLRAGAzureFunction folder, this is a C# azure function, just becuase C# & SQL play well together.
   - Deploy the azure function under the SummarizeDocs folder, this is a pythin function, just beacuser python and parquet files play well together.
   - Deploy the Front end,  this is a razor application 
