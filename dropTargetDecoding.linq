<Query Kind="Statements">
  <Reference>&lt;RuntimeDirectory&gt;\WPF\PresentationFramework.dll</Reference>
  <Reference>&lt;RuntimeDirectory&gt;\System.Xaml.dll</Reference>
  <Reference>&lt;RuntimeDirectory&gt;\WPF\WindowsBase.dll</Reference>
  <Reference>&lt;RuntimeDirectory&gt;\WPF\PresentationCore.dll</Reference>
  <Reference>&lt;RuntimeDirectory&gt;\System.Configuration.dll</Reference>
  <Reference>&lt;RuntimeDirectory&gt;\WPF\UIAutomationProvider.dll</Reference>
  <Reference>&lt;RuntimeDirectory&gt;\WPF\UIAutomationTypes.dll</Reference>
  <Reference>&lt;RuntimeDirectory&gt;\WPF\ReachFramework.dll</Reference>
  <Reference>&lt;RuntimeDirectory&gt;\WPF\PresentationUI.dll</Reference>
  <Reference>&lt;RuntimeDirectory&gt;\WPF\System.Printing.dll</Reference>
  <Reference>&lt;RuntimeDirectory&gt;\Accessibility.dll</Reference>
  <Reference>&lt;RuntimeDirectory&gt;\System.Deployment.dll</Reference>
  <Namespace>System.Windows</Namespace>
  <Namespace>System.Windows.Controls</Namespace>
  <Namespace>System.Windows.Threading</Namespace>
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
	var isUrl = o.GetDataPresent("UniformResourceLocator");
	if (isUrl) {
		// chrome+ie
		// can't drag from edge.
		// xxx: If URL is file, deal with slightly differently.
		o.GetData(typeof(string)).Dump("URL from string");
		return;
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
		f.Dump();
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