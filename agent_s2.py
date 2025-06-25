#!/usr/bin/env python3

import os
import io
import sys
import time
from dotenv import load_dotenv
from gui_agents.s2.agents.agent_s import AgentS2
from gui_agents.s2.agents.grounding import OSWorldACI
from orgo import Computer
import pyautogui

load_dotenv()

CONFIG = {
    "model": os.getenv("AGENT_MODEL", "gpt-4o"),
    "model_type": os.getenv("AGENT_MODEL_TYPE", "openai"),
    "grounding_model": os.getenv("GROUNDING_MODEL", "claude-3-7-sonnet-20250219"),
    "grounding_type": os.getenv("GROUNDING_MODEL_TYPE", "anthropic"),
    "search_engine": os.getenv("SEARCH_ENGINE", "Perplexica"),
    "embedding_type": os.getenv("EMBEDDING_TYPE", "openai"),
    "max_steps": int(os.getenv("MAX_STEPS", "10")),
    "step_delay": float(os.getenv("STEP_DELAY", "0.5")),
    "remote": os.getenv("USE_CLOUD_ENVIRONMENT", "false").lower() == "true"
}


class LocalExecutor:
    def __init__(self):
        self.pyautogui = pyautogui
        if sys.platform == "win32":
            self.platform = "windows"
        elif sys.platform == "darwin":
            self.platform = "darwin"
        else:
            self.platform = "linux"
    
    def screenshot(self):
        img = self.pyautogui.screenshot()
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        return buffer.getvalue()
    
    def exec(self, code):
        exec(code, {"pyautogui": self.pyautogui, "time": time})


class RemoteExecutor:
    def __init__(self):
        self.computer = Computer()
        self.platform = "linux"
    
    def screenshot(self):
        return self.computer.screenshot_base64()
    
    def exec(self, code):
        result = self.computer.exec(code)
        if not result['success']:
            raise Exception(result.get('error', 'Execution failed'))
        if result['output']:
            print(f"Output: {result['output']}")


def create_agent(executor):
    engine_params = {"engine_type": CONFIG["model_type"], "model": CONFIG["model"]}
    grounding_params = {"engine_type": CONFIG["grounding_type"], "model": CONFIG["grounding_model"]}
    
    grounding_agent = OSWorldACI(
        platform=executor.platform,
        engine_params_for_generation=engine_params,
        engine_params_for_grounding=grounding_params
    )
    
    return AgentS2(
        engine_params=engine_params,
        grounding_agent=grounding_agent,
        platform=executor.platform,
        action_space="pyautogui",
        observation_type="screenshot",
        search_engine=CONFIG["search_engine"] if CONFIG["search_engine"] != "none" else None,
        embedding_engine_type=CONFIG["embedding_type"]
    )


def run_task(agent, executor, instruction):
    print(f"\n🤖 Task: {instruction}")
    print(f"📍 Mode: {'Remote' if CONFIG['remote'] else 'Local'}\n")
    
    for step in range(CONFIG["max_steps"]):
        print(f"Step {step + 1}/{CONFIG['max_steps']}")
        
        obs = {"screenshot": executor.screenshot()}
        info, action = agent.predict(instruction=instruction, observation=obs)
        
        if info:
            print(f"💭 {info}")
        
        if not action or not action[0]:
            print("✅ Complete")
            return True
        
        try:
            print(f"🔧 {action[0]}")
            executor.exec(action[0])
        except Exception as e:
            print(f"❌ Error: {e}")
            instruction = "The previous action failed. Try a different approach."
        
        time.sleep(CONFIG["step_delay"])
    
    print("⏱️ Max steps reached")
    return False


def main():
    executor = RemoteExecutor() if CONFIG["remote"] else LocalExecutor()
    print(f"💻 Using {executor.__class__.__name__}")
    agent = create_agent(executor)
    
    if len(sys.argv) > 1:
        run_task(agent, executor, " ".join(sys.argv[1:]))
    else:
        print("🎮 Interactive Mode (type 'exit' to quit)\n")
        while True:
            task = input("Task: ").strip()
            if task == "exit":
                break
            elif task:
                run_task(agent, executor, task)


if __name__ == "__main__":
    main()