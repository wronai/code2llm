"""Entry point for running code2llm as a module."""

# Suppress stderr at OS level immediately to avoid syntax error messages from C parser
# This must happen BEFORE any imports that might trigger file parsing
import os
if os.name != 'nt':  # Unix-like systems
    _code2llm_main_null_fd = os.open(os.devnull, os.O_WRONLY)
    _code2llm_main_old_stderr_fd = os.dup(2)
    os.dup2(_code2llm_main_null_fd, 2)

from .cli import main

# Restore stderr after imports
if os.name != 'nt' and '_code2llm_main_old_stderr_fd' in globals():
    os.dup2(_code2llm_main_old_stderr_fd, 2)
    os.close(_code2llm_main_null_fd)
    os.close(_code2llm_main_old_stderr_fd)

if __name__ == '__main__':
    main()
