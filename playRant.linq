<Query Kind="Statements">
  <NuGetReference Prerelease="true">Rant</NuGetReference>
  <Namespace>Rant</Namespace>
</Query>

// cd \gits
// git clone https://github.com/RantLang/Rantionary

var n1 = new Rant.RantEngine("c:/gits/Rantionary");
var o = n1.Do("Hello <noun>");
o.First().Value.Dump();