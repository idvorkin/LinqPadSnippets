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
        ItemType = [Microsoft.Office.Interop.Outlook.olItemType]
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
$queryFilter =  '[CreationTime]> "11/1/2014"'
$g_AllMails = New-Object System.Collections.ArrayList #Yuk Global
$version = 0.5
function enumerateFolder ($folder)
{
    $folderName = $folder.Name
    "Enumerating ($folderName) with filter: $queryFilter"

    $table = $folder.GetTable($queryFilter, $ol.ItemType::olMailItem) 

    $table.Columns.RemoveAll()
    $m = $table.Columns.Add("Subject")
    $m = $table.Columns.Add("CreationTime")
    $m = $table.Columns.Add("SenderName")

    $countColumns = 3
    $duration = Measure-Command{ 
        $flatTable = $table.GetArray($clipCount)
    }
    for ($row =0; $row -lt $flatTable.Count ;$row++)
    {
        $date = "" 
        $possibleDate =  $flatTable[$row,1];
        if ($possibleDate) {$date =(get-date ($possibleDate)).toShortDateString();}

        $a =@{ 
                    # TODO clean up this crappy code.
                    "Folder"=$folderName
                    "Subject"=$flatTable[$row,0];
                    "CreationTime"=$date
                    "SenderName"=$flatTable[$row,2] ;
            }
        $squelch_output = $g_AllMails.Add((New-Object PSObject -Property $a))
    }
}


enumerateFolder($ol.Folders.DeletedItems)
enumerateFolder($ol.Folders.Inbox)
enumerateFolder($ol.Folders.SentMail)
"Count Items [max=$clipCount]:$($g_AllMails.Count)"
$matcherRE =  '^(RE: )?(\w{3,})\:'
$conciseMail = $g_AllMails|  
    ? {$_.Subject -match $matcherRE} | 
    Select -Property  @{Name="IsReply";Expression={$_.Subject -match 'RE:'}},
        @{Name="Type";Expression={ $matches[2] }},
        @{Name="SenderName";Expression={ $_.SenderName }},
        @{Name="Folder";Expression={ $_.Folder }},
        @{Name="CreationTime";Expression={ $_.CreationTime }} |
        ? {! $typeBlackList.contains($_.Type)}

$tmp = [System.IO.Path]::GetTempFileName() + ".txt"
$conciseMail | Group-Object Type, IsReply | Select Count, Name | Sort Count -Descending | Select -First 20
$countEmailByDay = $g_AllMails | Select  CreationTime | Group-Object CreationTime

$data = @{ "version" = $version
           "conciseMails"= $conciseMail; 
           "countEmailByDay"=$countEmailByDay ;}  

$data  | Export-CliXml  -Path $tmp
$mail = $ol.Application.CreateItem($ol.ItemType::olMailItem)
$mail.Subject = "Typed-Mail-Stats from: $([Environment]::UserName) version:$version";
$mail.HTMLBody = "Thank you for supporting concise mail!";
$mail.To = "igord@microsoft.com"
$mail.Attachments.Add($tmp)
$mail.Save();
$mail.Display(0);
"Detail Messages For Analysis are in: $tmp."
"Please click send on the e-mail Analysis are in: $tmp."
