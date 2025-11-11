# Super-Agents Context Update Script (PowerShell)
# Updates agent-specific context files with latest super-agent specifications
# Works with: Claude, Copilot, Amp, Cursor, Windsurf, Amazon Q, etc.

param(
    [string]$AgentType = ""
)

# Setup paths
try {
    $repoRoot = git rev-parse --show-toplevel 2>$null
} catch {
    $repoRoot = "."
}

$companyDir = Join-Path $repoRoot "company"
$agentRegistryPath = Join-Path $companyDir "agent_registry.yaml"
$agentDir = Join-Path $companyDir "agents"

# Color codes
$greenCheck = "[✓]"
$redX = "[✗]"
$blueInfo = "[ℹ]"

# Check if we're in a super-agents project
if (-not (Test-Path $agentRegistryPath)) {
    Write-Host "$redX Agent registry not found. Are you in a super-agents project?" -ForegroundColor Red
    exit 1
}

# Parse YAML to get agent folders
# Simple parser for our specific format
function Get-AgentFolder {
    param([string]$AgentId)

    $content = Get-Content $agentRegistryPath -Raw
    if ($content -match "  $AgentId:`n(.*?)folder: '([^']+)'") {
        return $matches[2]
    }
    if ($content -match "  $AgentId:`n(.*?)folder: `"([^`"]+)`"") {
        return $matches[2]
    }
    if ($content -match "  $AgentId:`n(.*?)folder: ([^\n]+)") {
        return $matches[2].Trim()
    }
    return $null
}

# Parse agent specs from YAML
function Get-AgentSpecs {
    $agents = @()
    $agentFiles = Get-ChildItem -Path $agentDir -Filter "*_agent.yaml" -ErrorAction SilentlyContinue

    foreach ($file in $agentFiles) {
        $content = Get-Content $file -Raw

        # Simple YAML parsing
        if ($content -match "^id:\s*(.+?)$") {
            $id = $matches[1].Trim()
        }
        if ($content -match "^title:\s*(.+?)$") {
            $title = $matches[1].Trim().Trim("'`"")
        }
        if ($content -match "^mission:\s*(.+?)$") {
            $mission = $matches[1].Trim().Trim("'`"")
        }

        if ($id) {
            $agents += @{
                id      = $id
                title   = $title
                mission = $mission
            }
        }
    }

    return $agents
}

# Update context for a specific agent
function Update-AgentContext {
    param([string]$AgentId)

    $agentFolder = Get-AgentFolder $AgentId

    if (-not $agentFolder) {
        Write-Host "$redX Unknown agent: $AgentId" -ForegroundColor Red
        return $false
    }

    $contextFile = Join-Path $repoRoot $agentFolder "super-agents-context.md"
    $contextDir = Split-Path $contextFile -Parent

    # Create directory if needed
    if (-not (Test-Path $contextDir)) {
        New-Item -ItemType Directory -Path $contextDir -Force | Out-Null
    }

    # Get agent specs
    $agents = Get-AgentSpecs
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

    # Generate context file
    $content = @"
# Super-Agents Context

Last updated: $timestamp

## Available Super-Agents

"@

    foreach ($agent in $agents) {
        $content += @"
### $($agent.id) - $($agent.title)

$($agent.mission)

"@
    }

    $content += @"
## How to Delegate Tasks

Use the delegation pattern to coordinate with super-agents:

\`\`\`
@agent_id: Your task description here
\`\`\`

Example:
\`\`\`
@backend_engineer: Design a REST API for product catalog
@ux_designer: Create mobile-responsive UI components
@qa_engineer: Write integration tests for payment flow
\`\`\`

"@

    Set-Content -Path $contextFile -Value $content -Encoding UTF8

    Write-Host "$greenCheck Updated context for $AgentId at $agentFolder" -ForegroundColor Green
    return $true
}

# Update all agent contexts
function Update-AllAgents {
    Write-Host "$blueInfo Updating context for all agents..." -ForegroundColor Cyan

    $registryContent = Get-Content $agentRegistryPath -Raw

    # Extract agent IDs using regex
    $agentIds = [regex]::Matches($registryContent, "^\s{2}([a-z_]+):\s*$", [System.Text.RegularExpressions.RegexOptions]::Multiline) |
    ForEach-Object { $_.Groups[1].Value } |
    Sort-Object -Unique

    $count = 0
    foreach ($agent in $agentIds) {
        if (Update-AgentContext $agent) {
            $count++
        }
    }

    Write-Host "$greenCheck Updated $count agent contexts" -ForegroundColor Green
}

# Main logic
if ([string]::IsNullOrEmpty($AgentType)) {
    Write-Host "$blueInfo No agent specified. Updating all agents..." -ForegroundColor Cyan
    Update-AllAgents
} else {
    Write-Host "$blueInfo Updating context for: $AgentType" -ForegroundColor Cyan
    if (Update-AgentContext $AgentType) {
        exit 0
    } else {
        exit 1
    }
}
