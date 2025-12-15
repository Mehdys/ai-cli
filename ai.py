#!/usr/bin/env python3
"""
AI CLI - Open or create projects in Cursor using natural language.
"""

import re
import subprocess
from pathlib import Path
from typing import List, Optional, Tuple

import typer
from rapidfuzz import fuzz, process

app = typer.Typer()

# Base projects directory - uses absolute path so it works from any directory
PROJECTS_DIR = Path.home() / "Desktop" / "Projects"

# Default category for newly created projects
CREATE_CATEGORY = "NotFinishedYet"

# Stopwords to filter out from queries
STOPWORDS = {
    "open", "the", "project", "about", "on", "cursor", "a", "an", "and", "or",
    "create", "start", "new", "init", "make", "called", "named", "it"
}

# Create intent keywords
CREATE_KEYWORDS = {"create", "start", "new", "init", "make"}

# Confidence threshold for fuzzy matching
CONFIDENCE_THRESHOLD = 55


def extract_keywords(text: str) -> List[str]:
    """Extract meaningful keywords from text, removing stopwords."""
    # Convert to lowercase and split
    words = re.findall(r'\b\w+\b', text.lower())
    # Filter out stopwords and return unique keywords
    keywords = [w for w in words if w not in STOPWORDS and len(w) > 1]
    return keywords


def normalize_project_name(name: str) -> str:
    """Normalize project name: lowercase, spaces to hyphens, keep [a-z0-9_-]."""
    # Convert to lowercase
    name = name.lower()
    # Replace spaces and underscores with hyphens
    name = re.sub(r'[\s_]+', '-', name)
    # Keep only alphanumeric, hyphens, and underscores
    name = re.sub(r'[^a-z0-9_-]', '', name)
    # Remove multiple consecutive hyphens
    name = re.sub(r'-+', '-', name)
    # Remove leading/trailing hyphens
    name = name.strip('-')
    return name


def detect_create_intent(text: str) -> bool:
    """Detect if the command is about creating a project."""
    text_lower = text.lower()
    has_create_keyword = any(keyword in text_lower for keyword in CREATE_KEYWORDS)
    has_project_keyword = "project" in text_lower
    return has_create_keyword and has_project_keyword


def extract_project_name(text: str) -> Optional[str]:
    """Extract project name from text using various patterns."""
    text_lower = text.lower()
    
    # Pattern 1: "called X" or "named X"
    patterns = [
        r'(?:called|named)\s+([a-z0-9\s_-]+?)(?:\s+and|\s*$)',
        r'project\s+([a-z0-9\s_-]+?)(?:\s+and|\s*$)',
        r'(?:create|start|new|init|make)\s+(?:a\s+)?(?:project\s+)?([a-z0-9\s_-]+?)(?:\s+and|\s*$)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text_lower)
        if match:
            name = match.group(1).strip()
            if name:
                return normalize_project_name(name)
    
    # Fallback: extract the last meaningful word sequence
    keywords = extract_keywords(text)
    if keywords:
        # Try to find a sequence that looks like a project name
        # Skip create keywords
        filtered = [k for k in keywords if k not in CREATE_KEYWORDS]
        if filtered:
            return normalize_project_name(' '.join(filtered))
    
    return None


def get_existing_projects() -> List[Tuple[str, Path]]:
    """
    Get list of existing projects, searching one level deep.
    Returns: List of (project_name, project_path) tuples.
    Searches in ~/Desktop/Projects/*/ for project folders.
    """
    try:
        if not PROJECTS_DIR.exists():
            return []
        
        projects = []
        # Search in each subdirectory of PROJECTS_DIR (one level deep)
        for category_dir in PROJECTS_DIR.iterdir():
            try:
                if not category_dir.is_dir() or category_dir.name.startswith('.'):
                    continue
                
                # Look for projects inside this category directory
                for project_dir in category_dir.iterdir():
                    try:
                        if project_dir.is_dir() and not project_dir.name.startswith('.'):
                            projects.append((project_dir.name, project_dir))
                    except (OSError, PermissionError):
                        # Skip directories we can't access
                        continue
            except (OSError, PermissionError):
                # Skip category directories we can't access
                continue
        
        # Sort by project name
        return sorted(projects, key=lambda x: x[0])
    except Exception as e:
        typer.echo(f"❌ Error reading projects directory: {e}", err=True)
        return []


def fuzzy_match_project(query: str, projects: List[Tuple[str, Path]]) -> Tuple[Optional[Path], Optional[str], int, List[Tuple[str, int]]]:
    """
    Fuzzy match query against projects.
    Args:
        query: Search query
        projects: List of (project_name, project_path) tuples
    Returns: (best_match_path, best_match_name, best_score, top_5_matches)
    """
    try:
        if not projects:
            return None, None, 0, []
        
        # Extract keywords from query
        keywords = extract_keywords(query)
        query_normalized = ' '.join(keywords)
        
        if not query_normalized:
            return None, None, 0, []
        
        # Extract just the project names for matching
        project_names = [name for name, _ in projects]
        
        # Use token_sort_ratio for fuzzy matching
        results = process.extract(
            query_normalized,
            project_names,
            scorer=fuzz.token_sort_ratio,
            limit=5
        )
        
        if not results:
            return None, None, 0, []
        
        best_match_name, best_score, _ = results[0]
        # Find the corresponding path for the best match
        best_match_path = next((path for name, path in projects if name == best_match_name), None)
        
        # Build top 5 matches with names and scores
        top_5 = [(name, score) for name, score, _ in results]
        
        return best_match_path, best_match_name, best_score, top_5
    except Exception as e:
        typer.echo(f"❌ Error during fuzzy matching: {e}", err=True)
        return None, None, 0, []


def open_in_cursor(path: Path) -> bool:
    """Open a path in Cursor."""
    try:
        if not path.exists():
            typer.echo(f"❌ Error: Path does not exist: {path}", err=True)
            return False
        
        # Try different methods to open Cursor
        import platform
        
        # Method 1: Try 'cursor' command (if in PATH)
        cursor_commands = ["cursor"]
        
        # Method 2: Try full path to cursor command (macOS)
        if platform.system() == "Darwin":
            cursor_commands.append("/Applications/Cursor.app/Contents/Resources/app/bin/cursor")
        
        # Method 3: Try macOS 'open' command as fallback
        use_open_command = False
        if platform.system() == "Darwin":
            use_open_command = True
        
        last_error = None
        for cmd in cursor_commands:
            try:
                subprocess.run(
                    [cmd, str(path)],
                    check=True,
                    capture_output=True,
                    timeout=10
                )
                return True
            except FileNotFoundError:
                last_error = "FileNotFoundError"
                continue
            except subprocess.CalledProcessError as e:
                last_error = f"Exit code {e.returncode}"
                continue
        
        # Fallback to macOS 'open' command
        if use_open_command:
            try:
                subprocess.run(
                    ["open", "-a", "Cursor", str(path)],
                    check=True,
                    capture_output=True,
                    timeout=10
                )
                return True
            except FileNotFoundError:
                typer.echo("❌ Error: Cursor is not installed or not found.", err=True)
                typer.echo("   Make sure Cursor is installed in /Applications/Cursor.app", err=True)
                return False
            except subprocess.CalledProcessError as e:
                typer.echo(f"❌ Error: Failed to open Cursor (exit code {e.returncode})", err=True)
                return False
        
        # If we get here, all methods failed
        typer.echo("❌ Error: 'cursor' command not found. Make sure Cursor is installed.", err=True)
        if platform.system() == "Darwin":
            typer.echo("   You can add Cursor to PATH by running:", err=True)
            typer.echo("   ln -s /Applications/Cursor.app/Contents/Resources/app/bin/cursor /usr/local/bin/cursor", err=True)
        return False
        
    except subprocess.TimeoutExpired:
        typer.echo("❌ Error: Cursor command timed out", err=True)
        return False
    except Exception as e:
        typer.echo(f"❌ Error opening in Cursor: {e}", err=True)
        return False


def create_project(project_name: str, base_dir: Optional[Path] = None) -> Path:
    """Create a new project: folder, git init, README."""
    try:
        target_base = base_dir or PROJECTS_DIR
        project_root = target_base / CREATE_CATEGORY

        # Ensure category directory exists
        try:
            project_root.mkdir(parents=True, exist_ok=True)
        except (OSError, PermissionError) as e:
            raise Exception(f"Failed to create category directory '{project_root}': {e}")

        project_path = project_root / project_name
        
        # Create directory if it doesn't exist
        try:
            project_path.mkdir(parents=True, exist_ok=True)
        except (OSError, PermissionError) as e:
            raise Exception(f"Failed to create project directory: {e}")
        
        # Initialize git if not already present
        git_dir = project_path / ".git"
        if not git_dir.exists() or not git_dir.is_dir():
            try:
                result = subprocess.run(
                    ["git", "init"],
                    cwd=project_path,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode != 0:
                    # Git init failed, but continue anyway
                    typer.echo(f"⚠️  Warning: Git initialization failed: {result.stderr}", err=True)
            except FileNotFoundError:
                typer.echo("⚠️  Warning: Git not found. Project created without git.", err=True)
            except subprocess.TimeoutExpired:
                typer.echo("⚠️  Warning: Git init timed out. Project created without git.", err=True)
            except Exception as e:
                typer.echo(f"⚠️  Warning: Git initialization error: {e}", err=True)
        
        # Create README.md if it doesn't exist
        readme_path = project_path / "README.md"
        if not readme_path.exists():
            try:
                with open(readme_path, 'w') as f:
                    f.write(f"# {project_name}\n")
            except (IOError, OSError) as e:
                raise Exception(f"Failed to create README.md: {e}")
        
        return project_path
    except Exception as e:
        typer.echo(f"❌ Error creating project: {e}", err=True)
        raise


@app.command()
def main(
    command: str = typer.Argument(..., help="Natural language command to open or create a project")
):
    """
    AI CLI - Open or create projects in Cursor using natural language.
    
    Examples:
    - ai "open local ai"
    - ai "create a project called voice-audit and open it"
    """
    try:
        # Ensure projects directory exists
        try:
            PROJECTS_DIR.mkdir(parents=True, exist_ok=True)
        except (OSError, PermissionError) as e:
            typer.echo(f"❌ Error: Cannot access or create projects directory: {e}", err=True)
            typer.echo(f"   Path: {PROJECTS_DIR}", err=True)
            raise typer.Exit(1)
        
        # Detect intent
        try:
            is_create = detect_create_intent(command)
        except Exception as e:
            typer.echo(f"❌ Error detecting intent: {e}", err=True)
            raise typer.Exit(1)
        
        if is_create:
            # Create project flow
            try:
                project_name = extract_project_name(command)
            except Exception as e:
                typer.echo(f"❌ Error extracting project name: {e}", err=True)
                raise typer.Exit(1)
            
            if not project_name:
                typer.echo("❌ Error: Could not extract project name from command.", err=True)
                typer.echo(f"   Command: {command}", err=True)
                raise typer.Exit(1)
            
            project_root = PROJECTS_DIR / CREATE_CATEGORY
            project_path = project_root / project_name
            
            if project_path.exists():
                typer.echo(f"✅ Project '{project_name}' already exists. Opening...")
            else:
                typer.echo(f"✅ Creating project '{project_name}'...")
                try:
                    project_path = create_project(project_name, base_dir=PROJECTS_DIR)
                    typer.echo(f"✅ Project created at {project_path}")
                except Exception as e:
                    typer.echo(f"❌ Failed to create project: {e}", err=True)
                    raise typer.Exit(1)
            
            typer.echo(f"✅ Opening project in Cursor...")
            if not open_in_cursor(project_path):
                raise typer.Exit(1)
            typer.echo(f"✅ Opened '{project_name}' in Cursor")
        
        else:
            # Open existing project flow
            try:
                projects = get_existing_projects()
            except Exception as e:
                typer.echo(f"❌ Error getting projects list: {e}", err=True)
                raise typer.Exit(1)
            
            if not projects:
                typer.echo(f"❌ No projects found in {PROJECTS_DIR}", err=True)
                raise typer.Exit(1)
            
            try:
                best_match_path, best_match_name, score, top_5 = fuzzy_match_project(command, projects)
            except Exception as e:
                typer.echo(f"❌ Error during fuzzy matching: {e}", err=True)
                raise typer.Exit(1)
            
            if best_match_path and best_match_name and score >= CONFIDENCE_THRESHOLD:
                typer.echo(f"✅ Opening project '{best_match_name}' (confidence: {score}%)")
                if not open_in_cursor(best_match_path):
                    raise typer.Exit(1)
                typer.echo(f"✅ Opened '{best_match_name}' in Cursor")
            else:
                typer.echo("🤔 Not confident about the match. Top matches:")
                if top_5:
                    for i, (name, match_score) in enumerate(top_5, 1):
                        typer.echo(f"   {i}. {name} (confidence: {match_score}%)")
                else:
                    typer.echo("   No matches found.")
                typer.echo("\n💡 Try being more specific or use one of the suggestions above.")
    
    except typer.Exit:
        raise
    except KeyboardInterrupt:
        typer.echo("\n❌ Operation cancelled by user", err=True)
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"❌ Unexpected error: {e}", err=True)
        raise typer.Exit(1)


if __name__ == "__main__":
    app()

