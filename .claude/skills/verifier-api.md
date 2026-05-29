# verifier-api

Smoke-test the rohit-ai-os production API at https://api.rohitnikam.tech.
Covers: health, auth enforcement, and Digital Twin conversation memory.

## Setup

Read the API key from the local .env file:

```powershell
$key = (Get-Content "D:\Development Projects\rohit-ai-operating-system\.env" |
        Where-Object { $_ -match "^API_KEY=" }) -replace "^API_KEY=", ""
if (-not $key) { Write-Error "API_KEY not found in .env"; exit 1 }
$base = "https://api.rohitnikam.tech"
```

## Steps

### 1. Health check (public endpoint)
```powershell
$h = Invoke-RestMethod -Uri "$base/health"
# expect: status = "ok"
```

### 2. Auth enforcement
```powershell
# Without key → must be 401
try {
    Invoke-RestMethod -Uri "$base/tasks/" -Method POST `
        -Headers @{ "Content-Type" = "application/json" } `
        -Body '{"task_type":"digital_twin","input":"test"}'
    Write-Warning "FAIL: expected 401 but got 2xx"
} catch {
    $code = $_.Exception.Response.StatusCode.value__
    if ($code -eq 401) { Write-Host "Auth 401 OK" } else { Write-Warning "FAIL: got $code, expected 401" }
}
```

### 3. Digital Twin — single turn
```powershell
$session = [System.Guid]::NewGuid().ToString()
$headers = @{ "Content-Type" = "application/json"; "X-API-Key" = $key }

function Submit-Task($input, $session) {
    $body = @{ task_type = "digital_twin"; input = $input; context = @{ session_id = $session } } | ConvertTo-Json
    $r = Invoke-RestMethod -Uri "$base/tasks/" -Method POST -Headers $headers -Body $body
    do {
        Start-Sleep -Seconds 3
        $poll = Invoke-RestMethod -Uri "$base/tasks/$($r.task_id)"
    } while ($poll.status -eq "pending" -or $poll.status -eq "running")
    return $poll.output
}

$out1 = Submit-Task "What is Rohit's tech stack?" $session
Write-Host "Turn 1: $($out1.Substring(0, [Math]::Min(200, $out1.Length)))..."
```

### 4. Digital Twin — conversation memory (turn 2)
```powershell
$out2 = Submit-Task "Which of those do you use most heavily?" $session
Write-Host "Turn 2: $($out2.Substring(0, [Math]::Min(200, $out2.Length)))..."
# Memory is working if turn 2 references the tech stack from turn 1
# without restating the question
```

### 5. Session isolation (new session should not see prior history)
```powershell
$newSession = [System.Guid]::NewGuid().ToString()
$out3 = Submit-Task "Which of those do you use most heavily?" $newSession
Write-Host "New session turn 1: $($out3.Substring(0, [Math]::Min(200, $out3.Length)))..."
# Should ask a clarifying question or give a generic answer — not reference the tech stack
```

## Pass criteria

| Check | Pass if |
|---|---|
| Health | `status == "ok"` |
| Auth | 401 without key |
| Turn 1 | Non-empty response about Rohit's stack |
| Turn 2 (memory) | References tech from turn 1 without re-asking |
| New session | Does NOT reference the previous session's context |
