<Query Kind="Statements">
  <Reference Relative="..\smiletwillio\bin\SmileBoxTwillio.dll">C:\gits\smiletwillio\bin\SmileBoxTwillio.dll</Reference>
  <Reference Relative="..\smiletwillio\bin\SmileLogic.dll">C:\gits\smiletwillio\bin\SmileLogic.dll</Reference>
  <NuGetReference>RestSharp</NuGetReference>
  <NuGetReference>Twilio</NuGetReference>
  <Namespace>RestSharp</Namespace>
</Query>

// RestSharp Help: http://restsharp.org/
// Bit.ly HELP: http://dev.bitly.com/links.html#v3_shorten
// https://bitly.com/a/feelings
var client = new RestClient("https://api-ssl.bitly.com");
var request = new RestRequest("v3/shorten", Method.GET);
request.AddObject(
	new {
        longurl="http://ig2600.blogspot.com",
        // domain="sadto.me",
		domain="luvit.me",
		login="++",
		apikey="--",
		});

// execute the request
var response = client.Execute(request);
var content = response.Content; // raw cntent as string
content.Dump();