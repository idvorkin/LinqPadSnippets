<Query Kind="Program">
  <Reference>&lt;RuntimeDirectory&gt;\System.Net.Http.dll</Reference>
  <NuGetReference>Flurl.Http</NuGetReference>
  <NuGetReference>Html2Markdown</NuGetReference>
  <NuGetReference>HtmlAgilityPack</NuGetReference>
  <Namespace>Flurl</Namespace>
  <Namespace>Flurl.Http</Namespace>
  <Namespace>Flurl.Http.Configuration</Namespace>
  <Namespace>Flurl.Http.Content</Namespace>
  <Namespace>Flurl.Http.Testing</Namespace>
  <Namespace>Flurl.Util</Namespace>
  <Namespace>HtmlAgilityPack</Namespace>
  <Namespace>Newtonsoft.Json</Namespace>
  <Namespace>Newtonsoft.Json.Linq</Namespace>
  <Namespace>System.Net.Http</Namespace>
  <Namespace>System.Threading.Tasks</Namespace>
</Query>

internal class OneNoteAPI
{
	public const string url = "https://www.onenote.com/api/v1.0/me/notes";
}

public class Page
{
	public string id;
	public string title;
	public string oneNoteClientUrl;
	public string oneNoteWebUrl;
	
	public static Page fromJToken(JToken t) => new Page()
	{
		id = t["id"].ToString(),
		title = t["title"].ToString(),
		oneNoteClientUrl = t["links"]["oneNoteClientUrl"]["href"].ToString(),
		oneNoteWebUrl = t["links"]["oneNoteClientUrl"]["href"].ToString()
	};
	public static bool IsValidJToken(JToken t) => t["title"] != null;
	public string toContent(string token)
	{
		return OneNoteAPI.url.AppendPathSegment($"pages/{id}/content").WithOAuthBearerToken(token).GetStringAsync().Result;
	}
}
public class Section
{
	public string id;
	public string name;
	public string pagesUrl;
	public static Section fromJToken(JToken t) => new Section()
	{
		id = t["id"].ToString(),
		name = t["name"].ToString(),
		pagesUrl = t["pagesUrl"].ToString()
	};
	public IEnumerable<Page> toPages(string token)
	{
		var res = OneNoteAPI.url.AppendPathSegment($"sections/{id}/pages").SetQueryParam("top", "100").WithOAuthBearerToken(token).GetStringAsync().Result;
		var ss = JObject.Parse(res);
		return ss["value"].Children().Where(Page.IsValidJToken).Select(Page.fromJToken);
	}
}
public class Notebook
{
	public string id;
	public string name;
	public string oneNoteClientUrl;
	public string oneNoteWebUrl;
	public static Notebook fromJToken(JToken t) => new Notebook()
	{
		id = t["id"].ToString(),
		name = t["name"].ToString(),
		oneNoteClientUrl = t["links"]["oneNoteClientUrl"]["href"].ToString(),
		oneNoteWebUrl = t["links"]["oneNoteClientUrl"]["href"].ToString()
	};
	public IEnumerable<Section> toSections(string token)
	{
		var res = OneNoteAPI.url.AppendPathSegment($"notebooks/{id}/sections").WithOAuthBearerToken(token).GetStringAsync().Result;
		var ss = JObject.Parse(res);
		return ss["value"].Children().Select(Section.fromJToken);
	}
}
async Task Main()
{	
	//HtmlToMarkDown();
	Scratch();
}
void HtmlToMarkDown()
{
	var onenoteHtml = File.ReadAllText(@"c:\temp\dailyTemplate.html");
	var onenoteMarkdown = new Html2Markdown.Converter().Convert(onenoteHtml);
	onenoteMarkdown.Dump();
}
async Task<Page> GetPage(string notebook, string section, string title, string token)
{
	var notebooksJson = await OneNoteAPI.url.AppendPathSegment("notebooks").WithOAuthBearerToken(token).GetStringAsync();
	return JObject.Parse(notebooksJson)["value"].Children().Select(Notebook.fromJToken)
   .Where(n => n.name == "BlogContentAndResearch")
   .SelectMany(n => n.toSections(token))
   .Single(s => s.name == "Marmalade")
   .toPages(token)
   .Single(s => s.title == "Igor's OLR");
}

async Task Scratch()
{
	// Get a bearer token. Two approaches in the sample:
	// 1) Use the mechanisim in writeUrlToPageOneNote and copy from it's cache file: 
	//   var token = File.ReadAllText(@"c:\Users\idvor\AppData\Local\Temp\saveOneNoteAccessToken_18668");
	// 2) Copy the token as cached by the webapp at @ <url>/.auth/me: 
	//var token = "EwAYA61DBAAUGCCXc8wU/zFu9QnLdZXy+YnElFkAAQiA4nGSPxiyW0WStV8Gg+ERCeaevIsv+vl78Kiy643AE4jZS+R1qXd0GZzJvKR8q6mVS5YTv+IJUzRyC2EMatTUChD1cnBXla07VaIVnQH4l1GMKeXp0quM+xsJXJ+OpBUbSvdGW2BLuVcZ9bGubiWCzV2i+B0swfMxbEG2nYrCORXRI/o3ZfqF7MYzLWLzHWi9EdmmKgS/H0ZyacFShpxDTIb12xCUAim/aXPmn9pDicdBMqUZc0cICTLKrLa6nlh3z+tc3Y8npsDeVSqLs/TvAxkLv62Ov3282E00zSkjJ264fjeXUz2oPsLciws4HNwh7AWnSSd1M376p1sEDmUDZgAACASl5JwSfZBr6AHDPGd2erubbmLG5t4Oqaew+EQUvNIXkhOi8n/T53TG/3HIQRQxg/JBk6/PJgUilQ51pZVgS2CjC21gEcvUJVymdyjLuarJgbXtoVMyR4CQdy+G2ICW5iv7ZI5B8MspDvWuwyJ2W/24/Izmv4kRr4xpM/E0VtrtiqvZ3F5w+I+P8DoNeIbdoxArfbLMSffegIg0rrjG2a7qycCgq/YVcwkBtfTxlwkfgivYvOCApIscmuOU+5yz6a+Tgy3RMvDBuPbSuk643OTIcUzGJdPw1SUhafO0inw3riy925UrzkBRhaFFhKcdBJptf0yrpH9VbyGZoNmcdM+H5RTXUtU/UH/a94qzWE07OU5fVEKGskD/bDfPLPdopfO3RJnT6owojbU92oyqQoZBFdBiKmxnxmRtABAIMALaKu6qm/VPEv+l4ETy612qtW8esd5U11NsXmEgwVRdHeDwigWbOvPak69ouQ5D4Zo+jU0t4grjf3y8CWoNFfstV1k9XRIrH9DWE/tOM0p0W0yAbtHSLHEuxnDbbIBPCQ7m1IDbL55wgcw0eDlPGTBoNj3Rj7Gew932/02ljytsHz2JfROHFJyKiurfR/QxC21gFsxYWdI0HE7aJ7AvGftq3fcpAJsHHHnFNY9PwQ3zFfFAjQwC";
	
	var token = File.ReadAllText(@"C:\Users\idvor\AppData\Local\Temp\saveOneNoteAccessToken_7908");
	var notebooksJson = await OneNoteAPI.url.AppendPathSegment("notebooks").WithOAuthBearerToken(token).GetStringAsync();
	
	var peopleSection = JObject.Parse(notebooksJson)["value"].Children().Select(Notebook.fromJToken)
	.Where(n=>n.name == "BlogContentAndResearch")
	.SelectMany(n => n.toSections(token))
	.Single(s=>s.name == "People");

	var igorOLR = await GetPage("BlogContentAndResearch","Marmalade","Igor's OLR",token);
	var olrAsHtml = igorOLR.toContent(token);
	var olrAsMarkdown = new Html2Markdown.Converter().Convert(olrAsHtml);
	olrAsMarkdown.Dump("OLR As Markdown");


	peopleSection.Dump();
	//peopleSection.toPages(token).Dump();

	var templatePages = JObject.Parse(notebooksJson)["value"].Children().Select(Notebook.fromJToken)
	.Where(n => n.name == "Templates")
	.SelectMany(n => n.toSections(token))
	.Single(s => s.name == "Default")
	.toPages(token);
	templatePages.Dump();
	
	var dailyTemplate =  templatePages.Single(x=>x.title=="Daily");
	dailyTemplate.Dump();


	// Create page based on a template 
	//var dailyTemplateHtml = dailyTemplate.toContent(token);
	// dailyTemplateHtml.Dump();
	// var dailyTemplateHtml = File.ReadAllText(@"c:\temp\dailyTemplate.html");
	//var ret = await OneNoteAPI.url.AppendPathSegment("pages").WithOAuthBearerToken(token).PostAsync(new StringContent(dailyTemplateHtml, System.Text.Encoding.UTF8, "text/html"));
	//ret.Dump();
}



// Define other methods and classes here