<Query Kind="Program">
  <Reference>&lt;RuntimeDirectory&gt;\Microsoft.Build.Framework.dll</Reference>
  <Reference>&lt;RuntimeDirectory&gt;\Microsoft.Build.Tasks.v4.0.dll</Reference>
  <Reference>&lt;RuntimeDirectory&gt;\Microsoft.Build.Utilities.v4.0.dll</Reference>
  <Reference>&lt;RuntimeDirectory&gt;\System.ComponentModel.DataAnnotations.dll</Reference>
  <Reference>&lt;RuntimeDirectory&gt;\System.Configuration.dll</Reference>
  <Reference>&lt;RuntimeDirectory&gt;\System.Design.dll</Reference>
  <Reference>&lt;RuntimeDirectory&gt;\System.DirectoryServices.dll</Reference>
  <Reference>&lt;RuntimeDirectory&gt;\System.DirectoryServices.Protocols.dll</Reference>
  <Reference>&lt;RuntimeDirectory&gt;\System.EnterpriseServices.dll</Reference>
  <Reference>&lt;RuntimeDirectory&gt;\System.Net.Http.dll</Reference>
  <Reference>&lt;RuntimeDirectory&gt;\System.Runtime.Caching.dll</Reference>
  <Reference>&lt;RuntimeDirectory&gt;\System.Security.dll</Reference>
  <Reference>&lt;RuntimeDirectory&gt;\System.ServiceProcess.dll</Reference>
  <Reference>&lt;RuntimeDirectory&gt;\System.Web.ApplicationServices.dll</Reference>
  <Reference>&lt;RuntimeDirectory&gt;\System.Web.dll</Reference>
  <Reference>&lt;RuntimeDirectory&gt;\System.Web.RegularExpressions.dll</Reference>
  <Reference>&lt;RuntimeDirectory&gt;\System.Web.Services.dll</Reference>
  <Reference>&lt;RuntimeDirectory&gt;\System.Windows.Forms.dll</Reference>
  <NuGetReference>Newtonsoft.Json</NuGetReference>
  <NuGetReference>RestSharp</NuGetReference>
  <Namespace>Newtonsoft.Json</Namespace>
  <Namespace>System</Namespace>
  <Namespace>System.Collections.Generic</Namespace>
  <Namespace>System.Net.Http</Namespace>
  <Namespace>System.Net.Http.Headers</Namespace>
  <Namespace>System.Text</Namespace>
  <Namespace>System.Threading.Tasks</Namespace>
  <Namespace>System.Web</Namespace>
  <Namespace>RestSharp</Namespace>
  <Namespace>RestSharp.Authenticators</Namespace>
</Query>

static void Main()
{
	string accountKey = "--";
	string ServiceBaseUri = "https://api.datamarket.azure.com/data.ashx/amla/text-analytics/";
	var inputText = File.ReadAllText(@"C:\Users\igord\OneDrive\750words\8_10_2015.txt");
	var textAnalytics = new RestClient(new Uri(ServiceBaseUri));
	textAnalytics.Authenticator = new HttpBasicAuthenticator("AccountKey", accountKey);

	var keyPhrases = textAnalytics.Execute<KeyPhraseResult>(new RestRequest("v1/GetKeyPhrases").AddObject(new { Text = inputText }));
	keyPhrases.Data.Dump();

	var sentimentAnalysis = textAnalytics.Execute<SentimentResult>(new RestRequest("v1/GetSentiment").AddObject(new { Text = inputText }));
	sentimentAnalysis.Data.Dump();
}

public class KeyPhraseResult
{
	public List<string> KeyPhrases { get; set; }
}


public class SentimentResult
{
	public double Score { get; set; }
}
