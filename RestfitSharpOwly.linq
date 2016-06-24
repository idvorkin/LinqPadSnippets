<Query Kind="Program">
  <Reference>&lt;RuntimeDirectory&gt;\System.Configuration.dll</Reference>
  <Reference>&lt;RuntimeDirectory&gt;\System.Data.Services.Client.dll</Reference>
  <Reference>&lt;RuntimeDirectory&gt;\System.Data.Services.Design.dll</Reference>
  <Reference>&lt;RuntimeDirectory&gt;\System.Design.dll</Reference>
  <Reference>&lt;RuntimeDirectory&gt;\System.Net.Http.dll</Reference>
  <Reference>&lt;RuntimeDirectory&gt;\System.Runtime.Serialization.dll</Reference>
  <Reference>&lt;RuntimeDirectory&gt;\System.ServiceModel.Activation.dll</Reference>
  <Reference>&lt;RuntimeDirectory&gt;\System.ServiceModel.dll</Reference>
  <Reference>&lt;RuntimeDirectory&gt;\System.Web.ApplicationServices.dll</Reference>
  <Reference>&lt;RuntimeDirectory&gt;\System.Web.dll</Reference>
  <Reference>&lt;RuntimeDirectory&gt;\System.Web.Extensions.dll</Reference>
  <Reference>&lt;RuntimeDirectory&gt;\System.Web.Services.dll</Reference>
  <Reference>&lt;RuntimeDirectory&gt;\System.Windows.Forms.dll</Reference>
  <NuGetReference>Castle.Core</NuGetReference>
  <NuGetReference>Newtonsoft.Json</NuGetReference>
  <NuGetReference>refit</NuGetReference>
  <Namespace>Castle.DynamicProxy</Namespace>
  <Namespace>Newtonsoft.Json.Linq</Namespace>
  <Namespace>Refit</Namespace>
  <Namespace>System.Net.Http</Namespace>
  <Namespace>System.Threading.Tasks</Namespace>
</Query>

// Resfit doesn't work right in linqpad, need to use this proxy polyfill
// https://gist.github.com/bennor/c73870e810f8245b2b1d

public class ProxyRestService
{
	static readonly ProxyGenerator Generator = new ProxyGenerator();

	public static T For<T>(HttpClient client)
		where T : class
	{
		if (!typeof(T).IsInterface)
		{
			throw new InvalidOperationException("T must be an interface.");
		}

		var interceptor = new RestMethodInterceptor<T>(client);
		return Generator.CreateInterfaceProxyWithoutTarget<T>(interceptor);
	}

	public static T For<T>(string hostUrl)
		where T : class
	{
		var client = new HttpClient() { BaseAddress = new Uri(hostUrl) };
		return For<T>(client);
	}

	class RestMethodInterceptor<T> : IInterceptor
	{
		static readonly Dictionary<string, Func<HttpClient, object[], object>> methodImpls
			= RequestBuilder.ForType<T>().InterfaceHttpMethods
				.ToDictionary(k => k, v => RequestBuilder.ForType<T>().BuildRestResultFuncForMethod(v));

		readonly HttpClient client;

		public RestMethodInterceptor(HttpClient client)
		{
			this.client = client;
		}

		public void Intercept(IInvocation invocation)
		{
			if (!methodImpls.ContainsKey(invocation.Method.Name))
			{
				throw new NotImplementedException();
			}
			invocation.ReturnValue = methodImpls[invocation.Method.Name](client, invocation.Arguments);
		}
	}
}



public interface IOwlyClient
{
	[Get("/api/1.1/url/shorten")]
	Task<ShortenResults> Shorten(string longUrl, string apiKey);
}

public class ShortenResults
{
	public class Result
	{
		public string hash { get; set;}
		public string longUrl { get; set;}
		public string shortUrl { get; set;}
	}
	public Result results { get; set;}
}

void Main()
{
	// Ow.ly help:http://ow.ly/api-docs
	
	// +++ Secret setup
	var secrets = JObject.Parse(File.ReadAllText(@"c:/gits/igor2/secretBox.json"));
	var key = secrets["OwlyApiKey"];
	if (key == null) throw new InvalidDataException("Missing Key");
	// --- Secret setup
	
	var owlyAPI = ProxyRestService.For<IOwlyClient>("http://ow.ly");
	var r= owlyAPI.Shorten("https://ig2600.blogspot.com",key.ToString()).Result;
	r.Dump();	
}

// Define other methods and classes here
