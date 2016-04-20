<Query Kind="Program">
  <Reference>&lt;RuntimeDirectory&gt;\System.DirectoryServices.AccountManagement.dll</Reference>
  <Reference>&lt;RuntimeDirectory&gt;\System.DirectoryServices.Protocols.dll</Reference>
  <Reference>&lt;RuntimeDirectory&gt;\System.DirectoryServices.dll</Reference>
  <Reference>&lt;RuntimeDirectory&gt;\System.Configuration.dll</Reference>
  <Namespace>System.DirectoryServices.AccountManagement</Namespace>
  <Namespace>System.DirectoryServices</Namespace>
  <Namespace>System.Drawing</Namespace>
</Query>

static class Extensions{
	public static Dictionary<Principal, Dictionary<string,Object>> PropertyCache = new Dictionary<Principal, Dictionary<string,Object>>();
	public static String GetProperty(this Principal principal, String property)
	   {
	       DirectoryEntry directoryEntry = principal.GetUnderlyingObject() as DirectoryEntry;
	       if (directoryEntry.Properties.Contains(property))
	           return directoryEntry.Properties[property].Value.ToString();
	       else
	           return String.Empty;
	   }
	   public static Dictionary<string,Object>  Properties(this Principal principal)
	   {
	   		
	   		var ret = new Dictionary<string,Object>();
			if (principal == null) return ret;
			if (Extensions.PropertyCache.ContainsKey(principal)) { return Extensions.PropertyCache[principal];};
			DirectoryEntry directoryEntry = principal.GetUnderlyingObject() as DirectoryEntry;
			var properties = directoryEntry.Properties;      
			foreach(var p in properties.PropertyNames)
			{
				ret.Add(p.ToString(),properties[p.ToString()]);
			}
			Extensions.PropertyCache[principal] = ret;
			return ret;
	   }
	public static IEnumerable<string>  DirectReports(this Principal principal)
	{
		if (!principal.Properties().ContainsKey("directReports")){
			return new List<string>();
		}
		var directProperty = ((PropertyValueCollection) (principal.Properties()["directReports"])).Value;
		var singleReport = directProperty as string; 
		if (singleReport != null) {return new List<string>() {singleReport};};
		var directReports = directProperty as object[];
		return directReports.Cast<string>(); 
	}
	public static string  StringProperty(this Principal principal, string property)
	{
		return (string)((PropertyValueCollection) (principal.Properties()[property])).Value;
	}
	public static Byte[] ByteProperty(this Principal principal, string property)
	{
		return (Byte[])((PropertyValueCollection)(principal.Properties()[property])).Value;
	}
}
	class MSEmployee
{
	public MSEmployee(string name)
	{
		var domainsToTry = new List<string> {"redmond","northamerica","europe","ntdev"};
		foreach (var domain in domainsToTry)
		{
			me = UserPrincipal.FindByIdentity
				(new PrincipalContext(ContextType.Domain,domain),
				name);
			if (me != null) break;
		}

		if (me == null) 
		{
			name.Dump();
		}
	}
	Principal me;
	public bool IsValid
	{
		get {
			return me.Properties().ContainsKey("title");
		}
	}
	public string Name {
		get {return me.StringProperty("name");}
	}
	public string Title
	{	
		get {return  me.StringProperty("title");}
	}
	public Bitmap BitMap
	{

		get
		{
			var bytes = me.ByteProperty("thumbnailPhoto");
			return new Bitmap(new MemoryStream(bytes));
		}

	}
	public int Level
	{
		get
		{
			var lowerTitle = Title.ToLower();
			if (lowerTitle.Contains("ii")) return 2;
				if (lowerTitle.Contains("2")) return 2;
				if (lowerTitle.Contains("senior")) return 3;
				if (lowerTitle.Contains("principal")) return 4;
				if (lowerTitle.Contains("partner")) return 5;
				if (lowerTitle.Contains("director")) return 6;
				if (lowerTitle.Contains("general")) return 6;
				if (lowerTitle.Contains("vp")) return 7;
				if (lowerTitle.Contains("fellow")) return 8;
				if (lowerTitle.Contains("cheif")) return 9;
				return 0;
			}
	}
	public IEnumerable<MSEmployee> DirectReports{
	get 	{
				return me.DirectReports().Select(d=>new MSEmployee(d)).Where(mse=>mse.IsValid).OrderByDescending(mse=>mse.Level);
	}
	}
}
void Main()
{
	var employee = new MSEmployee("igord");
	employee.Dump();
}

// Define other methods and classes here