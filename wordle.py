import os, io, sys, time, pyautogui

from gui_agents.s2_5.agents.agent_s import AgentS2_5
from gui_agents.s2_5.agents.grounding import OSWorldACI
from orgo import Computer
from dotenv import load_dotenv
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.progress import track
from rich import box

console = Console()
load_dotenv()


CONFIG = {
    "model": os.getenv("AGENT_MODEL", ""),
    "model_type": os.getenv("AGENT_MODEL_TYPE", ""),
    "grounding_model": os.getenv("GROUNDING_MODEL", ""),
    "grounding_type": os.getenv("GROUNDING_MODEL_TYPE", ""),
    "max_steps": int(os.getenv("MAX_STEPS", "50")),
    "step_delay": float(os.getenv("STEP_DELAY", "3.0")),
    "remote": os.getenv("USE_CLOUD_ENVIRONMENT", "false").lower() == "true"
}


class Executor:
    def __init__(self, remote=False):
        self.remote = remote
        if remote:
            self.computer = Computer()
            self.platform = "linux"
        else:
            self.pyautogui = pyautogui
            self.platform = {"win32": "windows", "darwin": "darwin"}.get(sys.platform, "linux")
    
    def screenshot(self):
        img = self.computer.screenshot() if self.remote else self.pyautogui.screenshot()
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        return buffer.getvalue()
    
    def exec(self, code):
        if self.remote:
            result = self.computer.exec(code)
            if not result.get('success', True):
                raise Exception(result.get('error', 'Execution failed'))
            #if output := result.get('output', '').strip():
                #print(f"📤 {output}")
        else:
            exec(code, {"pyautogui": self.pyautogui, "time": time})


def create_agent(executor):
    params = {"engine_type": CONFIG["model_type"], "model": CONFIG["model"]}
    grounding_model_resize_width = 1366 #For anthropic models
    screen_width = 1024 #For Orgo VM
    screen_height = 768 #For Orgo VM
    grounding = {
        "engine_type": CONFIG["grounding_type"], 
        "model": CONFIG["grounding_model"],
        "grounding_width": grounding_model_resize_width,
        "grounding_height": (screen_height * grounding_model_resize_width) / screen_width
    }
    
    return AgentS2_5(
        engine_params=params,
        grounding_agent=OSWorldACI(executor.platform, params, grounding),
        platform=executor.platform,
    )

def run_task(agent, executor, instruction):
    console.print(Panel(f"[bold cyan]GAME STARTS", box=box.ROUNDED))
    done_count = 0

    for step in range(CONFIG["max_steps"]):
        console.print(f"[bold blue]Step {step + 1}/{CONFIG['max_steps']}[/]")
        
        if not done_count : console.print("[yellow]⏳ Guessing better than you...[/]")
        if step: time.sleep(CONFIG["step_delay"])

        try:
            info, action = agent.predict(instruction=instruction, observation={"screenshot": executor.screenshot()})
            #if info:
             #   console.print(f"[italic green]💭 Thought:[/] {info}")

            if not action or not action[0] or action[0].strip().upper() == "DONE":
                done_count += 1
                if done_count >= 2:
                    console.print("[bold green]✅ Complete![/]")
                    return True
                continue

            done_count = 0
            console.print(f"[bold magenta]🔧 Agent Action:[/] {action[0]}")
            executor.exec(action[0])

        except Exception as e:
            console.print(f"[bold red]❌ Error:[/] {e}")
            done_count = 0

    console.print("[bold red]⏱️ Max steps reached[/]")
    return False

def main():
    console.clear()
    console.rule("[bold green]🧠 Wordle Agent CLI — S2.5 GUI Edition")
    console.print("Press [bold yellow]Ctrl+C[/] or type [bold red]'exit'[/] to quit.\n")

    try:
        executor = Executor(CONFIG["remote"])
        agent = create_agent(executor)

        if len(sys.argv) > 1:
            sys.exit(0 if run_task(agent, executor, " ".join(sys.argv[1:])) else 1)

        while True:
            task = Prompt.ask("[bold cyan]👉 Wanna try first or should I play?")
            if task.strip().lower() == "exit":
                break
            if task:
                run_task(agent, executor, task)

    except KeyboardInterrupt:
        console.print("\n[bold red]⚠️ Either you play or let me![/]")
    except Exception as e:
        console.print(f"[bold red]❌ Fatal error:[/] {e}")
        sys.exit(1)
   

if __name__ == "__main__":
    main()