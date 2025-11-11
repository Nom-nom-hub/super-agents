#!/bin/bash
# Super-Agents Context Update Script (Bash/POSIX)
# Updates agent-specific context files with latest super-agent specifications
# Works with: Claude, Copilot, Amp, Cursor, Windsurf, Amazon Q, etc.

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
COMPANY_DIR="$PROJECT_ROOT/company"
AGENT_TYPE="${1:-}"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

# Check if we're in a super-agents project
if [ ! -f "$COMPANY_DIR/agent_registry.yaml" ]; then
    print_error "Agent registry not found at $COMPANY_DIR/agent_registry.yaml. Are you in a super-agents project?"
    exit 1
fi

# Parse agent registry to get the agent folder - simplified
get_agent_folder() {
    local agent_id=$1
    grep -A 10 "^  $agent_id:" "$COMPANY_DIR/agent_registry.yaml" | grep "folder:" | head -1 | awk '{print $2}' | sed 's/"//g' | sed "s/'//g"
}

# Update context for a specific agent
update_agent_context() {
    local agent_id=$1
    local agent_folder=$(get_agent_folder "$agent_id")

    if [ -z "$agent_folder" ]; then
        print_error "Unknown agent: $agent_id"
        return 1
    fi

    local context_file="$PROJECT_ROOT/$agent_folder/super-agents-context.md"

    mkdir -p "$(dirname "$context_file")"

    # Generate context file
    > "$context_file"  # Clear the file first
    {
        echo "# Super-Agents Context for $agent_id"
        echo ""
        echo "Last updated: $(date '+%Y-%m-%d %H:%M:%S')"
        echo ""
        echo "This file provides context for working with AICODE Labs super-agents."
        echo ""
        echo "## Complete Super-Agent Specifications"
        echo ""
        echo "For complete super-agent specifications, see:"
        echo "- super-agents-context.yaml (in the same directory)"
        echo "- The agent specifications in $COMPANY_DIR/agents/"
        echo ""
        echo "## How to Use Super-Agents"
        echo ""
        echo "The super-agents system allows you to delegate specialized tasks to autonomous agents."
        echo "Each agent has specific capabilities and responsibilities within the AICODE Labs organization."
        echo ""
        echo "### Agent Categories:"
        echo ""
        echo "- **Executive Division**: CEO, CTO, COO for strategic decisions"
        echo "- **Product Division**: Product Manager, UX Designer, Market Analyst for requirements"
        echo "- **Engineering Division**: Backend, Frontend, AI, DevOps Engineers for implementation"
        echo "- **Quality Division**: QA and Reliability Engineers for validation"
        echo "- **Security Division**: Security Engineer for protection measures"
        echo "- **Knowledge Division**: Tech Writer and Knowledge Architect for documentation"
        echo "- **Governance Division**: Meta Architect for system evolution"
        echo "- **Expansion Division**: Finance Agent, Research Agent, etc. for growth"
        echo ""
        echo "### Task Delegation Pattern"
        echo ""
        echo "Use the delegation pattern to coordinate with super-agents:"
        echo ""
        echo "\`\`\`"
        echo "@agent_id: Your task description here"
        echo "\`\`\`"
        echo ""
        echo "### Examples:"
        echo ""
        echo "\`\`\`"
        echo "@backend_engineer: Design a REST API for product catalog with Postgres backend"
        echo "@ux_designer: Create mobile-responsive UI components for dashboard"
        echo "@qa_engineer: Write integration tests for payment flow"
        echo "@security_engineer: Implement OAuth2 authentication with JWT tokens"
        echo "@devops_engineer: Set up CI/CD pipeline with Docker and Kubernetes"
        echo "@ai_engineer: Create recommendation engine model using LangChain"
        echo "\`\`\`"
        echo ""
        echo "### Best Practices"
        echo ""
        echo "1. Be specific about requirements and constraints"
        echo "2. Reference existing specifications when relevant" 
        echo "3. Include success criteria and acceptance tests when applicable"
        echo "4. Consider dependencies on other agents' work"
        echo "5. Plan complex workflows across multiple agents"
        echo ""
    } > "$context_file"

    print_status "Updated context for $agent_id at $agent_folder"
    return 0
}

# Hardcoded list of agents for the "all" operation since complex parsing is problematic
update_all_agents() {
    print_info "Updating context for all agents..."

    local agents=("claude" "copilot" "amp" "gemini" "cursor" "windsurf" "q" "qwen" "kilocode")
    local count=0
    
    for agent in "${agents[@]}"; do
        if update_agent_context "$agent"; then
            ((count++)) || true
        fi
    done

    print_status "Updated $count agent contexts"
}

# Main logic
if [ -z "$AGENT_TYPE" ]; then
    print_info "No agent specified. Updating all agents..."
    update_all_agents
else
    print_info "Updating context for: $AGENT_TYPE"
    if update_agent_context "$AGENT_TYPE"; then
        exit 0
    else
        exit 1
    fi
fi