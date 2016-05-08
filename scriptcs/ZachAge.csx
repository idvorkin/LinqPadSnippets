var birthdate = new DateTime(2010,4,22);
var age = DateTime.Now - birthdate;
var weeks = age.TotalDays/7;

Console.WriteLine($"Zach Age in Weeks:{weeks}");
