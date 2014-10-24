<Query Kind="Program">
  <Reference>&lt;RuntimeDirectory&gt;\System.DirectoryServices.AccountManagement.dll</Reference>
  <Reference>&lt;RuntimeDirectory&gt;\System.DirectoryServices.Protocols.dll</Reference>
  <Reference>&lt;RuntimeDirectory&gt;\System.DirectoryServices.dll</Reference>
  <Reference>&lt;RuntimeDirectory&gt;\System.Configuration.dll</Reference>
  <Namespace>System.DirectoryServices.AccountManagement</Namespace>
  <Namespace>System.DirectoryServices</Namespace>
</Query>

	static class Extensions{
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
	       DirectoryEntry directoryEntry = principal.GetUnderlyingObject() as DirectoryEntry;
		   var properties = directoryEntry.Properties;      
		   var ret = new Dictionary<string,Object>();
		   foreach(var p in properties.PropertyNames)
		   {
		   	ret.Add(p.ToString(),properties[p.ToString()]);
		   }
		   return ret;
	   }
	public static IEnumerable<string>  DirectReports(this Principal principal)
	{
		var directReports = (Object[])((PropertyValueCollection) (principal.Properties()["directReports"])).Value;
		return directReports.Cast<string>(); 
	}
	public static string  StringProperty(this Principal principal, string property)
	{
		return (string)((PropertyValueCollection) (principal.Properties()[property])).Value;
	}
	
	
	}
void Main()
{
	var user = UserPrincipal.FindByIdentity(new PrincipalContext(ContextType.Domain,"REDMOND"),
	"Li-Fen Wu");
	user.StringProperty("manager").Dump("Manager");
	user.DirectReports().Dump("Reports");
	user.StringProperty("title").Dump("title");
}

// Define other methods and classes here