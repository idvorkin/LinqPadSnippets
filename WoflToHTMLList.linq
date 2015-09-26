<Query Kind="Program" />

class TreeNode
{
	public string Line;
	public string Meta;
	public List<TreeNode> Children = new List<TreeNode>();
	public static TreeNode FromLineToken(LineToken line)
	{
		return new TreeNode(){
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

TreeNode BuildTree(string[] lines)
{
	int lineIndex = 0;
	var root = new TreeNode();
	BuildTreeRecurse(lines, ref lineIndex, 0,root);
	return root;
}
void BuildTreeRecurse(string[] lines, ref int  lineIndex, int depth, TreeNode parent)
{
	
	while (lineIndex < lines.Count())
	{
		var token = LineToken.FromString(lines[lineIndex]);
		var isTokenForMe  = depth == token.Depth;
		var isTokenForMyChild= token.Depth > depth;
		var isTokenForMyParent= token.Depth < depth;

		if (token.IsEmpty())
		{
			lineIndex++;  // proceed to next line
			continue;
		}
		if (isTokenForMe)
		{
			lineIndex++;  // proceed to next line
			parent.Children.Add(TreeNode.FromLineToken(token));
		}
		else if (isTokenForMyChild)
		{
			if (token.Depth != depth + 1)
			{
				token.Dump("Invalid Tree -> Double Indent not handled");		
			}
			var newParent = parent.Children.Count == 0 ? parent : parent.Children.Last();
			BuildTreeRecurse(lines, ref lineIndex, depth+1, newParent);
		}
		else if (isTokenForMyParent) 
		{
			// all children processed.
			break;
		}
	}
	return;
}

void TreeToHTML(TreeNode tree, ref string buffer)
{
	buffer += $"<li>{tree.Line}";
	if (tree.Children.Count == 0)
	{
		buffer+="</li>\n";
		return;
	}
	buffer +="<ul>\n";
	foreach (var child in tree.Children)
	{
		TreeToHTML(child, ref buffer);
	}
	buffer += "</ul>\n";
	buffer += "</li>\n";
}




void Main()
{
	var filename = @"c:\gits\igor2\WorkingSets\CompeteApps.wofl";
	var lines = File.ReadAllLines(filename);
	lines.Count().Dump();
	var root = BuildTree(lines);
	string s ="";
	TreeToHTML(root,ref s);
	s.Dump();
	
	//root.Dump();
}

// Define other methods and classes here