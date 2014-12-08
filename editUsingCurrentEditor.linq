<Query Kind="Statements">
  <Reference>&lt;ProgramFilesX86&gt;\Microsoft Visual Studio 12.0\Visual Studio Tools for Office\PIA\Office15\Microsoft.Office.Interop.Outlook.dll</Reference>
  <Reference>&lt;ProgramFilesX86&gt;\Microsoft Visual Studio 12.0\Visual Studio Tools for Office\PIA\Office15\Microsoft.Office.Interop.Word.dll</Reference>
  <Namespace>Microsoft.Office</Namespace>
  <Namespace>Microsoft.Office.Interop</Namespace>
  <Namespace>Microsoft.Office.Interop.Outlook</Namespace>
  <Namespace>Microsoft.Office.Interop.Word</Namespace>
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


Document replyEditor = null;
if (app.ActiveExplorer().ActiveInlineResponse !=null)
{
	replyEditor = app.ActiveExplorer().ActiveInlineResponseWordEditor as Document;
}
else
{
	var inspect = app.ActiveInspector();
	replyEditor  = inspect.WordEditor as Document;
}




var conciseMailLink = replyEditor.Range(0,0);
conciseMailLink.Text = "Concise Mail";
footer.Font.Italic=1;
conciseMailLink.Hyperlinks.Add(conciseMailLink,"http://www.google.com");

var footer= replyEditor.Range(0,0);
footer.Text = "\n\nEffectively Communicated with ";
footer.Font.Italic=1;


var replyBody = replyEditor.Range(0,0);
replyBody.Text = "LIKE";
replyBody.Font.Italic=0;


//mailDoc.Bookmarks.Dump();
//mailDoc.Paragraphs.Cast<Paragraph>().Select(p=>p.
///var newP = we.Content.Paragraphs.Add(null);