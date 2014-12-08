<Query Kind="Statements">
  <Reference>&lt;ProgramFilesX86&gt;\Microsoft Visual Studio 12.0\Visual Studio Tools for Office\PIA\Office15\Microsoft.Office.Interop.Outlook.dll</Reference>
  <Reference>&lt;ProgramFilesX86&gt;\Microsoft Visual Studio 12.0\Visual Studio Tools for Office\PIA\Office15\Microsoft.Office.Interop.Word.dll</Reference>
  <Namespace>Microsoft.Office</Namespace>
  <Namespace>Microsoft.Office.Interop</Namespace>
  <Namespace>Microsoft.Office.Interop.Outlook</Namespace>
  <Namespace>System</Namespace>
  <Namespace>System.Collections.Generic</Namespace>
  <Namespace>System.Configuration</Namespace>
  <Namespace>System.Linq</Namespace>
  <Namespace>System.Runtime.InteropServices</Namespace>
  <Namespace>System.Text</Namespace>
  <Namespace>System.Threading.Tasks</Namespace>
</Query>

//crib sheet -- http://msdn.microsoft.com/en-us/library/ms268994.aspx
// http://www.add-in-express.com/creating-addins-blog/2008/03/28/build-outlook-add-in-in-net-to-manage-outlook-templates-signatures/

"Part 1: View the selected email".Dump();
var app = new Microsoft.Office.Interop.Outlook.Application();
var mapi = app.GetNamespace("mapi");
var explorer = app.ActiveExplorer();
var currentFolder = (MAPIFolder)(explorer.CurrentFolder);
currentFolder.Name.Dump("Folder Name");
if (explorer.Selection.Count != 1)
{
	explorer.Selection.Count.Dump("Only works if 1 item selected counted Selected = ");
	return;
}
var selected = explorer.Selection[1]; // I don't know why it's 1 indexed
selected.Dump();
var selectedMail = selected as MailItem;
selectedMail.Subject.Dump("Selected Mail Subject");

var inlineResponse = explorer.ActiveInlineResponse as MailItem;
inlineResponse.Subject.Dump("Inline Response Subject");
inlineResponse.Subject = "SnowFlakes";
var editor = explorer.ActiveInlineResponseWordEditor;


// inspectors only exist with popped out mails. 

/*
var inspector = app.ActiveInspector();
explorer.ActiveInlineResponse

inspector.EditorType.Dump("Editor Type");
var wordEditor = inspector.WordEditor;
wordEditor.Dump("Word Editor");

var inspectedMail = inspector.CurrentItem as MailItem;
inspectedMail.Subject.Dump();
inspectedMail.Body.Dump();
*/
//inspector.CurrentItem.Dump();
//inspector.Dump("Current Inspsector");
//app.Inspectors.Dump("Inspectors");