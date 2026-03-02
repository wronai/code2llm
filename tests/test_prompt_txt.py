"""Tests for prompt.txt generation functionality."""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

from code2llm.cli import _export_prompt_txt


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
        
        _export_prompt_txt(mock_args, temp_output_dir, formats)
        
        prompt_file = temp_output_dir / 'prompt.txt'
        assert not prompt_file.exists(), "prompt.txt should not be generated without code2logic format"
    
    def test_prompt_txt_generated_with_code2logic_format(self, temp_output_dir, mock_args):
        """Test that prompt.txt IS generated when code2logic is in formats."""
        formats = ['toon', 'evolution', 'code2logic']
        
        # Create some existing files
        (temp_output_dir / 'analysis.toon').write_text('test')
        (temp_output_dir / 'context.md').write_text('test')
        
        _export_prompt_txt(mock_args, temp_output_dir, formats)
        
        prompt_file = temp_output_dir / 'prompt.txt'
        assert prompt_file.exists(), "prompt.txt should be generated with code2logic format"
    
    def test_prompt_txt_generated_with_all_format(self, temp_output_dir, mock_args):
        """Test that prompt.txt IS generated when 'all' is in formats."""
        formats = ['all']
        
        _export_prompt_txt(mock_args, temp_output_dir, formats)
        
        prompt_file = temp_output_dir / 'prompt.txt'
        assert prompt_file.exists(), "prompt.txt should be generated with 'all' format"
    
    def test_prompt_txt_lists_existing_files(self, temp_output_dir, mock_args):
        """Test that prompt.txt correctly lists existing files with descriptions."""
        formats = ['code2logic']
        
        # Create some files that should be detected
        expected_files = ['analysis.toon', 'context.md']
        for f in expected_files:
            (temp_output_dir / f).write_text('test content')
        
        _export_prompt_txt(mock_args, temp_output_dir, formats)
        
        prompt_file = temp_output_dir / 'prompt.txt'
        content = prompt_file.read_text()
        
        # Check that existing files are listed with descriptions
        assert "FILES FOR ANALYSIS:" in content
        for f in expected_files:
            assert f in content, f"Existing file {f} should be listed in prompt.txt"
            # Check for description line
            assert f"PURPOSE:" in content, "Description should be present for each file"
        
        # Check that missing files are marked
        assert "MISSING FILES" in content or "project.toon" in content, "Missing files should be indicated"
    
    def test_prompt_txt_shows_missing_files(self, temp_output_dir, mock_args):
        """Test that prompt.txt shows missing files section when files don't exist."""
        formats = ['code2logic']
        
        # Don't create any files - all should be missing
        _export_prompt_txt(mock_args, temp_output_dir, formats)
        
        prompt_file = temp_output_dir / 'prompt.txt'
        content = prompt_file.read_text()
        
        assert "MISSING FILES" in content, "Missing section should be present when files don't exist"
        assert "analysis.toon" in content, "Missing files should be listed"
    
    def test_prompt_txt_contains_task_instructions(self, temp_output_dir, mock_args):
        """Test that prompt.txt contains task instructions for LLM."""
        formats = ['code2logic']
        
        _export_prompt_txt(mock_args, temp_output_dir, formats)
        
        prompt_file = temp_output_dir / 'prompt.txt'
        content = prompt_file.read_text()
        
        # Check for key sections in English
        assert "TASK FOR LLM:" in content, "Task section should be present"
        assert "REQUIREMENTS:" in content, "Requirements section should be present"
        assert "Analyze the attached files" in content, "Main instruction should be present"
    
    def test_prompt_txt_content_structure(self, temp_output_dir, mock_args):
        """Test the overall structure of generated prompt.txt."""
        formats = ['code2logic']
        
        # Create all expected files
        all_files = ['analysis.toon', 'context.md', 'evolution.toon', 'project.toon', 'README.md']
        for f in all_files:
            (temp_output_dir / f).write_text('test')
        
        _export_prompt_txt(mock_args, temp_output_dir, formats)
        
        prompt_file = temp_output_dir / 'prompt.txt'
        content = prompt_file.read_text()
        lines = content.split('\n')
        
        # Check structure in English
        assert any("Analyze the attached files" in line for line in lines), \
            "Prompt should start with English instruction"
        assert any("FILES FOR ANALYSIS:" in line for line in lines), \
            "Files section should be present in English"
        
        # All files should be listed without missing section
        assert "MISSING FILES" not in content, "No missing section when all files exist"
        for f in all_files:
            assert f in content, f"All files should be listed: {f}"
        
        # Check for descriptions
        assert "PURPOSE:" in content, "Descriptions should be present"
    
    def test_prompt_txt_no_verbose_output(self, temp_output_dir):
        """Test that no print occurs when verbose is False."""
        args = MagicMock()
        args.verbose = False
        formats = ['code2logic']
        
        # Should not raise or print anything
        _export_prompt_txt(args, temp_output_dir, formats)
        
        assert (temp_output_dir / 'prompt.txt').exists()
