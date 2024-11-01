using System;
using System.IO;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Azure.WebJobs;
using Microsoft.Azure.WebJobs.Extensions.Http;
using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.Logging;
using Newtonsoft.Json;
using System.Data;
using Azure.Identity;
using Microsoft.Data.SqlClient;


namespace SQLRAGAzureFunction
{
    public static class SQLNLP
    {
        static string user_assigned_identity = Environment.GetEnvironmentVariable("user_assigned_identity");

        [FunctionName("SQLNLP")]
        public static async Task<IActionResult> Run(
            [HttpTrigger(AuthorizationLevel.Function, "get", "post", Route = null)] HttpRequest req,
            ILogger log)
        {
            try
            {
                // Existing code here
                log.LogInformation("C# HTTP trigger function processed a request.");
                               
                string question = req.Query["question"];
                string schema = req.Query["schema"];

                string requestBody = await new StreamReader(req.Body).ReadToEndAsync();
                dynamic data = JsonConvert.DeserializeObject(requestBody);
                schema = schema ?? data?.schema;
                question = question ?? data?.question;

                string result = ExecuteStoredProcedure( question, schema);

                string responseMessage = result;
                return new OkObjectResult(responseMessage);

            }
            catch (Exception ex)
            {
                log.LogError(ex, "An error occurred while executing the stored procedure.");
                return new StatusCodeResult(StatusCodes.Status500InternalServerError);
            }
        }

        private static string GetConnectionString()
        {
            string password = Environment.GetEnvironmentVariable("SQL_SECRET");
            string server = Environment.GetEnvironmentVariable("SQL_SERVER");
            string database = Environment.GetEnvironmentVariable("SQL_NPL_DB");
            string username = Environment.GetEnvironmentVariable("SQL_USERNAME");

            return $"Server=tcp:{server},1433;Initial Catalog={database};";

            //return $"Server={server};Database={database};User Id={username};Password={password};";
        }

        public static string ExecuteStoredProcedure(string question, string schema)
        {
            //connect to sql server using managed identities
            var tokenCredential = new DefaultAzureCredential(new DefaultAzureCredentialOptions
            {
                ManagedIdentityClientId = user_assigned_identity
            });

            var sqlConnection = new SqlConnection(GetConnectionString())
            {
                AccessToken = tokenCredential.GetToken(new Azure.Core.TokenRequestContext(new[] { "https://database.windows.net/.default" })).Token
            };
            
             using (SqlCommand command = new SqlCommand("[dbo].[SQLNLP]", sqlConnection))
                {
                    command.CommandType = CommandType.StoredProcedure;                  
                    command.Parameters.AddWithValue("@question", question);
                    command.Parameters.AddWithValue("@schema", schema);

                    sqlConnection.Open();

                   using (SqlDataReader reader = command.ExecuteReader())
                    {
                        DataTable dataTable = new DataTable();
                        dataTable.Load(reader);
                         sqlConnection.Close();
                        string jsonResult = JsonConvert.SerializeObject(dataTable);
                        return jsonResult;
                    }
                }
          
        }
    }
}
