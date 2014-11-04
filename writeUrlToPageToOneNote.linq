<Query Kind="Program">
  <Reference>&lt;RuntimeDirectory&gt;\Accessibility.dll</Reference>
  <Reference>&lt;RuntimeDirectory&gt;\System.Configuration.dll</Reference>
  <Reference>&lt;RuntimeDirectory&gt;\System.Deployment.dll</Reference>
  <Reference>&lt;RuntimeDirectory&gt;\System.Net.Http.dll</Reference>
  <Reference>&lt;RuntimeDirectory&gt;\System.Runtime.Serialization.Formatters.Soap.dll</Reference>
  <Reference>&lt;RuntimeDirectory&gt;\System.Security.dll</Reference>
  <Reference>&lt;RuntimeDirectory&gt;\System.Windows.Forms.dll</Reference>
  <NuGetReference>Newtonsoft.Json</NuGetReference>
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
  <Namespace>Newtonsoft.Json.Linq</Namespace>
  <Namespace>Newtonsoft.Json</Namespace>
</Query>

void Main()
{
	var auth = new LiveAuth(new Client());
	var c = new CreateExamples(auth.GetOAuthUserAccessToken());
	var url = "http://www.google.com";
	var urlTitle = "www.google.com";
	var response = c.CreatePageWithUrl("OneClip",url,urlTitle);
	response.Wait();
}

internal class Client
{
   public string ClientId = "0000000048130833";
   public string Secret = "40lRVb3d17e0AsQh3n0oFMXr3q-nkjPw";
};

class LiveAuth
{
   public LiveAuth(Client client)
   {
       this.client = client;
   }

   private readonly  Client client;
   private static readonly string wlCallBackUri = "https://login.live.com/oauth20_desktop.srf";
   private static readonly string accessTokenAPI = "https://login.live.com/oauth20_authorize.srf?client_id={1}&scope={0}&response_type=code&redirect_uri={2}";
   private static Uri CreateClientAccessCodeUrl(IEnumerable<string> scopes, string cliend_id )
   {
       var url =  String.Format(accessTokenAPI, String.Join("%20", scopes), cliend_id, Uri.EscapeDataString(wlCallBackUri));
       return new Uri(url);
   }

   private static IEnumerable<string> Scopes = new [] {"wl.signin", "Office.onenote_create"};

   private static Uri RunWebBrowserTillReturnedToUrl(Uri uri, Func<string, bool> stopCondition )
   {
       var window = new Form()
       {
           Width=440,
           Height=600
       };

       Uri url=null;

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
public class CreateExamples
{
  private static readonly string PagesEndPoint = "https://www.onenote.com/api/v1.0/pages";

  private string DEFAULT_SECTION_NAME = "Quick Notes";

  private string AuthToken;
  public CreateExamples(string authToken)
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
  /// Does the object currently have a valid authenticated state
  /// </summary>
  public bool IsAuthenticated
  {
      // get { return _authClient.Session != null && !string.IsNullOrEmpty(_authClient.Session.AccessToken); }
      get { return true; }
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
  /// Create a page with an image of a URL on it.
  /// </summary>
  /// <param name="debug">Run the code under the debugger</param>
  async public Task<StandardResponse> CreatePageWithUrl(string sectionName, string url, string urlTitle)
  {
      var client = new HttpClient();

      // Note: API only supports JSON return type.
      client.DefaultRequestHeaders.Accept.Add(new MediaTypeWithQualityHeaderValue("application/json"));

      // This allows you to see what happens when an unauthenticated call is made.
      if (IsAuthenticated)
      {
          client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", this.AuthToken);
      }

      string date = GetDate();
      string simpleHtml = @"<html>" +
                          "<head>" +
                          "<title>"+urlTitle+"</title>" +
                          "<meta name=\"created\" content=\"" + date + "\" />" +
                          "</head>" +
                          "<body>" +
                          "<p>This is a page with an image of an html page rendered from a URL on it.</p>" +
                          "<img data-render-src=\""+url+"\" alt=\"An important web page\"/>" +
                          "</body>" +
                          "</html>";

      var createMessage = new HttpRequestMessage(HttpMethod.Post, GetPagesEndpoint(sectionName))
      {
          Content = new StringContent(simpleHtml, System.Text.Encoding.UTF8, "text/html")
      };

      HttpResponseMessage response = await client.SendAsync(createMessage);

      return await TranslateResponse(response);
  }

  /// <summary>
  /// Get date in ISO8601 format with local timezone offset
  /// </summary>
  /// <returns>Date as ISO8601 string</returns>
  private static string GetDate()
  {
      return DateTime.Now.ToString("o");
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


  /// <summary>
  /// Convert the http response message into a simple structure suitable for apps to process
  /// </summary>
  /// <param name="response">The response to convert</param>
  /// <returns>A simple rsponse</returns>
  private async static Task<StandardResponse> TranslateResponse(HttpResponseMessage response)
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
