<Query Kind="Program">
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

	string advancedSearchTag="QUESTION";
	private void CreateSearchFolder(Application OutlookApp, string wordInSubject, string folderName)
	{
	    string scope = "Inbox";
	    string filter = "urn:schemas:mailheader:subject LIKE \'%"+ wordInSubject +"%\'";            
	    Search advancedSearch = null;
	    MAPIFolder folderInbox = null;
	    MAPIFolder folderSentMail = null;
	    NameSpace ns = null;
	    try
	    {
	        ns = OutlookApp.GetNamespace("MAPI");
	        folderInbox = ns.GetDefaultFolder(OlDefaultFolders.olFolderInbox);
	        folderSentMail = ns.GetDefaultFolder(OlDefaultFolders.olFolderSentMail);
	        scope = "\'" + folderInbox.FolderPath + 
	                                      "\',\'" + folderSentMail.FolderPath + "\'";
	        advancedSearch = OutlookApp.AdvancedSearch(scope, filter, true, advancedSearchTag);
			advancedSearch.Save(folderName);
	     	}
	          finally
	     {
	         if(advancedSearch!=null) Marshal.ReleaseComObject(advancedSearch);
	         if (folderSentMail != null) Marshal.ReleaseComObject(folderSentMail);
	         if (folderInbox != null) Marshal.ReleaseComObject(folderInbox);
	         if (ns != null) Marshal.ReleaseComObject(ns);
	    }                
	}
void Main()
{
	// http://www.add-in-express.com/creating-addins-blog/2008/03/28/build-outlook-add-in-in-net-to-manage-outlook-templates-signatures/
	
	var app = new Microsoft.Office.Interop.Outlook.Application();
	var mapi = app.GetNamespace("mapi");
	CreateSearchFolder(app,"QUESTION:","_QUESTIONS");
	CreateSearchFolder(app,"TASK:","_TASK");
	CreateSearchFolder(app,"INFORM:","_INFORM");
}

// Define other methods and classes here
