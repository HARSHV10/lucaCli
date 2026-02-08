import pytest
from command_executor import CommandExecutor

def test_destructive_commands():
    executor = CommandExecutor()
    
    destructive_cmds = [
        "rm -rf /",
        "del system32",
        "rd /s /q folder",
        "mv file.txt /dev/null -f",
        "format c:", 
        "echo 'hello' > existing_file.txt" 
    ]
    
    for cmd in destructive_cmds:
        assert executor.is_destructive(cmd, False) == True, f"Failed to detect destructive command: {cmd}"

def test_safe_commands():
    executor = CommandExecutor()
    
    safe_cmds = [
        "ls -la",
        "dir",
        "mkdir new_folder",
        "echo 'hello'",
        "python script.py",
        "git status"
    ]
    
    for cmd in safe_cmds:
        assert executor.is_destructive(cmd, False) == False, f"Falsely flagged safe command: {cmd}"

def test_llm_flag():
    executor = CommandExecutor()
    # Even if command looks safe, if LLM says it's destructive, trust LLM
    assert executor.is_destructive("ls -la", True) == True
