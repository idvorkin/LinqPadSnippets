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
wordsThatStartWithG = "[rep:2]<noun-head>"; // Noun of type face.
//wordsThatStartWithG = "<name.subtype ? /(hi)/ >"; // Noun of type face.
var s2 = @"
  [case:sentence]
[rs:2;\n]
{
    [`[^aeiou\-\s]`:
        {{(10)|{[numfmt:verbal;[n:1;10]]|<verb.pp-transitive>}\s}<noun..pl-place|animal|person|tool?!`\s`>|<adj-appearance?!`\s`>|<surname?!`\s`>}
        ;
        {(10)[match]|[capsinfer:[match]]{b|t|c|n|m|l|k|g|w|cc|ll|dd|gg|(.1)x}[case:word]}
    ]
    {(5)|\s{creek|lake|river|rock}|{wood|way}}\s
    {road|street}
}
";


var pgm = RantProgram.CompileString(@"[numfmt:verbal][rep:10][sep:,\s]{[rn]}");

var pathToDictionary = @"C:\Users\idvor\Downloads\Rantionary-3.0.20.rantpkg";
var rant= new Rant.RantEngine();
rant.LoadPackage(pathToDictionary);
var o = rant.Do(s2);
o.Dump();
o.First().Value.Dump();