<Query Kind="Statements">
  <NuGetReference Prerelease="true">Rant</NuGetReference>
  <Namespace>Rant</Namespace>
</Query>

// cd \gits
// git clone https://github.com/RantLang/Rantionary
// Doc: https://github.com/RantLang/RantDocs/tree/master/content
var s= @"
	[case: sentence]<timeadv-past> we thought <noun-weapon.plural::=a> were important, but now we know <noun-weapon.plural::=a> are only <adj>.

";
var n1 = new Rant.RantEngine("c:/gits/Rantionary");
var o = n1.Do(s);
o.First().Value.Dump();