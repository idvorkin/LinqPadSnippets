<Query Kind="Program">
  <Reference Relative="..\oc\OneClip.Common\obj\Debug\Interop.Shell32.dll">C:\gits\oc\OneClip.Common\obj\Debug\Interop.Shell32.dll</Reference>
</Query>

void Main()
{
	var path = Environment.GetFolderPath(Environment.SpecialFolder.Recent);
	foreach (var p in Directory.GetFiles(path))
	{
		var isDirectory = Directory.Exists(p);
		if (isDirectory)
		{
			// skip? continue
			continue;
		}
		if (Path.GetExtension(p) == ".lnk")
		{
			var target = GetLnkTarget(p);
			if (File.Exists(target))
			{
				target.Dump();
			}
		}
		else
		{
			p.Dump();
		}
	}
}



private object GetShell()
{
	var shellType = Type.GetTypeFromProgID("Shell.Application");

	return Activator.CreateInstance(shellType);
}

public static string GetLnkTarget(string lnkPath)
{
	var shl = new Shell32.Shell();         // Move this to class scope
	lnkPath = System.IO.Path.GetFullPath(lnkPath);
	var dir = shl.NameSpace(System.IO.Path.GetDirectoryName(lnkPath));
	var itm = dir.Items().Item(System.IO.Path.GetFileName(lnkPath));
	var lnk = (Shell32.ShellLinkObject)itm.GetLink;
	return lnk.Target.Path;
}