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
  <Namespace>MargieBot</Namespace>
  <Namespace>MargieBot.Models</Namespace>
  <Namespace>MargieBot.Responders</Namespace>
  <Namespace>Microsoft.TeamFoundation.WorkItemTracking.WebApi</Namespace>
  <Namespace>Microsoft.VisualStudio.Services.Client</Namespace>
  <Namespace>Microsoft.VisualStudio.Services.Common</Namespace>
  <Namespace>Newtonsoft.Json.Linq</Namespace>
  <Namespace>Microsoft.TeamFoundation.WorkItemTracking.WebApi.Models</Namespace>
</Query>

var secrets = JObject.Parse(File.ReadAllText(@"c:/gits/igor2/secretBox.json"));
var slackKey = secrets["BundleTfsBotSlackKey"];
var vsoKey= secrets["BundleTfsBotVsoPAT"];

if (slackKey == null) throw new InvalidDataException("Missing Key");
if (vsoKey == null) throw new InvalidDataException("Missing Key");



var collectionUri = "https://dlwteam.visualstudio.com/DefaultCollection";
var connection = new VssConnection(new Uri(collectionUri), new VssBasicCredential("", vsoKey.ToString()));
var  witClient = connection.GetClient<WorkItemTrackingHttpClient>();

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

Bot tfsBot = new Bot();
IResponder myResponder = tfsBot.CreateResponder(
	(ResponseContext context) =>
	{
		return !(context.Message.User.IsSlackbot);
	},
	(ResponseContext context) =>
	{
		var message = context.Message.Text;
		var channel = context.Message.ChatHub.Name;
		var match = Regex.Match(message, "#(\\d+)");
		if (!match.Success) return null;
		var wi = getWI(match.Groups[1].Value);
		if (wi == null) return null;
		wi.Dump();
		var wiState= wi.Fields["System.State"].ToString();
		var shortUrl = "http://sadto.me/1M8VT01";
		if (wiState== "Done" || wiState== "Removed")
		{
			shortUrl="http://yaythis.me/1RGSLVW";
		}
		var response = $"*#{wi.Id}:* {wi.Fields["System.Title"]} {shortUrl}#id={wi.Id}";
		response += $"\n  *Pri*: {wi.Fields["Microsoft.VSTS.Common.Priority"]} *State:* {wiState} *Assigned To*:{wi.Fields.GetValueOrDefault("System.AssignedTo")?? "Not yet assigned"}";
		return response;
    }
);

tfsBot.Responders.Add(myResponder);
await tfsBot.Connect(slackKey.ToString());
"Sleeping".Dump();
Thread.Sleep(Timeout.Infinite);
