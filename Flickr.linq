<Query Kind="Statements">
  <NuGetReference>FlickrNet</NuGetReference>
  <Namespace>FlickrNet</Namespace>
  <Namespace>FlickrNet.Exceptions</Namespace>
</Query>

var searchWord = "kittens";
var options = new PhotoSearchOptions { 
  Text = searchWord, 
  Tags = "-kittens",
  PerPage = 500, 
  Page = 1   , 
  Extras = PhotoSearchExtras.License | PhotoSearchExtras.Description | PhotoSearchExtras.Tags
};
options.Licenses.Add(LicenseType.AttributionCC);
options.Licenses.Dump();
Flickr flickr = new Flickr(myAPIKey);


PhotoCollection photos = flickr.PhotosSearch(options);
// Each photos Tags and LargeUrl properties should now be set, 
// assuming that the photo has any tags, and is large enough to have a LargeUrl image available.
//photos.Select(p=>new { p.PhotoId, p.WebUrl, p.License} ).Dump();
photos.Where(x=>x.Title.Contains(searchWord)).Dump();

flickr.PhotosGetInfo("3170305511").Dump();

flickr.UrlsLookupUser("https://www.flickr.com/photos/62123641@N06/18260434458/").Dump();
