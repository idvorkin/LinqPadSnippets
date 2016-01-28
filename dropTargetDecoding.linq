<Query Kind="Statements">
  <Reference>&lt;RuntimeDirectory&gt;\Accessibility.dll</Reference>
  <Reference>&lt;RuntimeDirectory&gt;\WPF\PresentationCore.dll</Reference>
  <Reference>&lt;RuntimeDirectory&gt;\WPF\PresentationFramework.dll</Reference>
  <Reference>&lt;RuntimeDirectory&gt;\WPF\PresentationUI.dll</Reference>
  <Reference>&lt;RuntimeDirectory&gt;\WPF\ReachFramework.dll</Reference>
  <Reference>&lt;RuntimeDirectory&gt;\System.Configuration.dll</Reference>
  <Reference>&lt;RuntimeDirectory&gt;\System.Deployment.dll</Reference>
  <Reference>&lt;RuntimeDirectory&gt;\WPF\System.Printing.dll</Reference>
  <Reference>&lt;RuntimeDirectory&gt;\System.Xaml.dll</Reference>
  <Reference>&lt;RuntimeDirectory&gt;\WPF\UIAutomationProvider.dll</Reference>
  <Reference>&lt;RuntimeDirectory&gt;\WPF\UIAutomationTypes.dll</Reference>
  <Reference>&lt;RuntimeDirectory&gt;\WPF\WindowsBase.dll</Reference>
  <NuGetReference>HtmlAgilityPack</NuGetReference>
  <Namespace>System.Windows</Namespace>
  <Namespace>System.Windows.Controls</Namespace>
  <Namespace>System.Windows.Threading</Namespace>
  <Namespace>HtmlAgilityPack</Namespace>
</Query>

/* 
Directions:
	Run the script, and then click on the DropTarget tab beside results.
	drag items onto the drop target.
	Click on results to see what was processed.
	Rinse+Repeat

*/


var button = new Button { FontSize = 50, Content = "Drop OnTo me", AllowDrop=true } ;


Func<string,IEnumerable<string>> HtmlToImages = (html) =>
{
	var htmlSnippet = new HtmlDocument();
	htmlSnippet.LoadHtml(html);
	var imageSrcAttribute = "src";
	var nodes = htmlSnippet.DocumentNode.SelectNodes("//img");
	if (nodes==null) return  new List<string>();
	var images = nodes.Where(x => (x.Attributes[imageSrcAttribute] != null))
	.Select(x => (x.Attributes[imageSrcAttribute].Value)).ToList();
	return images;
};


Action<IDataObject> dump = (o) =>
{
	var isHTML = o.GetDataPresent("text/html");
	if (isHTML)
	{
		var htmlStream = (MemoryStream)o.GetData("text/html");
		var html = new StreamReader(htmlStream).ReadToEnd();
		var images = HtmlToImages(html);
		if (images.Any())
		{
			images.Select(i => Util.Image(i)).Dump();
			return;
		}
	}
	var isHtmlEdge = o.GetDataPresent("HTML Format");
	if (isHtmlEdge)
	{
		var htmlS = (string)o.GetData("HTML Format");
		var realHTML = htmlS.Split(new[] { "<!DOCTYPE HTML>" }, StringSplitOptions.RemoveEmptyEntries)[1];
		var images = HtmlToImages(realHTML);
		if (images.Any())
		{
			images.Select(i => Util.Image(i)).Dump();
			return;
		}
	}

	var isUrl = o.GetDataPresent("UniformResourceLocator");
	if (isUrl)
	{
		// chrome+ie
		// can't drag from edge.
		// xxx: If URL is file, deal with slightly differently.
		o.GetData(typeof(string)).Dump("URL from string");
		//return;
	}
	var isFileDrop = o.GetDataPresent("FileDrop");
	if (isFileDrop)
	{
		// explorer file+directory
		// note this is a list of files.
		o.GetData("FileDrop").Dump("FileDrop");
		return;
	}
	var isOutlookEmail = o.GetDataPresent("RenPrivateMessages");
	if (isOutlookEmail)
	{
		o.GetData(typeof(string)).Dump("Email as string - continuing, use outlook automation to find active object");
		// Microsoft.Office.Interop.Outlook.MailItem = app.ActiveExplorer.Selection(1)
	}

	o.GetData(typeof(string)).Dump("As String");
	foreach (var f in o.GetFormats(true))
	{
		f.Dump("format name");
		try
		{
			o.GetData(f, true).Dump(f);
		}
		catch { }

	}
};

// https://msdn.microsoft.com/en-us/library/system.windows.idataobject(v=vs.110).aspx
button.Drop += (sender, dragevent) => dump(dragevent.Data);

PanelManager.StackWpfElement(button,"DropTarget");