Set-StrictMode -Version 2.0
$ErrorActionPreference="Stop"

# More info @ https://github.com/idvorkin/psOutlook

function global:Get-Outlook
{
    Add-type -assembly "Microsoft.Office.Interop.Outlook" 
    $olApp = New-Object -comObject Outlook.Application     $mapi = $olApp.GetNameSpace("MAPI")

    $ol = [PSCustomObject] @{
        MAPI = $mapi
        Application = $olApp
        Folders = @{}
    }

    # Add the Folders
    $olFolders = "Microsoft.Office.Interop.Outlook.OlDefaultFolders" -as [type]

    $realFolderCount = 10 # manually set by looking at OlDefaultFolders struct.
    [enum]::GetValues($olFolders) | Select -First 10 | %  {
        # extract string from folderName e.g olFolderInbox
        $folderName = (([string]$_) -Split "olFolder")[1]
        $folderValue = ([int]$_)
        $ol.Folders[$folderName] = $mapi.GetDefaultFolder($folderValue)
    }

    # Useful member if you use delayed send.
    $ol | Add-Member -MemberType ScriptMethod -Name SendAllInOutbox -Value {
        $this.Folders.Outbox.Items | % {
            # Move Deferred Time To Past
            $_.DeferredDeliveryTime = [DateTime]::Now- [TimeSpan]::FromMinutes(10)
            $_.Send()
        }
    } 

    return $ol
}

$ol = Get-Outlook

#paramaters
$clipCount =10000
$typeBlackList = "Accepted,Fwd,Canceled,Declined".Split(',')
$queryFilter =  '[Received]> "11/1/2014"'
$folderItems = New-Object System.Collections.ArrayList #Yuk Global
function enumerateFolder ($folder)
{
    $folderName = $folder.Name
    "Enumerating ($folderName) with filter: $queryFilter"

    $table = $folder.GetTable($queryFilter, [Microsoft.Office.Interop.Outlook.olItemType]::olMailItem) 

    $table.Columns.RemoveAll()
    $m = $table.Columns.Add("Subject")
    $m = $table.Columns.Add("ReceivedTime")
    $m = $table.Columns.Add("SenderName")

    $countColumns = 3
    $duration = Measure-Command{ 
        $flatTable = $table.GetArray($clipCount)
    }
    for ($row =0; $row -lt $flatTable.Count ;$row++)
    {
        $a =@{ 
                    # TODO clean up this crappy code.
                    "Folder"=$folderName
                    "Subject"=$flatTable[$row,0];
                    "ReceivedTime"=$flatTable[$row,1];
                    "SenderName"=$flatTable[$row,2] ;
            }
        $_ = $folderItems.Add($a)
    }
}


enumerateFolder($ol.Folders.DeletedItems)
enumerateFolder($ol.Folders.Inbox)
enumerateFolder($ol.Folders.SentMail)
"Enumerating Folder, it will take minutes to enumerate upto $clipCount emails... "
$Duration = Measure-Command {$folderItems = $ol.Folders.Inbox.Items | Select -First $clipCount}
"It took  $($duration.TotalMinutes) Minutes" 
"Count Items [max=$clipCount]:$($folderItems.Count)"

$matcherRE =  '^(RE: )?(\w{3,})\:'
$conciseMail = $folderItems|  
    ? {$_.Subject -match $matcherRE} | 
    Select -Property  @{Name="IsReply";Expression={$_.Subject -match 'RE:'}},
        @{Name="Type";Expression={ $matches[2] }},
        @{Name="SenderName";Expression={ $_.SenderName }},
        @{Name="Folder";Expression={ $_.Folder }},
        @{Name="ReceivedTime";Expression={ $_.ReceivedTime }} |
        ? {! $typeBlackList.contains($_.Type)}
$conciseMail | Group-Object Type, IsReply | Select Count, Name | Sort Count -Descending | Select -First 20
$tmp = [System.IO.Path]::GetTempFileName() 
$conciseMail  | Export-CSV  $tmp
"Detail Messages For Analysis are in: $tmp"
