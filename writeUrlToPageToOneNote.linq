<Query Kind="Program">
  <Reference>&lt;RuntimeDirectory&gt;\Accessibility.dll</Reference>
  <Reference>&lt;RuntimeDirectory&gt;\System.Configuration.dll</Reference>
  <Reference>&lt;RuntimeDirectory&gt;\System.Deployment.dll</Reference>
  <Reference>&lt;RuntimeDirectory&gt;\System.Net.Http.dll</Reference>
  <Reference>&lt;RuntimeDirectory&gt;\System.Runtime.Serialization.Formatters.Soap.dll</Reference>
  <Reference>&lt;RuntimeDirectory&gt;\System.Security.dll</Reference>
  <Reference>&lt;RuntimeDirectory&gt;\System.Windows.Forms.dll</Reference>
  <NuGetReference>Newtonsoft.Json</NuGetReference>
  <NuGetReference>RestSharp</NuGetReference>
  <Namespace>Newtonsoft.Json</Namespace>
  <Namespace>Newtonsoft.Json.Linq</Namespace>
  <Namespace>System</Namespace>
  <Namespace>System.Collections.Generic</Namespace>
  <Namespace>System.Collections.Specialized</Namespace>
  <Namespace>System.Diagnostics</Namespace>
  <Namespace>System.IO</Namespace>
  <Namespace>System.Linq</Namespace>
  <Namespace>System.Net</Namespace>
  <Namespace>System.Net.Http</Namespace>
  <Namespace>System.Net.Http.Headers</Namespace>
  <Namespace>System.Security.Policy</Namespace>
  <Namespace>System.Text</Namespace>
  <Namespace>System.Text.RegularExpressions</Namespace>
  <Namespace>System.Threading</Namespace>
  <Namespace>System.Threading.Tasks</Namespace>
  <Namespace>System.Windows.Forms</Namespace>
  <Namespace>RestSharp</Namespace>
  <Namespace>RestSharp.Authenticators</Namespace>
</Query>

void Main()
{
	var cacheAccessTokenFile = Path.Combine(Path.GetTempPath(), $"saveOneNoteAccessToken_{Util.HostProcessID}");
	cacheAccessTokenFile.Dump();
	string accessToken = "";
	if (File.Exists(cacheAccessTokenFile))
    {
		accessToken = File.ReadAllText(cacheAccessTokenFile);
	}
	else
	{
		var auth = new LiveAuth(new ClientIdentifier());
		accessToken = auth.GetOAuthUserAccessToken();
		File.WriteAllText(cacheAccessTokenFile, accessToken);
		// XXX: Handle expired token.
	}

	var c = new OneNoteSamples(accessToken);
	var url = "http://www.bing.com";
	var pageName = "Another Stab";
	var response = c.CreatePageFromURL("OneClip-Pinned Urls", url, pageName);
	response.Dump();
}

// I believe it is safe to list my secretid since it represents an app that I don't care about.
// Someone could take my client id and use it for nefarious puproses and then tie it back to my account, but that's a big stretch.
internal class ClientIdentifier
{
	public string ClientId = "0000000048130833";
	public string Secret = "40lRVb3d17e0AsQh3n0oFMXr3q-nkjPw";
};

class LiveAuth
{
	public LiveAuth(ClientIdentifier client)
	{
		this.client = client;
	}

	private readonly ClientIdentifier client;
	private static readonly string wlCallBackUri = "https://login.live.com/oauth20_desktop.srf";

	private static Uri CreateClientAccessCodeUrl(IEnumerable<string> scopes, string cliend_id)
	{

		string authorizeBase = "https://login.live.com/oauth20_authorize.srf";
		string urlParms = $"client_id={cliend_id}&scope={String.Join("%20", scopes)}&response_type=code&redirect_uri={Uri.EscapeDataString(wlCallBackUri)}";
		return new Uri($"{authorizeBase}?{urlParms}");
	}

	private static IEnumerable<string> Scopes = new[] { "wl.signin", "Office.onenote_create" };

	private static Uri RunWebBrowserTillReturnedToUrl(Uri uri, Func<string, bool> stopCondition)
	{
		var window = new Form()
		{
			Width = 440,
			Height = 600
		};

		Uri url = null;

		Action<object, WebBrowserDocumentCompletedEventArgs> pageLoaded = (o, args) =>
       {
           url = args.Url;
           if (stopCondition(url.OriginalString))
           {
               window.Close();
           }
       };
       
       var web = new WebBrowser()
       {
           Width = window.Width,
           Height = window.Height,
           Url = uri
       };
       web.DocumentCompleted += new WebBrowserDocumentCompletedEventHandler(pageLoaded);
       window.Controls.Add(web);
       window.ShowDialog();
       return url;
   }

   private string GetOAuthClientAccessCode()
   {
       string code = "";

       // The WebBrower must run on an stA thread.
       var staThread = new Thread(() =>
       {
           var accessTokenUrl = CreateClientAccessCodeUrl(Scopes, client.ClientId);
           var urlWithClientAccessCode  = RunWebBrowserTillReturnedToUrl(accessTokenUrl, (url) => (url.Contains("error") || url.Contains("code=")) );
           if (urlWithClientAccessCode != null)
           {
               // XXX: This does nto handle errors.
               var queryParams =
                   Regex.Matches(urlWithClientAccessCode.Query, "([^?=&]+)(=([^&]*))?") .Cast<Match>() .ToDictionary(x => x.Groups[1].Value, x => x.Groups[3].Value);
               code = queryParams["code"];
           }
       });

       staThread.SetApartmentState(ApartmentState.STA);
       staThread.Start();
       staThread.Join();
       return code;
   }

   public String GetOAuthUserAccessToken()
   {
       var userAccessTokenParameters = new NameValueCollection();
       userAccessTokenParameters["client_id"] = client.ClientId;
       userAccessTokenParameters["client_secret"] = client.Secret;
       userAccessTokenParameters["redirect_uri"] = wlCallBackUri;
       userAccessTokenParameters["grant_type"] = "authorization_code";
       userAccessTokenParameters["code"] = GetOAuthClientAccessCode();

       var wc = new WebClient();
       var accessTokenUrl = "https://login.live.com/oauth20_token.srf";
       var response = wc.UploadValues(accessTokenUrl, "POST", userAccessTokenParameters);
       var reponseAsString = Encoding.Default.GetString(response);
       var parsedToken = JToken.Parse(reponseAsString);
       return parsedToken.Value<string>("access_token");
   }
}


/// <summary>
/// Base class representing a simplified response from a service call 
/// </summary>
public abstract class StandardResponse
{
	public HttpStatusCode StatusCode { get; set; }

	/// <summary>
	/// Per call identifier that can be logged to diagnose issues with Microsoft support
	/// </summary>
	public string CorrelationId { get; set; }

	public async static Task<StandardResponse> TranslateResponse(HttpResponseMessage response)
	{
		StandardResponse standardResponse;
		if (response.StatusCode == HttpStatusCode.Created)
		{
			dynamic responseObject = JsonConvert.DeserializeObject(await response.Content.ReadAsStringAsync());
			standardResponse = new CreateSuccessResponse
			{
				StatusCode = response.StatusCode,
				OneNoteClientUrl = responseObject.links.oneNoteClientUrl.href,
				OneNoteWebUrl = responseObject.links.oneNoteWebUrl.href
			};
		}
		else
		{
			standardResponse = new StandardErrorResponse
			{
				StatusCode = response.StatusCode,
				Message = await response.Content.ReadAsStringAsync()
			};
		}

		// Extract the correlation id.  Apps should log this if they want to collcet the data to diagnose failures with Microsoft support 
		IEnumerable<string> correlationValues;
		if (response.Headers.TryGetValues("X-CorrelationId", out correlationValues))
		{
			standardResponse.CorrelationId = correlationValues.FirstOrDefault();
		}

		return standardResponse;
	}

}

/// <summary>
/// Class representing standard error from the service
/// </summary>
public class StandardErrorResponse : StandardResponse
{
	/// <summary>
	/// Error message - intended for developer, not end user
	/// </summary>
	public string Message { get; set; }

	/// <summary>
	/// Constructor
	/// </summary>
	public StandardErrorResponse()
	{
		this.StatusCode = HttpStatusCode.InternalServerError;
	}
}


/// <summary>
/// Class representing a successful create call from the service
/// </summary>
public class CreateSuccessResponse : StandardResponse
{
	/// <summary>
	/// URL to launch OneNote rich client
	/// </summary>
	public string OneNoteClientUrl { get; set; }

	/// <summary>
	/// URL to launch OneNote web experience
	/// </summary>
	public string OneNoteWebUrl { get; set; }
}


public class OneNoteSamples
{
	private static readonly string PagesEndPoint = "https://www.onenote.com/api/v1.0/pages";

	private string DEFAULT_SECTION_NAME = "Quick Notes";

	private string AuthToken;
	public OneNoteSamples(string authToken)
	{
		AuthToken = authToken;
	}

	public Uri GetPagesEndpoint(string specifiedSectionName)
	{
		string sectionNameToUse;
		if (specifiedSectionName != null)
		{
			sectionNameToUse = specifiedSectionName;
		}
		else
		{
			sectionNameToUse = DEFAULT_SECTION_NAME;
		}
		return new Uri(PagesEndPoint + "/?sectionName=" + sectionNameToUse);
	}

	/// <summary>
	/// Create a page with an image of a URL on it.
	/// </summary>
	/// <param name="debug">Run the code under the debugger</param>
	async public Task<StandardResponse> CreatePageFromURL(string sectionName, string url, string urlTitle)
	{
		var client = new HttpClient();
		client.DefaultRequestHeaders.Accept.Add(new MediaTypeWithQualityHeaderValue("application/json"));
		client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", this.AuthToken);

		string simpleHtml = @"<html>" +
							"<head>" +
							$"<title>{urlTitle}</title>" +
							$"<meta name=\"created\" content=\"{DateTime.Now.ToString("o")}\" />" +
								"</head>" +
								"<body>" +
								$" <p> source: <a href='{url}'> </p>" +
								$"<img data-render-src='{url}' alt=\"An important web page\"/>" +
								$"<p> Copied using <a href=\"http://OneClip.com\">OneClip</a> on {DateTime.Now.ToShortDateString()}.</p>" +
									"<ul>" +
									"<li> List Item 1</li>" +
									"<li> List Item 2 " +
											"<li>Nested List #3</li>" +
									"</li>" +
									"<li> List Item 3</li>" +
									"</ul>" +
								"</body>" +
								"</html>";

		var createMessage = new HttpRequestMessage(HttpMethod.Post, GetPagesEndpoint(sectionName))
		{
			Content = new StringContent(simpleHtml, System.Text.Encoding.UTF8, "text/html")
		};

		HttpResponseMessage response = await client.SendAsync(createMessage);
		return await StandardResponse.TranslateResponse(response);
	}
}