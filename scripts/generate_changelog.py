#!/usr/bin/env python3
"""
Generate changelog entries for documentation updates.

This script analyzes git changes and generates formatted changelog entries
following the Keep a Changelog format.
"""

import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple


def run_git_command(cmd: List[str]) -> str:
    """Run a git command and return its output."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running git command: {e}", file=sys.stderr)
        return ""


def get_changed_files() -> List[str]:
    """Get list of changed files from git."""
    output = run_git_command(["git", "diff", "--name-only", "HEAD"])
    if not output:
        # Try staged files if no unstaged changes
        output = run_git_command(["git", "diff", "--name-only", "--cached"])
    return [f for f in output.split("\n") if f]


def get_file_stats(filepath: str) -> Tuple[int, int]:
    """Get additions and deletions for a specific file."""
    # Try unstaged changes first
    output = run_git_command(["git", "diff", "--numstat", "HEAD", "--", filepath])
    if not output:
        # Try staged changes
        output = run_git_command(["git", "diff", "--numstat", "--cached", "--", filepath])

    if output:
        parts = output.split()
        if len(parts) >= 2:
            try:
                additions = int(parts[0]) if parts[0] != '-' else 0
                deletions = int(parts[1]) if parts[1] != '-' else 0
                return additions, deletions
            except ValueError:
                pass
    return 0, 0


def categorize_changes(files: List[str], source: str) -> Dict[str, List[Tuple[str, int, int]]]:
    """Categorize files into Added, Changed, or Removed with stats."""
    categories = {
        "Added": [],
        "Changed": [],
        "Removed": []
    }

    # Filter files by source
    source_prefix = f"docs/{source}/"
    filtered_files = [f for f in files if f.startswith(source_prefix)]

    for filepath in filtered_files:
        # Skip manifest and cache files from changelog
        if filepath.endswith("manifest.json") or "cache" in filepath:
            continue

        additions, deletions = get_file_stats(filepath)

        # Determine category based on stats
        if additions > 0 and deletions == 0:
            # Check if file actually exists (new file)
            if not Path(filepath).exists():
                categories["Removed"].append((filepath, additions, deletions))
            else:
                # Could be new or mostly additions
                try:
                    # Check git status to see if it's a new file
                    status = run_git_command(["git", "status", "--short", filepath])
                    if status.startswith("A") or status.startswith("??"):
                        categories["Added"].append((filepath, additions, deletions))
                    else:
                        categories["Changed"].append((filepath, additions, deletions))
                except:
                    categories["Changed"].append((filepath, additions, deletions))
        elif additions == 0 and deletions > 0:
            categories["Removed"].append((filepath, additions, deletions))
        elif additions > 0 or deletions > 0:
            categories["Changed"].append((filepath, additions, deletions))

    return categories


def format_source_name(source: str) -> str:
    """Format source name for display."""
    source_names = {
        "claude": "Claude Documentation",
        "reddit": "Reddit API Documentation"
    }
    return source_names.get(source, source.capitalize())


def generate_changelog_entry(source: str, date: str = None) -> str:
    """Generate a formatted changelog entry."""
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")

    files = get_changed_files()
    if not files:
        print("No changes detected", file=sys.stderr)
        return ""

    categories = categorize_changes(files, source)

    # Check if there are any relevant changes
    total_files = sum(len(files) for files in categories.values())
    if total_files == 0:
        print(f"No changes detected for {source} documentation", file=sys.stderr)
        return ""

    # Calculate totals
    total_additions = 0
    total_deletions = 0
    for category_files in categories.values():
        for _, additions, deletions in category_files:
            total_additions += additions
            total_deletions += deletions

    # Build changelog entry
    lines = [
        f"## [{date}] - {format_source_name(source)}",
        ""
    ]

    # Add each category if it has files
    for category in ["Added", "Changed", "Removed"]:
        if categories[category]:
            lines.append(f"### {category}")
            for filepath, additions, deletions in sorted(categories[category]):
                lines.append(f"- `{filepath}` (+{additions}, -{deletions})")
            lines.append("")

    # Add summary
    lines.append(f"**Total**: {total_files} file{'s' if total_files != 1 else ''} changed, "
                 f"+{total_additions} additions, -{total_deletions} deletions")
    lines.append("")

    return "\n".join(lines)


def update_changelog(entry: str, changelog_path: Path):
    """Prepend entry to existing changelog."""
    if not entry:
        print("No entry to add to changelog", file=sys.stderr)
        return

    # Read existing changelog
    if changelog_path.exists():
        with open(changelog_path, 'r') as f:
            existing_content = f.read()
    else:
        print(f"Warning: {changelog_path} does not exist", file=sys.stderr)
        return

    # Find where to insert (after the [Unreleased] section)
    lines = existing_content.split('\n')
    insert_index = 0

    # Find the line after [Unreleased] section
    for i, line in enumerate(lines):
        if line.startswith('## [Unreleased]'):
            # Skip to next non-empty line after [Unreleased]
            insert_index = i + 1
            while insert_index < len(lines) and not lines[insert_index].strip():
                insert_index += 1
            break

    # Insert the new entry
    if insert_index > 0:
        new_lines = lines[:insert_index] + [''] + entry.split('\n') + [''] + lines[insert_index:]
        new_content = '\n'.join(new_lines)
    else:
        # Fallback: append after header
        new_content = existing_content.split('\n\n', 2)
        if len(new_content) >= 2:
            new_content = f"{new_content[0]}\n\n{new_content[1]}\n\n{entry}\n\n" + (new_content[2] if len(new_content) > 2 else "")
        else:
            new_content = existing_content + "\n\n" + entry

    # Write updated changelog
    with open(changelog_path, 'w') as f:
        f.write(new_content)

    print(f"Updated {changelog_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate changelog entry for documentation updates"
    )
    parser.add_argument(
        "--source",
        required=True,
        choices=["claude", "reddit"],
        help="Documentation source (claude or reddit)"
    )
    parser.add_argument(
        "--date",
        help="Date for the changelog entry (YYYY-MM-DD, defaults to today)"
    )
    parser.add_argument(
        "--changelog",
        default="CHANGELOG.md",
        help="Path to changelog file (default: CHANGELOG.md)"
    )

    args = parser.parse_args()

    # Generate entry
    entry = generate_changelog_entry(args.source, args.date)

    if entry:
        # Get repository root (go up from scripts/ to root)
        repo_root = Path(__file__).parent.parent
        changelog_path = repo_root / args.changelog

        # Update changelog
        update_changelog(entry, changelog_path)
    else:
        print("No changelog entry generated", file=sys.stderr)
        sys.exit(0)  # Don't fail the workflow, just skip


if __name__ == "__main__":
    main()
