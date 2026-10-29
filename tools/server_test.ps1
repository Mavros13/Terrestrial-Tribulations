# Terrestrial Tribulations: headless server test (Windows PowerShell 5.1+).
# Boots a Forge dedicated server with the Test Build 1 mods (stages A-C) and our kubejs + config folders, waits for it
# to finish loading, runs `kubejs errors` and `reload`, stops it, and writes a short report of anything that went
# wrong with our content. Everything happens in %TEMP%\tt-servertest, which is deleted at the end; only the report
# (%TEMP%\tt-servertest-report.txt) is kept. No game window; the server runs at below-normal priority with 3 GB.
#
# Run in PowerShell (no admin needed):
#   irm https://raw.githubusercontent.com/Mavros13/Terrestrial-Tribulations/claude/project-thread-gnjvhs/tools/server_test.ps1 | iex
$Branch = 'claude/project-thread-gnjvhs'
$Forge = '1.20.1-47.4.18'
$Stages = if ($env:TT_STAGES) { $env:TT_STAGES -split ',' } else { @('A', 'B', 'C') }   # TT_STAGES=A,B,C,D for Test Build 2

$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'   # Invoke-WebRequest is very slow with the progress bar
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$root = Join-Path $env:TEMP 'tt-servertest'
$report = Join-Path $env:TEMP 'tt-servertest-report.txt'
$lines = New-Object System.Collections.Generic.List[string]
function Say($m) { Write-Host "[TT test] $m"; $lines.Add($m) }

try {
  if (Test-Path $root) { Remove-Item $root -Recurse -Force }
  New-Item -ItemType Directory $root | Out-Null
  $server = Join-Path $root 'server'; New-Item -ItemType Directory $server | Out-Null
  $mods = Join-Path $server 'mods'; New-Item -ItemType Directory $mods | Out-Null

  Say 'Downloading Java 17 (portable)...'
  Invoke-WebRequest 'https://api.adoptium.net/v3/binary/latest/17/ga/windows/x64/jdk/hotspot/normal/eclipse' -OutFile "$root\jdk.zip"
  Expand-Archive "$root\jdk.zip" "$root\jdk"
  $java = (Get-ChildItem "$root\jdk" -Recurse -Filter java.exe | Where-Object { $_.FullName -like '*\bin\java.exe' } | Select-Object -First 1).FullName

  Say "Downloading the pack ($Branch)..."
  Invoke-WebRequest "https://github.com/Mavros13/Terrestrial-Tribulations/archive/refs/heads/$Branch.zip" -OutFile "$root\pack.zip"
  Expand-Archive "$root\pack.zip" "$root\pack"
  $repo = (Get-ChildItem "$root\pack" -Directory | Select-Object -First 1).FullName

  Say "Installing Forge $Forge server..."
  Invoke-WebRequest "https://maven.minecraftforge.net/net/minecraftforge/forge/$Forge/forge-$Forge-installer.jar" -OutFile "$root\forge-installer.jar"
  Push-Location $server
  & $java -jar "$root\forge-installer.jar" --installServer | Out-File "$root\forge-install.log"
  Pop-Location
  if (-not (Test-Path "$server\libraries\net\minecraftforge\forge\$Forge\win_args.txt")) { throw 'Forge server install failed (see forge-install.log)' }

  Say "Downloading mods for stages $($Stages -join ',') from CurseForge..."
  $skip = @('Embeddium', 'Oculus')   # client-only renderers; entries with "side": "client" are skipped too
  $list = (Get-Content "$repo\modpack\curseforge-mods.json" -Raw | ConvertFrom-Json).mods |
    Where-Object { $Stages -contains $_.stage -and $skip -notcontains $_.name -and $_.side -ne 'client' }
  $failed = @()
  foreach ($m in $list) {
    $out = Join-Path $mods ("{0}-{1}.jar" -f $m.projectID, $m.fileID)
    try {
      Invoke-WebRequest "https://www.curseforge.com/api/v1/mods/$($m.projectID)/files/$($m.fileID)/download" -OutFile $out -UserAgent 'Mozilla/5.0'
    } catch {
      $id = [int64]$m.fileID
      $name = if ($m.file -like '*.jar') { $m.file } else { "$($m.file).jar" }
      try { Invoke-WebRequest ("https://mediafilez.forgecdn.net/files/{0}/{1}/{2}" -f [math]::Floor($id / 1000), ($id % 1000), [uri]::EscapeDataString($name)) -OutFile $out }
      catch { $failed += $m.name; if (Test-Path $out) { Remove-Item $out } }
    }
  }
  Say ("Mods downloaded: {0} of {1}" -f ($list.Count - $failed.Count), $list.Count)
  if ($failed.Count) { Say ('Could not download: ' + ($failed -join ', ')) }

  Copy-Item "$repo\pack\kubejs" "$server\kubejs" -Recurse
  Copy-Item "$repo\pack\config" "$server\config" -Recurse -Force
  Set-Content "$server\eula.txt" 'eula=true'
  Set-Content "$server\server.properties" "online-mode=false`nview-distance=4`nsimulation-distance=4`nspawn-protection=0`nmax-tick-time=-1`nmotd=TT test"
  # max-tick-time=-1: no watchdog. A /reload of the full pack can block one tick for over 60 s on a laptop at
  # below-normal priority (2026-10-29: ModernFix resource cache + Palladium addon preload), which killed the server.
  Set-Content "$server\user_jvm_args.txt" $(if ($Stages -contains 'D') { '-Xmx4G' } else { '-Xmx3G' })

  Say 'Starting the server (hidden, below-normal priority)...'
  $psi = New-Object System.Diagnostics.ProcessStartInfo
  $psi.FileName = $java
  $psi.Arguments = "@user_jvm_args.txt @libraries/net/minecraftforge/forge/$Forge/win_args.txt nogui"
  $psi.WorkingDirectory = $server
  $psi.UseShellExecute = $false
  $psi.CreateNoWindow = $true
  $psi.RedirectStandardInput = $true
  $psi.RedirectStandardOutput = $true
  $psi.RedirectStandardError = $true
  $p = New-Object System.Diagnostics.Process
  $p.StartInfo = $psi
  $null = $p.Start()
  $p.PriorityClass = 'BelowNormal'
  $p.BeginOutputReadLine(); $p.BeginErrorReadLine()   # drain output so the server never blocks

  $log = "$server\logs\latest.log"
  $deadline = (Get-Date).AddMinutes(20)
  $done = $false
  while ((Get-Date) -lt $deadline -and -not $p.HasExited) {
    Start-Sleep 10
    if ((Test-Path $log) -and (Select-String -Path $log -Pattern 'Done \(' -Quiet)) { $done = $true; break }
    if ((Test-Path $log) -and (Select-String -Path $log -Pattern 'Failed to start the minecraft server' -Quiet)) {
      Start-Sleep 5; if (-not $p.HasExited) { $p.Kill(); $null = $p.WaitForExit(10000) }   # Forge can hang after a failed start
      break
    }
  }
  if ($done) {
    Say 'Server finished loading. Running kubejs errors, reload, tt_selftest, stop...'
    $p.StandardInput.WriteLine('kubejs errors server'); Start-Sleep 5
    $p.StandardInput.WriteLine('reload'); Start-Sleep 120
    $p.StandardInput.WriteLine('kubejs custom_command tt_selftest'); Start-Sleep 10
    # Smoke test: mobs take every common damage type while our hurt handlers listen, then the world ticks a while
    foreach ($c in @('forceload add -16 -16 16 16', 'summon minecraft:zombie 0 100 0 {NoAI:1b,PersistenceRequired:1b}',
        'summon minecraft:skeleton 3 100 0 {NoAI:1b,PersistenceRequired:1b}', 'summon minecraft:villager 0 100 3 {NoAI:1b}',
        'say [TT] damage test: start',
        'damage @e[type=minecraft:zombie,limit=1] 2 minecraft:arrow', 'damage @e[type=minecraft:zombie,limit=1] 2 minecraft:magic',
        'damage @e[type=minecraft:zombie,limit=1] 2 minecraft:generic', 'damage @e[type=minecraft:villager,limit=1] 2 minecraft:mob_attack by @e[type=minecraft:skeleton,limit=1]',
        'damage @e[type=minecraft:skeleton,limit=1] 50 minecraft:out_of_world',
        'summon minecraft:wither 0 100 -4 {NoAI:1b,Invul:0}', 'damage @e[type=minecraft:wither,limit=1] 5 minecraft:generic',
        'kill @e[type=minecraft:wither]',
        # (the zombie burns in daylight, so only the villager is checked; KubeJS errors from the hurt handlers show below)
        'execute if entity @e[type=minecraft:villager] run say [TT] damage test: done, the hurt handlers ran without stopping the server',
        'execute unless entity @e[type=minecraft:wither] run say [TT] damage test: wither removed',
        # Story NPC presets (tools/gen_npcs.py): each should import as a new Easy NPC
        'easy_npc preset import_new data tt:easy_npc/preset/humanoid_slim/maera.npc.snbt 0 100 8',
        'easy_npc preset import_new data tt:easy_npc/preset/humanoid/doran.npc.snbt 2 100 8',
        'easy_npc preset import_new data tt:easy_npc/preset/humanoid/rhosk.npc.snbt 4 100 8',
        'easy_npc preset import_new data tt:easy_npc/preset/humanoid/pell.npc.snbt 6 100 8',
        'easy_npc preset import_new data tt:easy_npc/preset/humanoid_slim/tamsin.npc.snbt 8 100 8',
        'easy_npc preset import_new data tt:easy_npc/preset/humanoid_slim/ilsabet.npc.snbt 10 100 8',
        'easy_npc preset import_new data tt:easy_npc/preset/humanoid/stranger.npc.snbt 12 100 8',
        'easy_npc preset import_new data tt:easy_npc/preset/humanoid_slim/wren.npc.snbt 14 100 8',
        'easy_npc preset import_new data tt:easy_npc/preset/humanoid/sol.npc.snbt 16 100 8',
        'easy_npc list',
        # Story NPC sites (tools/gen_npc_sites.py): each structure places; the camp at spawn logs its own [TT] line
        'forceload add 32 -16 260 16',
        'place structure tt:npc/thornwatch_outpost 40 100 0', 'place structure tt:npc/pell_ruin 70 100 0',
        'place structure tt:npc/tamsin_grove 100 100 0', 'place structure tt:npc/conclave_tower 130 100 0',
        'place structure tt:npc/stranger_caravan 160 100 0', 'place structure tt:npc/wren_lookout 190 100 0',
        'place structure tt:npc/sol_archive 220 100 0', 'place structure tt:npc/refugee_camp 250 100 0',
        'time add 6000', 'chunky progress')) {
      $p.StandardInput.WriteLine($c); Start-Sleep 2
    }
    Start-Sleep 60
    $p.StandardInput.WriteLine('stop')
    if (-not $p.WaitForExit(120000)) { $p.Kill() }
  } elseif ($p.HasExited) {
    Say "Server failed to start; see the errors and crash report below."
  } else {
    Say 'Server did not finish loading within 20 minutes; stopping it.'
    $p.Kill()
  }

  # ---------- report ----------
  # Other mods' load chatter fills any line cap before the results; drop it instead of capping early.
  $noise = 'Loaded Java class|Loaded script addonpack|Failed to parse recipe|Tried to add unknown item|^\s+at '
  # Our own log lines first, so no cap can push them out
  $lines.Add(''); $lines.Add('=== [TT] lines (all logs) ===')
  Get-ChildItem "$server\logs" -Recurse -Filter *.log -ErrorAction SilentlyContinue |
    Select-String -Pattern '\[TT\]' | ForEach-Object { $lines.Add("$($_.Filename): $($_.Line)") }
  # Everything the server logged after it finished loading: the Done line, the test commands' own feedback (NPC
  # preset imports, easy_npc list, damage smoke test) and any error they caused. Other mods' load errors can fill
  # the 300-line cap below before these, so they get their own section.
  # The reload repeats every other mod's datapack errors (loot tables, tags, recipes); skip those here.
  $reloadNoise = 'ForgeHooks|TagLoader|LootDataType|LootTable|RecipeManager|Couldn''t parse|Couldn''t load|Failed to load|Missing pack_format|Parsing error'
  $lines.Add(''); $lines.Add('=== latest.log from "Done" on: test commands and their results ===')
  if (Test-Path $log) {
    $after = $false
    # Only what our commands and scripts produce: command feedback (MinecraftServer), our [TT] lines, Easy NPC,
    # KubeJS and structure placement. A whitelist, because other mods' reload errors span many line shapes.
    $keep = 'MinecraftServer\]|\[TT\]|easy_?npc|EasyNPC|KubeJS|kubejs|tt:|Done \(|place|structure|Stopping|[Cc]hunky'
    Get-Content $log | ForEach-Object {
      if (-not $after -and $_ -match 'Done \(') { $after = $true }
      if ($after -and $_ -match $keep -and $_ -notmatch $noise -and $_ -notmatch $reloadNoise -and $_ -notmatch '^\s') { $_ }
    } | Select-Object -First 1200 | ForEach-Object { $lines.Add($_) }
  }
  # Third-party data that fails to load, by ID, so it can be switched off with a data pack override
  $lines.Add(''); $lines.Add('=== corewithstuff: failed recipes and loot tables (distinct IDs) ===')
  if (Test-Path $log) {
    Select-String -Path $log -Pattern 'corewithstuff:[a-z0-9_/.\-]+' -AllMatches |
      Where-Object { $_.Line -match 'recipe|loot|Couldn''t parse|Failed to' } |
      ForEach-Object { $kind = if ($_.Line -match 'loot') { 'loot' } else { 'recipe' }; foreach ($m in $_.Matches) { "$kind $($m.Value)" } } |
      Sort-Object -Unique | ForEach-Object { $lines.Add($_) }
    $lines.Add(''); $lines.Add('--- sample lines ---')
    Select-String -Path $log -Pattern 'corewithstuff' | Select-Object -First 3 | ForEach-Object { $lines.Add($_.Line) }
    $lines.Add(''); $lines.Add('--- empty block id command, with context ---')
    Select-String -Path $log -Pattern "Unknown block type 'minecraft:'" -Context 3,1 | Select-Object -First 2 | ForEach-Object {
      $_.Context.PreContext | ForEach-Object { $lines.Add($_) }; $lines.Add($_.Line); $_.Context.PostContext | ForEach-Object { $lines.Add($_) } }
  }
  $lines.Add(''); $lines.Add('=== latest.log: errors and our content ===')
  if (Test-Path $log) {
    Select-String -Path $log -Pattern 'ERROR|Exception|\[TT\]|tt:|kubejs|Failed to load|Done \(' |
      Where-Object { $_.Line -notmatch $noise } | Select-Object -First 300 | ForEach-Object { $lines.Add($_.Line) }
  }
  foreach ($k in 'startup.log', 'server.log') {
    $f = "$server\logs\kubejs\$k"
    if (Test-Path $f) {
      $lines.Add(''); $lines.Add("=== kubejs/$k (errors, warnings and tt lines) ===")
      Select-String -Path $f -Pattern 'ERR|WARN|\[TT\]|tt_|Loaded script|scripts? in' |
        Where-Object { $_.Line -notmatch $noise } | Select-Object -First 300 | ForEach-Object { $lines.Add($_.Line) }
    }
  }
  Get-ChildItem "$server\crash-reports" -ErrorAction SilentlyContinue | ForEach-Object {
    $lines.Add(''); $lines.Add("=== crash report $($_.Name) (first 80 lines) ===")
    Get-Content $_.FullName -TotalCount 80 | ForEach-Object { $lines.Add($_) }
  }
} catch {
  Say "Test stopped: $($_.Exception.Message)"
} finally {
  Get-Process java -ErrorAction SilentlyContinue | Where-Object { $_.Path -like "$root*" } | Stop-Process -Force -ErrorAction SilentlyContinue
  Start-Sleep 2
  $lines | Set-Content $report -Encoding UTF8
  Remove-Item $root -Recurse -Force -ErrorAction SilentlyContinue
  Write-Host ''
  Write-Host "[TT test] Finished. Report: $report  (test folder deleted: $(-not (Test-Path $root)))"
}
