<Query Kind="Program">
  <NuGetReference>ServiceStack.Text</NuGetReference>
  <Namespace>ServiceStack.Text</Namespace>
</Query>

public class Temp
{
	public string s1 { get; set;}
	public string s2 { get; set;}
	public DateTime s3 { get; set;}
}
public class Temp2
{
	public string s2 { get; set;}
}
void Main()
{
	var explicitTyped = new[] { new Temp() { s1 = "Not Default" }, new Temp() { s2 = "NotNull", s3= DateTime.Now}};
	var anonymousTyped = new[] { new { s1 = "hi", s2 = "bye" }};
	//var ts=anonymousTyped;
	var ts= explicitTyped;
	
	var serializedAsJSV = CsvSerializer.SerializeToString(ts);
	serializedAsJSV.Dump("Serialized as Temp");
		
	CsvSerializer.DeserializeFromString<IEnumerable<Temp>>(serializedAsJSV).Dump("Temp");
	CsvSerializer.DeserializeFromString<IEnumerable<Temp2>>(serializedAsJSV).Dump("Temp2");
}


// Define other methods and classes here
