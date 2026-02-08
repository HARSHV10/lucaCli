import click
import sys
from config_manager import ConfigManager
from llm_engine import LLMEngine
from command_executor import CommandExecutor
from colorama import Fore, Style, init

init(autoreset=True)

@click.group(invoke_without_command=True)
@click.pass_context
@click.option("--setup", is_flag=True, help="Run the configuration wizard.")
@click.argument("prompt", required=False, nargs=-1)
def cli(ctx, setup, prompt):
    """LucaCli - A natural language CLI helper used to generate shell commands."""
    
    config_manager = ConfigManager()

    if setup:
        run_setup(config_manager)
        return

    # If no command and no prompt, show help
    if not prompt and ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())
        return

    # If subcommands are invoked (if any in future), let them run
    if ctx.invoked_subcommand:
        return

    # Main execution flow
    config = config_manager.load_config()
    if not config:
        click.echo(f"{Fore.RED}Configuration not found. Please run 'luca --setup' first.")
        return

    full_prompt = " ".join(prompt)
    if not full_prompt:
        click.echo(f"{Fore.YELLOW}Please provide a prompt.")
        return

    click.echo(f"{Fore.BLUE}Thinking...")
    
    try:
        import platform
        os_name = platform.system()
        engine = LLMEngine(config)
        command_data = engine.generate_command(full_prompt, os_name=os_name)

        mode = command_data.get("mode", "execute")
        
        if mode == "direct":
            explanation = command_data.get("explanation")
            click.echo(f"\n{Fore.GREEN}{Style.BRIGHT}Answer:{Style.RESET_ALL}\n{explanation}")
            return

        capture = (mode == "query")
        
        executor = CommandExecutor(config)
        result = executor.execute(command_data, capture_output=capture)

        if mode == "query" and result:
            click.echo(f"{Fore.BLUE}Analyzing result...")
            answer = engine.analyze_output(full_prompt, result, os_name=os_name)
            click.echo(f"\n{Fore.GREEN}{Style.BRIGHT}Answer:{Style.RESET_ALL}\n{answer}")

    except Exception as e:
        click.echo(f"{Fore.RED}An error occurred: {e}")

def run_setup(config_manager):
    click.echo(f"{Fore.GREEN}Welcome to LucaCli Setup!{Style.RESET_ALL}")
    
    provider = click.prompt("Choose LLM provider (ollama/openai/anthropic/gemini)", default="ollama").lower()
    
    config = {"provider": provider}
    
    if provider == "ollama":
        config["api_base"] = click.prompt("Ollama User URL", default="http://localhost:11434")
        config["model"] = click.prompt("Ollama Model", default="llama3")
    elif provider == "openai":
        config["api_key"] = click.prompt("OpenAI API Key", hide_input=True)
        config["model"] = click.prompt("OpenAI Model", default="gpt-4o")
    elif provider == "anthropic":
        config["api_key"] = click.prompt("Anthropic API Key", hide_input=True)
        config["model"] = click.prompt("Anthropic Model", default="claude-3-opus-20240229")
    elif provider == "gemini":
        config["api_key"] = click.prompt("Gemini API Key", hide_input=True)
        config["model"] = click.prompt("Gemini Model", default="gemini-1.5-flash")
    else:
        click.echo(f"{Fore.RED}Invalid provider. Setup aborted.")
        return

    config_manager.save_config(config)
    click.echo(f"{Fore.GREEN}Configuration saved successfully!")

if __name__ == "__main__":
    cli()
