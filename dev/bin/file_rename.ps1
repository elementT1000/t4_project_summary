$in = Read-Host -Prompt "Enter the patients initials"
$date = Get-Date -Format "MMddyy"
$fw = Read-Host -Prompt "Enter 's' if they are wearing Shoes, 'ns' for no shoes"

<#Dir -File -Recurse |
    Rename-Item -NewName {
        if ($_.Basename.contains("[A-Z]")) {
            $_.Basename -replace "[A-Z]", "[a-z]"
        }
        else {
            $_.Basename # no change
            Write-Host "All of the letters in the name are lower case."
            
        }
    }
    #>
Dir -File -Recurse | 
    ForEach-Object {
        $ext = $_.Extension
        $lowername = $_.Basename.ToLower()
        $shortname = $lowername.Substring(0, 2)
        $newname = $in + "_" + $date + "_" + $shortname + "_" + $fw + $ext
        Rename-Item $_ $newname
    }

exiftool -r -overwrite_original -rotation=90 .
