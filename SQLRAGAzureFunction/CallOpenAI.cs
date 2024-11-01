using System;
using System.IO;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Azure.WebJobs;
using Microsoft.Azure.WebJobs.Extensions.Http;
using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.Logging;
using Newtonsoft.Json;
using System.Net.Http;
using System.Text;
using Microsoft.Extensions.Configuration;
using Azure;
using OpenAI.Chat;
using Azure.AI.OpenAI;

namespace SQLRAGAzureFunction
{
    public static class CallOpenAI
    {       
        private static ChatClient OpenAIChat ()
        {


            AzureOpenAIClient azureClient = new(
                        new Uri(Environment.GetEnvironmentVariable("OPENAI_ENDPOINT")),
                        new AzureKeyCredential(Environment.GetEnvironmentVariable("OPENAI_API_KEY")));
            ChatClient _client = azureClient.GetChatClient(Environment.GetEnvironmentVariable("OPENAI_API_MODEL"));

            return _client;

        }


        [FunctionName("CallOpenAI")]
        public static async Task<IActionResult> Run(
            [HttpTrigger(AuthorizationLevel.Function, "get", "post", Route = null)] HttpRequest req,
            ILogger log)
        {
            log.LogInformation("C# HTTP trigger function processed a request.");

            string systemMessage = req.Query["systemMessage"];
            string userMessage = req.Query["userMessage"];

            string requestBody = await new StreamReader(req.Body).ReadToEndAsync();
            dynamic data = JsonConvert.DeserializeObject(requestBody);
            systemMessage = systemMessage ?? data?.systemMessage;
            userMessage = userMessage ?? data?.userMessage;


            if (string.IsNullOrEmpty(systemMessage) || string.IsNullOrEmpty(userMessage))
            {
                return new BadRequestObjectResult("Please pass both systemMessage and userMessage in the request body");
            }


            string responseMessage = await getChatCompletion(systemMessage, userMessage);
          

            return new OkObjectResult(responseMessage);
        }

        private static async Task<string> getChatCompletion(string prompt, string message)
        {

            try
            {
                if (string.IsNullOrEmpty(prompt) || string.IsNullOrEmpty(message))
                {
                    return "";
                }

                ChatClient _openAIclient = OpenAIChat();
               

                ChatCompletion completion = await _openAIclient.CompleteChatAsync(
               [
                   // System messages represent instructions or other guidance about how the assistant should behave
                   new SystemChatMessage(prompt),
                // User messages represent user input, whether historical or the most recen tinput
                new UserChatMessage(message)
                ]);

                string response = completion.Content[0].Text;
                return response;

            }
            catch (Exception ex)
            {
                return ex.Message;
            }
        }
    }

}
