<Query Kind="Statements">
  <NuGetReference>Newtonsoft.Json</NuGetReference>
  <NuGetReference>RestSharp</NuGetReference>
  <Namespace>Newtonsoft.Json</Namespace>
  <Namespace>RestSharp</Namespace>
  <Namespace>System.Diagnostics</Namespace>
  <Namespace>Newtonsoft.Json.Linq</Namespace>
</Query>

// Trigger by using the "Maker IFTTT Channel" -- https://ifttt.com/maker

// +++ Secret setup
var secrets = JObject.Parse(File.ReadAllText(@"c:/gits/igor2/secretBox.json"));
var key = secrets["IFTTTMakerKey"];
if (key == null) throw new InvalidDataException("Missing Key");
// --- Secret setup

var value1 = "Deliberate;Disciplined;Daily";
var eventName = "sms";
var client = new RestClient($"https://maker.ifttt.com/trigger/{eventName}/with/key/{key}?value1={value1}");

client.Execute(new RestRequest()).Content.Dump();