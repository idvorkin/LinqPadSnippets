<Query Kind="Statements">
  <NuGetReference>Html2Markdown</NuGetReference>
  <Namespace>HtmlAgilityPack</Namespace>
</Query>

/*
Convert from OneNote HTML, to Markdown2HTML HTML.

OneNote HTML Spec: https://msdn.microsoft.com/en-us/library/office/dn832628.aspx
Markdown2Html: https://github.com/baynezy/Html2Markdown/issues/60

This code makes 2 assumptions - need to verify if OneNote is honoring these assumptions.

1) Font Decoratoin will be encoded only on span
    e.g. *not* <td style='....'>

2) Font Decortations will not be combined 
	e.g. *not* <span style="font-weight:bold; font-text:italic">
*/



var styleToElementName = new Dictionary<string, string>()
{
	{"font-weight:bold","b"},
	{"font-style:italics","i"},
//	{"text-decoration:line-through","strike"},
//	{"text-decoration:underline","strike"},	
};

var onenoteHTML = @"<td style=''><span style='font-weight:bold'>Expected Bold </span></td>";


var doc = new HtmlAgilityPack.HtmlDocument();
doc.LoadHtml(onenoteHTML);

foreach (var s2e in styleToElementName)
{
	var styledElements = doc.DocumentNode.SelectNodes($"//span[@style='{s2e.Key}']");
	foreach (var element in styledElements)
	{
		element.Name = s2e.Value;
		element.Attributes.Where(a => a.Name == "style" && a.Value == s2e.Key).ToList().ForEach(a => element.Attributes.Remove(a));
	}
}

onenoteHTML.Dump("Original");
doc.DocumentNode.OuterHtml.Dump("Post");
