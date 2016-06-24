<Query Kind="Statements">
  <Reference Relative="..\margiebot\MargieBot.UI\Libs\BazamWPF.dll">C:\gits\margiebot\MargieBot.UI\Libs\BazamWPF.dll</Reference>
  <Reference Relative="..\margiebot\MargieBot.UI\bin\Debug\MargieBot.dll">C:\gits\margiebot\MargieBot.UI\bin\Debug\MargieBot.dll</Reference>
  <Reference Relative="..\margiebot\MargieBot.UI\Libs\websocket-sharp.dll">C:\gits\margiebot\MargieBot.UI\Libs\websocket-sharp.dll</Reference>
  <NuGetReference>Bazam</NuGetReference>
  <NuGetReference>Bazam.Http</NuGetReference>
  <NuGetReference>Bazam.WPF</NuGetReference>
  <NuGetReference>Microsoft.TeamFoundationServer.ExtendedClient</NuGetReference>
  <NuGetReference>Microsoft.VisualStudio.Services.Client</NuGetReference>
  <NuGetReference>Microsoft.VisualStudio.Services.InteractiveClient</NuGetReference>
  <NuGetReference>RestSharp</NuGetReference>
  <Namespace>MargieBot</Namespace>
  <Namespace>MargieBot.Models</Namespace>
  <Namespace>MargieBot.Responders</Namespace>
  <Namespace>Microsoft.TeamFoundation.WorkItemTracking.WebApi</Namespace>
  <Namespace>Microsoft.TeamFoundation.WorkItemTracking.WebApi.Models</Namespace>
  <Namespace>Microsoft.VisualStudio.Services.Client</Namespace>
  <Namespace>Microsoft.VisualStudio.Services.Common</Namespace>
  <Namespace>Newtonsoft.Json.Linq</Namespace>
  <Namespace>RestSharp</Namespace>
</Query>

var secrets = JObject.Parse(File.ReadAllText(@"c:/gits/igor2/secretBox.json"));
var slackKey = secrets["BundleTfsBotSlackKey"];
var vsoKey= secrets["BundleTfsBotVsoPAT"];
var owlyKey = secrets["OwlyApiKey"];

if (slackKey == null) throw new InvalidDataException("Missing Key");
if (vsoKey == null) throw new InvalidDataException("Missing Key");
if (owlyKey == null) throw new InvalidDataException("Missing Key");



var collectionUri = "https://dlwteam.visualstudio.com/DefaultCollection";
var connection = new VssConnection(new Uri(collectionUri), new VssBasicCredential("", vsoKey.ToString()));
var witClient = connection.GetClient<WorkItemTrackingHttpClient>();

var idToVsoUrl = new Func<int, string>((id) =>
{
	var client = new RestClient(" http://ow.ly/");
	var request = new RestRequest("api/1.1/url/shorten", Method.GET);
	request.AddObject(
		new
		{
			longUrl = $"https://dlwteam.visualstudio.com/DefaultCollection/OneClip/_workItems?triage=true&_a=edit&id={id}",
			apiKey = owlyKey,
		});

	// execute the 
	client.Execute(request).Content.Dump();
	return JObject.Parse(client.Execute(request).Content)["results"]["shortUrl"].ToString();
});

var getWI = new Func<string, WorkItem>(id=>
{	
	try
	{
		var workItemId = Int32.Parse(id);
		return witClient.GetWorkItemAsync(workItemId).Result;
	}
	catch (Exception)
	{
		return null;
	}
});


while (true)
{
	Bot tfsBot = new Bot();
	IResponder myResponder = tfsBot.CreateResponder(
		(ResponseContext context) =>
		{
			return !(context.Message.User.IsSlackbot);
		},
		(ResponseContext context) =>
		{
			var message = context.Message.Text;
			message.Dump("incoming");
			var channel = context.Message.ChatHub.Name;
			var matches = Regex.Matches(message, "#(\\d+)");
			var totalResponses = new List<string>();
			foreach (Match match in matches)
			{
				var parsed = match.Groups[1].Value;
				parsed.Dump("Parsed ID");
				var wi = getWI(parsed);
				if (wi == null) continue;
				wi.Dump();
				var wiState = wi.Fields["System.State"].ToString();
				var response = $"*#{wi.Id}:* {wi.Fields["System.Title"]}";
				response += $"\n  *Pri*: {wi.Fields["Microsoft.VSTS.Common.Priority"]} *State:* {wiState} *Assigned To*:{wi.Fields.GetValueOrDefault("System.AssignedTo") ?? "Not yet assigned"}\n{idToVsoUrl(wi.Id.Value)}";
				totalResponses.Add(response);
			}
			totalResponses.Dump();
			var finalText = String.Join("\n-------\n", totalResponses);
			finalText.Dump("finalText");
			return finalText;
		}
	);

	tfsBot.Responders.Add(myResponder);
	tfsBot.Aliases = new[] { "bundletfsbot" };

	await tfsBot.Connect(slackKey.ToString());
	var sleepTime = TimeSpan.FromHours(1.0);
	DateTime.Now.Dump($"Sleeping for {sleepTime.TotalHours} hours");
	Thread.Sleep(sleepTime);
	tfsBot.Disconnect();
}

//witClient.cre