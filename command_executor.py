import subprocess
import sys
import re
from colorama import Fore, Style, init

init(autoreset=True)

class CommandExecutor:
    def __init__(self, config=None):
        self.config = config or {}
        # Basic destructive keywords regex
        self.destructive_patterns = [
            r"rm\s+", r"del\s+", r"rd\s+", r"rmdir\s+", 
            r"mv\s+.*-f", r"cp\s+.*-f",  # force overwrite
            r">\s+", # redirection overwrite (simple check)
            r"format\s+", r"fdisk"
        ]

    def is_destructive(self, command, llm_flag):
        if llm_flag:
            return True
        for pattern in self.destructive_patterns:
            if re.search(pattern, command, re.IGNORECASE):
                return True
        return False

    def execute(self, command_data, capture_output=False):
        if "error" in command_data:
            print(f"{Fore.RED}Error: {command_data['error']}")
            return None

        command = command_data.get("command")
        explanation = command_data.get("explanation")
        llm_is_destructive = command_data.get("is_destructive", False)

        print(f"\n{Fore.CYAN}Proposed Command: {Style.BRIGHT}{command}")
        print(f"{Fore.YELLOW}Explanation: {explanation}")

        is_dangerous = self.is_destructive(command, llm_is_destructive)

        if is_dangerous:
            print(f"\n{Fore.RED}{Style.BRIGHT}WARNING: This command is flagged as DESTRUCTIVE.")
            confirm = input(f"{Fore.RED}Are you sure you want to execute this? (type 'yes' to confirm): ").strip()
            if confirm.lower() != "yes":
                print("Aborted.")
                return None
        else:
            # Default confirmation for non-destructive commands (optional, can be configured)
            confirm = input(f"\n{Fore.GREEN}Execute this command? (Y/n): ").strip().lower()
            if confirm not in ["", "y", "yes"]:
                print("Aborted.")
                return None

        try:
            if capture_output:
                # Capture output for analysis
                result = subprocess.run(command, check=True, shell=True, capture_output=True, text=True)
                print(f"\n{Fore.GREEN}Command executed successfully.")
                return result.stdout + "\n" + result.stderr
            else:
                # Standard execution (streaming output to console)
                subprocess.run(command, check=True, shell=True)
                print(f"\n{Fore.GREEN}Command executed successfully.")
                return None
        except subprocess.CalledProcessError as e:
            print(f"\n{Fore.RED}Command failed with exit code {e.returncode}.")
            if capture_output:
                return e.stdout + "\n" + e.stderr
            return None
        except Exception as e:
             print(f"\n{Fore.RED}Execution error: {str(e)}")
             return None
