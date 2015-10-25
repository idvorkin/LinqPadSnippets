<Query Kind="Statements">
  <Reference>&lt;RuntimeDirectory&gt;\Accessibility.dll</Reference>
  <Reference>&lt;RuntimeDirectory&gt;\System.Configuration.dll</Reference>
  <Reference>&lt;RuntimeDirectory&gt;\System.Deployment.dll</Reference>
  <Reference>&lt;RuntimeDirectory&gt;\System.Runtime.Serialization.Formatters.Soap.dll</Reference>
  <Reference>&lt;RuntimeDirectory&gt;\System.Security.dll</Reference>
  <NuGetReference>TestStack.White</NuGetReference>
  <NuGetReference>TestStack.White.ScreenObjects</NuGetReference>
  <Namespace>System.Windows.Forms</Namespace>
  <Namespace>TestStack.White</Namespace>
  <Namespace>TestStack.White.Factory</Namespace>
  <Namespace>TestStack.White.ScreenObjects</Namespace>
  <Namespace>TestStack.White.ScreenObjects.Services</Namespace>
  <Namespace>TestStack.White.ScreenObjects.Sessions</Namespace>
  <Namespace>TestStack.White.InputDevices</Namespace>
</Query>

var cmdDotExeTitle = @"C:\Windows\System32\cmd.exe";
var workConfig = new WorkConfiguration()
{
	ArchiveLocation=@"c:\temp\WhiteArchive", 
	Name="Unknown"
};

var workSession = new WorkSession(workConfig, new NullWorkEnvironment());
var application = TestStack.White.Application.Launch("cmd.exe");
var screens = workSession.Attach(application);

screens.Dump("Screens in cmd.exe");
var s = screens.Get<AppScreen>(cmdDotExeTitle,InitializeOption.NoCache);
s.Dump("Cmd.exe screen info");
var tempFile = Path.GetTempFileName();
var stringToEchoIntoFile="Hello World";

var keysToPress = $"echo {stringToEchoIntoFile} >> {tempFile}\n\r";
keysToPress.Dump("Keys sent to cmd");
Keyboard.Instance.Enter(keysToPress);
Thread.Sleep(TimeSpan.FromSeconds(0.2));
var textInTempFile = File.ReadAllText(tempFile);
textInTempFile.Dump($"Text in {tempFile}");

application.Dispose(); // uncomment to leave launched applications open.