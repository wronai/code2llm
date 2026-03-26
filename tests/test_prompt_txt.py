"""Tests for prompt.txt generation functionality."""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

from code2llm.cli import _export_prompt_txt, _export_code2logic


class TestPromptTxtGeneration:
    """Test the _export_prompt_txt function that generates prompt.txt for LLM."""
    
    @pytest.fixture
    def temp_output_dir(self):
        """Create temporary output directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def mock_args(self):
        """Create mock args object with verbose flag."""
        args = MagicMock()
        args.verbose = True
        return args
    
    def test_prompt_txt_not_generated_without_code2logic_format(self, temp_output_dir, mock_args):
        """Test that prompt.txt is NOT generated when code2logic is not in formats."""
        formats = ['toon', 'evolution']
        source_path = Path('/home/user/myproject')
        
        _export_prompt_txt(mock_args, temp_output_dir, formats, source_path)
        
        prompt_file = temp_output_dir / 'prompt.txt'
        assert not prompt_file.exists(), "prompt.txt should not be generated without code2logic format"
    
    def test_prompt_txt_generated_with_code2logic_format(self, temp_output_dir, mock_args):
        """Test that prompt.txt IS generated when code2logic is in formats."""
        formats = ['toon', 'evolution', 'code2logic']
        source_path = Path('/home/user/myproject')
        
        # Create some existing files
        (temp_output_dir / 'analysis.toon').write_text('test')
        (temp_output_dir / 'context.md').write_text('test')
        
        _export_prompt_txt(mock_args, temp_output_dir, formats, source_path)
        
        prompt_file = temp_output_dir / 'prompt.txt'
        assert prompt_file.exists(), "prompt.txt should be generated with code2logic format"
    
    def test_prompt_txt_generated_with_all_format(self, temp_output_dir, mock_args):
        """Test that prompt.txt IS generated when 'all' is in formats."""
        formats = ['all']
        source_path = Path('/home/user/myproject')
        
        _export_prompt_txt(mock_args, temp_output_dir, formats, source_path)
        
        prompt_file = temp_output_dir / 'prompt.txt'
        assert prompt_file.exists(), "prompt.txt should be generated with 'all' format"
    
    def test_prompt_txt_lists_existing_files(self, temp_output_dir, mock_args):
        """Test that prompt.txt correctly lists existing files with paths and descriptions."""
        formats = ['code2logic']
        source_path = Path('/home/user/myproject')
        
        # Create some files that should be detected
        expected_files = ['analysis.toon', 'context.md']
        for f in expected_files:
            (temp_output_dir / f).write_text('test content')
        
        _export_prompt_txt(mock_args, temp_output_dir, formats, source_path)
        
        prompt_file = temp_output_dir / 'prompt.txt'
        content = prompt_file.read_text()
        
        # Check that project name is shown (just folder name, not full path)
        assert "we are in project path:" in content
        assert "myproject" in content
        
        # Check that existing files are listed with paths and descriptions
        assert "Files for analysis:" in content
        for f in expected_files:
            assert f in content, f"Existing file {f} should be listed in prompt.txt"
            # Check for path format with description
            assert "- " in content, "File should be listed with bullet point"
        
        # Check that missing files are marked
        assert "Missing files" in content, "Missing files should be indicated"
        assert "map.toon.yaml" in content, "map.toon.yaml should be listed when it is missing"
    
    def test_prompt_txt_shows_missing_files(self, temp_output_dir, mock_args):
        """Test that prompt.txt shows missing files section when files don't exist."""
        formats = ['code2logic']
        source_path = Path('/home/user/myproject')
        
        # Don't create any files - all should be missing
        _export_prompt_txt(mock_args, temp_output_dir, formats, source_path)
        
        prompt_file = temp_output_dir / 'prompt.txt'
        content = prompt_file.read_text()
        
        assert "Missing files" in content, "Missing section should be present when files don't exist"
        assert "analysis.toon" in content, "Missing files should be listed"
    
    def test_prompt_txt_contains_task_instructions(self, temp_output_dir, mock_args):
        """Test that prompt.txt contains task instructions for LLM."""
        formats = ['code2logic']
        source_path = Path('/home/user/myproject')
        
        _export_prompt_txt(mock_args, temp_output_dir, formats, source_path)
        
        prompt_file = temp_output_dir / 'prompt.txt'
        content = prompt_file.read_text()
        
        # Check for key sections
        assert "You are an AI assistant" in content, "Main instruction should be present"
        assert "Task:" in content, "Task section should be present"
        assert "refactoring brief" in content, "Task section should instruct refactoring"
        assert "Priority Order:" in content, "Priority section should be present"
        assert "Constraints:" in content, "Constraints section should be present"
        assert "we are in project path:" in content, "Project path should be present"

    def test_prompt_txt_prioritizes_blockers_when_validation_and_duplication_exist(self, temp_output_dir, mock_args):
        """Test that prompt.txt orders blockers first when validation and duplication outputs exist."""
        formats = ['all']
        source_path = Path('/home/user/myproject')

        # Create the main generated files plus blocker files
        generated_files = [
            'analysis.toon',
            'map.toon.yaml',
            'evolution.toon.yaml',
            'project.toon.yaml',
            'context.md',
            'README.md',
        ]
        for f in generated_files:
            (temp_output_dir / f).write_text('test')

        (temp_output_dir / 'project').mkdir(parents=True, exist_ok=True)
        (temp_output_dir / 'project' / 'validation.toon.yaml').write_text('validation')
        (temp_output_dir / 'project' / 'duplication.toon.yaml').write_text('duplication')

        _export_prompt_txt(mock_args, temp_output_dir, formats, source_path)

        prompt_file = temp_output_dir / 'prompt.txt'
        content = prompt_file.read_text()

        assert "Priority Order:" in content, "Priority section should be present"
        assert "P0 — Fix validation issues" in content, "Validation issues should be first priority"
        assert "P0/P1 — Remove duplicated logic" in content, "Duplication issues should be prioritized next"
        assert "P1 — Split or simplify the highest-CC / god modules" in content, "Analysis-driven refactoring should follow blockers"
        assert "P2 — Keep the compact project overview" in content, "Project overview should be preserved as a later priority"

    def test_prompt_txt_content_structure(self, temp_output_dir, mock_args):
        """Test the overall structure of generated prompt.txt."""
        formats = ['code2logic']
        source_path = Path('/home/user/myproject')
        
        # Create all expected files
        all_files = ['analysis.toon', 'map.toon.yaml', 'evolution.toon.yaml', 'project.toon.yaml', 'context.md', 'README.md']
        for f in all_files:
            (temp_output_dir / f).write_text('test')
        
        _export_prompt_txt(mock_args, temp_output_dir, formats, source_path)
        
        prompt_file = temp_output_dir / 'prompt.txt'
        content = prompt_file.read_text()
        lines = content.split('\n')
        
        # Check structure
        assert any("You are an AI assistant" in line for line in lines), \
            "Prompt should start with AI assistant instruction"
        assert any("we are in project path:" in line for line in lines), \
            "Project path should be present"

        assert any("Files for analysis:" in line for line in lines), \
            "Files section should be present"

        # All files should be listed without missing section
        assert "Missing files" not in content, "No missing section when all files exist"
        for f in all_files:
            assert f in content, f"All files should be listed: {f}"

        # Check for file paths with descriptions
        assert "- " in content, "Files should be listed with bullet points"
        assert "Health diagnostics" in content, "Descriptions should be present"


class TestCode2logicExport:
    """Test the _export_code2logic wrapper."""

    @pytest.fixture
    def temp_output_dir(self):
        """Create temporary output directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    def test_export_code2logic_adds_quiet_flag_when_not_verbose(self, temp_output_dir):
        args = MagicMock()
        args.verbose = False

        source_path = Path('/home/user/myproject')
        formats = ['code2logic']

        completed = MagicMock()
        completed.returncode = 0
        completed.stdout = ""
        completed.stderr = ""

        with patch('code2llm.cli_exports.code2logic.shutil.which', return_value='/usr/bin/code2logic'), \
             patch('code2llm.cli_exports.code2logic.subprocess.run', return_value=completed) as run_mock, \
             patch('code2llm.core.toon_size_manager.manage_toon_size', return_value=[temp_output_dir / 'project.toon']), \
             patch('pathlib.Path.exists', return_value=True):
            _export_code2logic(args, source_path, temp_output_dir, formats)

        called_cmd = run_mock.call_args[0][0]
        assert '-q' in called_cmd

    def test_export_code2logic_does_not_add_quiet_flag_when_verbose(self, temp_output_dir):
        args = MagicMock()
        args.verbose = True

        source_path = Path('/home/user/myproject')
        formats = ['code2logic']

        completed = MagicMock()
        completed.returncode = 0
        completed.stdout = ""
        completed.stderr = ""

        with patch('code2llm.cli_exports.code2logic.shutil.which', return_value='/usr/bin/code2logic'), \
             patch('code2llm.cli_exports.code2logic.subprocess.run', return_value=completed) as run_mock, \
             patch('code2llm.core.toon_size_manager.manage_toon_size', return_value=[temp_output_dir / 'project.toon']), \
             patch('pathlib.Path.exists', return_value=True):
            _export_code2logic(args, source_path, temp_output_dir, formats)

        called_cmd = run_mock.call_args[0][0]
        assert '-q' not in called_cmd
    
    def test_prompt_txt_no_verbose_output(self, temp_output_dir):
        """Test that no print occurs when verbose is False."""
        args = MagicMock()
        args.verbose = False
        formats = ['code2logic']
        source_path = Path('/home/user/myproject')
        
        # Should not raise or print anything
        _export_prompt_txt(args, temp_output_dir, formats, source_path)
        
        assert (temp_output_dir / 'prompt.txt').exists()
