using Azure.Identity;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Azure.WebJobs;
using Microsoft.Azure.WebJobs.Extensions.Http;
//using System.Data.SqlClient;
using Microsoft.Data.SqlClient;
using Microsoft.Extensions.Logging;
using Newtonsoft.Json;
using System;
using System.Data;
using System.IO;
using System.Threading.Tasks;


namespace Company.Function
{

    public static class AskDocumentQuestion
    {
        static string user_assigned_identity = Environment.GetEnvironmentVariable("user_assigned_identity");

        [FunctionName("AskDocumentQuestion")]
        public static async Task<IActionResult> Run(
            [HttpTrigger(AuthorizationLevel.Function, "get", "post", Route = null)] HttpRequest req,
            ILogger log)
        {
            try
            {
                // Existing code here
                log.LogInformation("C# HTTP trigger function processed a request.");

                string system_message = req.Query["prompt"];
                string question = req.Query["question"];

                string requestBody = await new StreamReader(req.Body).ReadToEndAsync();
                dynamic data = JsonConvert.DeserializeObject(requestBody);
                system_message = system_message ?? data?.prompt;
                question = question ?? data?.question;

                string result = ExecuteStoredProcedure(system_message, question,log);

                string responseMessage = result;
                return new OkObjectResult(responseMessage);

            }
            catch (Exception ex)
            {
                log.LogError(ex.Message, "An error occurred");
                return new StatusCodeResult(StatusCodes.Status500InternalServerError);
            }
        }

        private static string GetConnectionString()
        {
            string password = Environment.GetEnvironmentVariable("SQL_SECRET");
            string server = Environment.GetEnvironmentVariable("SQL_SERVER");
            string database = Environment.GetEnvironmentVariable("SQL_DB");
            string username = Environment.GetEnvironmentVariable("SQL_USERNAME");
            return $"Server=tcp:{server},1433;Initial Catalog={database};";
        }


        public static string ExecuteStoredProcedure(string system_message, string question,  ILogger log, int returnJson = 0)
        {
            //connect to sql server using managed identities

            try
            {
                var tokenCredential = new DefaultAzureCredential(new DefaultAzureCredentialOptions
                {
                    ManagedIdentityClientId = user_assigned_identity
                });

                var sqlConnection = new SqlConnection(GetConnectionString())
                {
                    AccessToken = tokenCredential.GetToken(new Azure.Core.TokenRequestContext(new[] { "https://database.windows.net/.default" })).Token
                };

                // sqlConnection.Open();         


                using (SqlCommand command = new SqlCommand("[dbo].[AskDocumentQuestion]", sqlConnection))
                {
                    command.CommandType = CommandType.StoredProcedure;
                    command.Parameters.AddWithValue("@systemmessage", system_message);
                    command.Parameters.AddWithValue("@text", question);
                    command.Parameters.AddWithValue("@returnJSON", returnJson);

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
            catch (Exception ex)
            {
                log.LogError(ex, "An error occurred while executing the stored procedure.");
                return ex.Message;
            }

        }



    }


}
