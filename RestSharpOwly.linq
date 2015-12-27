<Query Kind="Statements">
  <Reference Relative="..\smiletwillio\bin\SmileBoxTwillio.dll">C:\gits\smiletwillio\bin\SmileBoxTwillio.dll</Reference>
  <Reference Relative="..\smiletwillio\bin\SmileLogic.dll">C:\gits\smiletwillio\bin\SmileLogic.dll</Reference>
  <NuGetReference>Newtonsoft.Json</NuGetReference>
  <NuGetReference>RestSharp</NuGetReference>
  <NuGetReference>Twilio</NuGetReference>
  <Namespace>RestSharp</Namespace>
  <Namespace>Newtonsoft.Json</Namespace>
</Query>

// RestSharp Help: http://restsharp.org/
// Ow.ly help:http://ow.ly/api-docs

// +++ Secret setup
dynamic secrets = JsonConvert.DeserializeObject(File.ReadAllText(@"c:/gits/igor2/secretBox.json"));
var key = secrets.OwlyApiKey;
if (key == null) throw new InvalidDataException("Missing Key");
// --- Secret setup

var client = new RestClient(" http://ow.ly/");
var request = new RestRequest("api/1.1/url/shorten", Method.GET);
request.AddObject(
	new
	{
		longUrl = "http://ig2600.blogspot.com",
		apiKey = key,
	});

// execute the 
client.BuildUri(request).Dump();
var response = client.Execute(request);
var content = response.Content; // raw cntent as string
content.Dump();