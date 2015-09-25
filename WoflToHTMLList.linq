<Query Kind="Program" />

class Level
{
	public string Line;
	public string Meta;
	public List<Level> Children = new List<Level>();
	public static Level FromLineToken(LineToken line)
	{
		return new Level(){
			Line = line.Line,
			Meta = line.Meta
		};
	}
}

class LineToken
{
	public string Line;
	public string Meta;
	public int Depth;
	public bool IsEmpty() => Line.Trim().Length == 0;
	public static LineToken FromString(string line)
	{
		var ret = new LineToken();
		var lineAsCharArray = line.ToCharArray();
		// 2 spaces = indent.
		var depth = lineAsCharArray.TakeWhile(Char.IsWhiteSpace).Count() /2 ; 
		ret.Depth = depth;
		
		var remainingLine = new String(lineAsCharArray.SkipWhile(Char.IsWhiteSpace).ToArray());
		// Strip out meta charectors, and the space after them.
		ret.Line = remainingLine.TrimStart(" *+".ToCharArray()).ToString();
		
		// TBD capture meta.
		return ret;		
	}
}
void Main()
{
	var filename = @"c:\gits\igor2\WorkingSets\CompeteApps.wofl";
	var lines = File.ReadAllLines(filename);
	lines.Count().Dump();
	var root = new Level();
	var current = root;
	foreach (var line in lines.Select(LineToken.FromString))
	{
		// hack at root.
		if (line.IsEmpty()) continue;
		if (line.Depth != 0 ) continue;
		current.Children.Add(Level.FromLineToken(line));
	}	
	
	root.Dump();
}

// Define other methods and classes here
