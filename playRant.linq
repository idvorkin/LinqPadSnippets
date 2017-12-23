<Query Kind="Statements">
  <NuGetReference Prerelease="true">Rant</NuGetReference>
  <Namespace>Rant</Namespace>
</Query>

// cd \gits
// git clone https://github.com/RantLang/Rantionary
// Doc: http://berkin.me/rant/docs/
var s= @"
	[case: sentence]<timeadv-past> we thought <noun-weapon.plural::=a> were important, but now we know <noun-weapon.plural::=a> are only <adj>.
";

//var wordsThatStartWithG="<noun ? /b/>";
var wordsThatStartWithG = "<noun>"; // Noun
wordsThatStartWithG = "[rep:2]<noun ? `g`>"; // Noun of type face.
//wordsThatStartWithG = "<name.subtype ? /(hi)/ >"; // Noun of type face.
var s2 = @"
  [case:sentence]
[rs:10;\n]
{
    [`[^aeiou\-\s]`:
        ;
    ]
    {(10){Big}|(5)little\s}
    [repnum]:{road|street}
}
";


var pgm = RantProgram.CompileString(@"[numfmt:verbal][rep:10][sep:,\s]{[rn]}");

var pathToDictionary = @"C:\Users\idvor\Downloads\Rantionary-3.0.20.rantpkg";
var rant= new Rant.RantEngine();
rant.LoadPackage(pathToDictionary);
var o = rant.Do(wordsThatStartWithG);
o.Dump();
o.First().Value.Dump();