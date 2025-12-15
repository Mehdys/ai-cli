#!/usr/bin/env python3
"""
Tests for AI CLI
"""

import subprocess
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from typer.testing import CliRunner

from ai import (
    CONFIDENCE_THRESHOLD,
    extract_keywords,
    normalize_project_name,
    detect_create_intent,
    extract_project_name,
    get_existing_projects,
    fuzzy_match_project,
    open_in_cursor,
    create_project,
    app,
)


@pytest.fixture
def temp_projects_dir():
    """Create a temporary projects directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def runner():
    """CLI test runner."""
    return CliRunner()


class TestExtractKeywords:
    """Tests for extract_keywords function."""
    
    def test_basic_keywords(self):
        result = extract_keywords("open local ai project")
        assert "local" in result
        assert "ai" in result
        assert "open" not in result  # stopword
        assert "project" not in result  # stopword
    
    def test_stopwords_removed(self):
        result = extract_keywords("open the project about local ai on cursor")
        assert "the" not in result
        assert "about" not in result
        assert "on" not in result
        assert "cursor" not in result
    
    def test_empty_string(self):
        result = extract_keywords("")
        assert result == []
    
    def test_only_stopwords(self):
        result = extract_keywords("open the project")
        assert len(result) == 0 or all(w not in ["open", "the", "project"] for w in result)


class TestNormalizeProjectName:
    """Tests for normalize_project_name function."""
    
    def test_lowercase(self):
        assert normalize_project_name("MyProject") == "myproject"
    
    def test_spaces_to_hyphens(self):
        assert normalize_project_name("my project") == "my-project"
        assert normalize_project_name("my  project") == "my-project"
    
    def test_underscores_to_hyphens(self):
        assert normalize_project_name("my_project") == "my-project"
    
    def test_special_chars_removed(self):
        assert normalize_project_name("my@project#123") == "myproject123"
    
    def test_multiple_hyphens(self):
        assert normalize_project_name("my---project") == "my-project"
    
    def test_leading_trailing_hyphens(self):
        assert normalize_project_name("-my-project-") == "my-project"
    
    def test_mixed_case_spaces(self):
        assert normalize_project_name("My Project Name") == "my-project-name"


class TestDetectCreateIntent:
    """Tests for detect_create_intent function."""
    
    def test_create_keyword(self):
        assert detect_create_intent("create a project") == True
        assert detect_create_intent("start new project") == True
        assert detect_create_intent("init project") == True
        assert detect_create_intent("make a project") == True
    
    def test_no_create_keyword(self):
        assert detect_create_intent("open project") == False
        assert detect_create_intent("show projects") == False
    
    def test_create_without_project(self):
        assert detect_create_intent("create something") == False
    
    def test_case_insensitive(self):
        assert detect_create_intent("CREATE A PROJECT") == True
        assert detect_create_intent("Create Project") == True


class TestExtractProjectName:
    """Tests for extract_project_name function."""
    
    def test_called_pattern(self):
        assert extract_project_name("create a project called voice-audit") == "voice-audit"
        assert extract_project_name("start project named my-app") == "my-app"
    
    def test_project_pattern(self):
        assert extract_project_name("create project credit-agent") == "credit-agent"
    
    def test_create_pattern(self):
        assert extract_project_name("create voice-audit") == "voice-audit"
        assert extract_project_name("start new project test-app") == "test-app"
    
    def test_normalization_applied(self):
        result = extract_project_name("create a project called My Test App")
        assert result == "my-test-app"
    
    def test_no_match(self):
        # Should return None or a fallback
        result = extract_project_name("just some random text")
        # Either None or some extracted value
        assert result is None or isinstance(result, str)


class TestGetExistingProjects:
    """Tests for get_existing_projects function."""
    
    def test_empty_directory(self, temp_projects_dir):
        with patch('ai.PROJECTS_DIR', temp_projects_dir):
            projects = get_existing_projects()
            assert projects == []
    
    def test_finds_projects_one_level_deep(self, temp_projects_dir):
        with patch('ai.PROJECTS_DIR', temp_projects_dir):
            # Create category directories with projects inside
            category1 = temp_projects_dir / "category1"
            category2 = temp_projects_dir / "category2"
            category1.mkdir()
            category2.mkdir()
            
            (category1 / "project1").mkdir()
            (category1 / "project2").mkdir()
            (category2 / "project3").mkdir()
            (temp_projects_dir / ".hidden").mkdir()  # Should be ignored
            (category1 / ".hidden-project").mkdir()  # Should be ignored
            
            projects = get_existing_projects()
            project_names = [name for name, _ in projects]
            assert "project1" in project_names
            assert "project2" in project_names
            assert "project3" in project_names
            assert ".hidden" not in project_names
            assert ".hidden-project" not in project_names
    
    def test_sorted_results(self, temp_projects_dir):
        with patch('ai.PROJECTS_DIR', temp_projects_dir):
            category = temp_projects_dir / "category"
            category.mkdir()
            (category / "zebra").mkdir()
            (category / "alpha").mkdir()
            (category / "beta").mkdir()
            
            projects = get_existing_projects()
            project_names = [name for name, _ in projects]
            assert project_names == ["alpha", "beta", "zebra"]
    
    def test_returns_tuples(self, temp_projects_dir):
        with patch('ai.PROJECTS_DIR', temp_projects_dir):
            category = temp_projects_dir / "category"
            category.mkdir()
            (category / "test-project").mkdir()
            
            projects = get_existing_projects()
            assert len(projects) == 1
            name, path = projects[0]
            assert name == "test-project"
            assert path == category / "test-project"


class TestFuzzyMatchProject:
    """Tests for fuzzy_match_project function."""
    
    def test_exact_match(self, temp_projects_dir):
        category = temp_projects_dir / "category"
        category.mkdir()
        projects = [
            ("local-ai", category / "local-ai"),
            ("voice-audit", category / "voice-audit"),
            ("credit-agent", category / "credit-agent")
        ]
        match_path, match_name, score, top_5 = fuzzy_match_project("local ai", projects)
        assert match_name == "local-ai"
        assert match_path == category / "local-ai"
        assert score >= CONFIDENCE_THRESHOLD
    
    def test_close_match(self, temp_projects_dir):
        category = temp_projects_dir / "category"
        category.mkdir()
        projects = [
            ("local-ai", category / "local-ai"),
            ("voice-audit", category / "voice-audit"),
            ("credit-agent", category / "credit-agent")
        ]
        match_path, match_name, score, top_5 = fuzzy_match_project("local", projects)
        assert match_name == "local-ai"
        assert match_path == category / "local-ai"
        assert score >= CONFIDENCE_THRESHOLD
    
    def test_poor_match(self, temp_projects_dir):
        category = temp_projects_dir / "category"
        category.mkdir()
        projects = [
            ("local-ai", category / "local-ai"),
            ("voice-audit", category / "voice-audit"),
            ("credit-agent", category / "credit-agent")
        ]
        match_path, match_name, score, top_5 = fuzzy_match_project("completely different", projects)
        # Should return something, but score might be low
        assert isinstance(top_5, list)
        assert len(top_5) <= 5
    
    def test_empty_projects(self):
        match_path, match_name, score, top_5 = fuzzy_match_project("anything", [])
        assert match_path is None
        assert match_name is None
        assert score == 0
        assert top_5 == []
    
    def test_top_5_results(self, temp_projects_dir):
        category = temp_projects_dir / "category"
        category.mkdir()
        projects = [(f"project-{i}", category / f"project-{i}") for i in range(10)]
        match_path, match_name, score, top_5 = fuzzy_match_project("project", projects)
        assert len(top_5) <= 5


class TestOpenInCursor:
    """Tests for open_in_cursor function."""
    
    @patch('subprocess.run')
    def test_success(self, mock_run, temp_projects_dir):
        test_path = temp_projects_dir / "test-project"
        test_path.mkdir()
        
        mock_run.return_value = subprocess.CompletedProcess(
            args=["cursor", str(test_path)],
            returncode=0
        )
        result = open_in_cursor(test_path)
        assert result == True
        mock_run.assert_called_once()
    
    @patch('subprocess.run')
    def test_path_not_exists(self, mock_run, temp_projects_dir):
        test_path = temp_projects_dir / "nonexistent"
        result = open_in_cursor(test_path)
        assert result == False
        mock_run.assert_not_called()
    
    @patch('subprocess.run')
    def test_cursor_not_found(self, mock_run, temp_projects_dir):
        test_path = temp_projects_dir / "test-project"
        test_path.mkdir()
        
        mock_run.side_effect = FileNotFoundError()
        result = open_in_cursor(test_path)
        assert result == False
    
    @patch('subprocess.run')
    def test_subprocess_error(self, mock_run, temp_projects_dir):
        test_path = temp_projects_dir / "test-project"
        test_path.mkdir()
        
        mock_run.side_effect = subprocess.CalledProcessError(1, "cursor")
        result = open_in_cursor(test_path)
        assert result == False


class TestCreateProject:
    """Tests for create_project function."""
    
    @patch('subprocess.run')
    def test_create_project_success(self, mock_run, temp_projects_dir):
        with patch('ai.PROJECTS_DIR', temp_projects_dir):
            mock_run.return_value = subprocess.CompletedProcess(
                args=["git", "init"],
                returncode=0
            )
            
            project_path = create_project("test-project")
            
            assert project_path.exists()
            assert (project_path / "README.md").exists()
            assert project_path.name == "test-project"
            assert project_path.parent.name == "NotFinishedYet"
            
            # Check README content
            readme_content = (project_path / "README.md").read_text()
            assert "# test-project" in readme_content
    
    @patch('subprocess.run')
    def test_git_init_called(self, mock_run, temp_projects_dir):
        with patch('ai.PROJECTS_DIR', temp_projects_dir):
            mock_run.return_value = subprocess.CompletedProcess(
                args=["git", "init"],
                returncode=0
            )
            
            project_path = create_project("test-project")
            
            # Check git init was called
            git_calls = [call for call in mock_run.call_args_list 
                        if len(call[0][0]) > 0 and call[0][0][0] == "git"]
            assert len(git_calls) > 0
    
    @patch('subprocess.run')
    def test_existing_project(self, mock_run, temp_projects_dir):
        with patch('ai.PROJECTS_DIR', temp_projects_dir):
            project_path = temp_projects_dir / "NotFinishedYet" / "existing-project"
            project_path.mkdir(parents=True, exist_ok=True)
            
            mock_run.return_value = subprocess.CompletedProcess(
                args=["git", "init"],
                returncode=0
            )
            result_path = create_project("existing-project")
            
            assert result_path == project_path


class TestCLI:
    """Integration tests for the CLI."""
    
    @patch('ai.open_in_cursor')
    @patch('ai.create_project')
    def test_create_command(self, mock_create, mock_open, runner, temp_projects_dir):
        with patch('ai.PROJECTS_DIR', temp_projects_dir):
            test_path = temp_projects_dir / "test-project"
            test_path.mkdir()
            mock_create.return_value = test_path
            mock_open.return_value = True
            
            result = runner.invoke(app, ["create a project called test-project"])
            
            assert result.exit_code == 0
            assert "Creating" in result.stdout or "Opening" in result.stdout
    
    @patch('ai.open_in_cursor')
    @patch('ai.get_existing_projects')
    @patch('ai.fuzzy_match_project')
    def test_open_command_high_confidence(self, mock_match, mock_get_projects, mock_open, 
                                          runner, temp_projects_dir):
        with patch('ai.PROJECTS_DIR', temp_projects_dir):
            category = temp_projects_dir / "category"
            category.mkdir()
            mock_get_projects.return_value = [
                ("local-ai", category / "local-ai"),
                ("voice-audit", category / "voice-audit")
            ]
            mock_match.return_value = (category / "local-ai", "local-ai", 85, [("local-ai", 85)])
            mock_open.return_value = True
            
            result = runner.invoke(app, ["open local ai"])
            
            assert result.exit_code == 0
            assert "Opening" in result.stdout or "Opened" in result.stdout
    
    @patch('ai.get_existing_projects')
    @patch('ai.fuzzy_match_project')
    def test_open_command_low_confidence(self, mock_match, mock_get_projects, 
                                        runner, temp_projects_dir):
        with patch('ai.PROJECTS_DIR', temp_projects_dir):
            category = temp_projects_dir / "category"
            category.mkdir()
            mock_get_projects.return_value = [
                ("local-ai", category / "local-ai"),
                ("voice-audit", category / "voice-audit")
            ]
            mock_match.return_value = (category / "local-ai", "local-ai", 30, [("local-ai", 30), ("voice-audit", 25)])
            
            result = runner.invoke(app, ["open something unclear"])
            
            assert result.exit_code == 0
            assert "Not confident" in result.stdout or "matches" in result.stdout
    
    def test_no_projects_found(self, runner, temp_projects_dir):
        with patch('ai.PROJECTS_DIR', temp_projects_dir):
            with patch('ai.get_existing_projects', return_value=[]):
                result = runner.invoke(app, ["open anything"])
                
                assert result.exit_code == 1
                assert "No projects found" in result.stdout
    
    def test_extract_name_failure(self, runner, temp_projects_dir):
        with patch('ai.PROJECTS_DIR', temp_projects_dir):
            with patch('ai.extract_project_name', return_value=None):
                result = runner.invoke(app, ["create a project"])
                
                assert result.exit_code == 1
                assert "Could not extract" in result.stdout


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

