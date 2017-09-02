<Query Kind="Program">
  <Reference>&lt;RuntimeDirectory&gt;\System.Net.Http.dll</Reference>
  <NuGetReference>Flurl.Http</NuGetReference>
  <Namespace>Flurl</Namespace>
  <Namespace>Flurl.Http</Namespace>
  <Namespace>Flurl.Http.Configuration</Namespace>
  <Namespace>Flurl.Http.Content</Namespace>
  <Namespace>Flurl.Http.Testing</Namespace>
  <Namespace>Flurl.Util</Namespace>
  <Namespace>Newtonsoft.Json</Namespace>
  <Namespace>Newtonsoft.Json.Linq</Namespace>
  <Namespace>System.Threading.Tasks</Namespace>
</Query>


class Results
{
	public OwlyResonse results {get; set;}
}
class OwlyResonse
{
	public string hash { get; set;}
	public string shortUrl { get; set;}
	public string longUrl { get; set;}
}

async Task Main()
{
	// RestSharp Help: http://restsharp.org/
	// Ow.ly help:http://ow.ly/api-docs
	
	// +++ Secret setup
	var secrets = JObject.Parse(File.ReadAllText(@"c:/gits/igor2/secretBox.json"));
	var key = secrets["OwlyApiKey"].ToString();
	if (key == null) throw new InvalidDataException("Missing Key");
	// --- Secret setup
	
	var inputs = new {
		apiKey=key,
		longUrl = "http://ig66.blogspot.com"
	};
	
	var url = await "http://ow.ly/".AppendPathSegment("api/1.1/url/shorten").SetQueryParams(inputs).GetAsync().ReceiveJson<Results>();
	url.Dump();
}

// Define other methods and classes here
