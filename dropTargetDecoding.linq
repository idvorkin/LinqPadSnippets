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
  <NuGetReference>AngleSharp</NuGetReference>
  <NuGetReference>HtmlAgilityPack</NuGetReference>
  <Namespace>HtmlAgilityPack</Namespace>
  <Namespace>System.Windows</Namespace>
  <Namespace>System.Windows.Controls</Namespace>
  <Namespace>System.Windows.Threading</Namespace>
  <Namespace>AngleSharp.Parser.Html</Namespace>
</Query>

/* 
Directions:
	Run the script, and then click on the DropTarget tab beside results.
	drag items onto the drop target.
	Click on results to see what was processed.
	Rinse+Repeat

*/


var button = new Button { FontSize = 50, Content = "Drop OnTo me", AllowDrop=true } ;

Action<IDataObject> dump = (o) =>
{
	var isHtmlEdge = o.GetDataPresent("HTML Format");
	isHtmlEdge.Dump("HTML");
	if (isHtmlEdge)
	{
		var htmlFormat = (string)o.GetData("HTML Format");
		var startFragmentOffsetS = htmlFormat.Split('\n').SingleOrDefault(l => l.Contains("StartFragment:")).Split(':')[1].Dump();
		var endFragmentOffsetS = htmlFormat.Split('\n').SingleOrDefault(l => l.Contains("EndFragment:")).Split(':')[1].Dump();
		var startFragmentOffset = Int32.Parse(startFragmentOffsetS);
		var endFragmentOffset = Int32.Parse(endFragmentOffsetS);
		var fragment = new String((htmlFormat.ToCharArray().Skip(startFragmentOffset).Take(endFragmentOffset - startFragmentOffset + 1).ToArray()));
		var parser = new HtmlParser();
		var document = parser.Parse(fragment);
		var images = document.QuerySelectorAll("img");
		images.Select(x => Util.Image(x.Attributes["src"].Value)).Dump();
		if (images.Any())
		{
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
		catch (Exception e)
		{
			
			e.Dump($"Threw getting format for: {f}");
		}

	}
};

// https://msdn.microsoft.com/en-us/library/system.windows.idataobject(v=vs.110).aspx
button.Drop += (sender, dragevent) => dump(dragevent.Data);

PanelManager.StackWpfElement(button,"DropTarget");