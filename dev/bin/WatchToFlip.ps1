### SET FOLDER TO WATCH + FILES TO WATCH + SUBFOLDERS YES/NO
$watcher = New-Object System.IO.FileSystemWatcher
$watcher.Path = "C:\Users\14124\Dropbox (RUNLAB)\Gait videos\2022\11 November\1_T4_Videos"
$watcher.Filter = "*.*"
$watcher.IncludeSubdirectories = $true
$watcher.EnableRaisingEvents = $true  

### DEFINE ACTIONS AFTER AN EVENT IS DETECTED
$log_action = { $path = $Event.SourceEventArgs.FullPath
            $changeType = $Event.SourceEventArgs.ChangeType
            $logline = "$(Get-Date), $changeType, $path"
            Add-content "C:\Tasks\log.txt" -value $logline
          }    

$flip_action = { $vid_path = $Event.SourceEventArgs.FullPath
            $exePath = 'C:\Windows\exiftool.exe'
            $flipArgs = $args.Clone()

            $flipArgs += '-overwrite_original'
            $flipArgs += '-rotation=270'

            #If the shoes folder name doesnt contain _xmph, then this down's run. WTF
            & $exePath $flipArgs $vid_path
          }
### DECIDE WHICH EVENTS SHOULD BE WATCHED 
Register-ObjectEvent $watcher "Created" -Action $flip_action
### Register-ObjectEvent $watcher "Changed" -Action $log_action
Register-ObjectEvent $watcher "Deleted" -Action $log_action
Register-ObjectEvent $watcher "Renamed" -Action $log_action
while ($true) {Start-Sleep 5}