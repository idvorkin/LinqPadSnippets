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
$folderItems = $ol.Folders.DeletedItems.Items

"Enumerating Folder, it will take minutes to enumerate upto $clipCount emails... "
$Duration = Measure-Command {$folderItems = $ol.Folders.Inbox.Items | Select -First $clipCount}
"It took  $($duration.TotalMinutes) Minutes" 
"Count Items [max=$clipCount]:$(($folderItems |Measure).Count)"

$matcherRE =  '^(RE: )?(\w{3,})\:'
$conciseMail = $folderItems|  
    ? {$_.Subject -match $matcherRE} | 
    Select -Property  @{Name="IsReply";Expression={$_.Subject -match 'RE:'}},
        @{Name="Type";Expression={ $matches[2] }},
        #Subject,  #Debug only no privacy.
        SenderName,  ReceivedTime | 
        ? {! $typeBlackList.contains($_.Type)}



"Count Concise Mails: $(@($conciseMail).Count)"
$conciseMail









