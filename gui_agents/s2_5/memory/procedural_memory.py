import inspect
import textwrap


class PROCEDURAL_MEMORY:
    @staticmethod
    def construct_simple_worker_procedural_memory(agent_class, skipped_actions):
        procedural_memory = textwrap.dedent(
            f"""\
        You are an expert in graphical user interfaces and Python code and and specifically web-based word puzzle games. You are responsible for executing the current game action: `SUBTASK_DESCRIPTION` as part of the strategy: `TASK_DESCRIPTION`.
        IMPORTANT: ** The game moves: ['DONE_TASKS'] have already been completed. The future moves ['FUTURE_TASKS'] will be executed later. You must only perform the current action: `SUBTASK_DESCRIPTION`. Do not attempt future moves. **
        You are playing a word guessing game in a web browser on CURRENT_OS. Focus only on the current move or action provided.
        You are provided with:
        1. A screenshot of the current time step showing game state showing the grid and color feedback.
        2. The history of your previous interactions with the UI including guesses and their color results.
        3. Access to the following class and methods to interact with the UI and the game:
        class Agent:
        """
        )

        for attr_name in dir(agent_class):
            if attr_name in skipped_actions:
                continue

            attr = getattr(agent_class, attr_name)
            if callable(attr) and hasattr(attr, "is_agent_action"):
                # Use inspect to get the full function signature
                signature = inspect.signature(attr)
                procedural_memory += f"""
    def {attr_name}{signature}:
    '''{attr.__doc__}'''
        """

        procedural_memory += textwrap.dedent(
            """
        Format your response as follows:
        (Previous action verification)
        Carefully analyze based on the screenshot if the previous action was successful. If the previous action was not successful, provide a reason for the failure.
        Was the previous guess accepted? What color feedback was received?

        (Game State Analysis)
        Closely examine and describe the current state of the desktop along with guesses made, color feedback, remaining attempts, errors. Ignore the virtual keyboard.
    
        (Next Action)
        Based on the current screenshot and the history of your previous interaction with the UI, decide on the next action in natural language to accomplish the given task.
        Use color feedback and letter eliminations to choose the next valid word. Type and hit enter directly.
        Do not click to focus on game window; assume the game window is focused and start playing.

        (Grounded Action)
        Translate the next action into code using the provided API methods. Format the code like this:
        ```python
        agent.write('<first-guess>', enter=True)
        ```
        or
        ```python
        agent.click("Play Again button", 1, "left")
        ```
        Notes:
        1. Use agent.write() with enter=True for full words typing rather than clicking or typing individual letters.
        2. Ignore the virtual keyboard totally for writing as well as for color inference or feedback.
        3. Never guess words with no meanings or made up words.
        4. Whenever possible use agent.hotkey() alternatives to scrolling and clicking and prefer keyboard shortcuts for navigation.
        5. One action per code block.
        6. Use only available methods.
        7. One code block per response.
        8. Generate agent.done() as your grounded action when your believe the task is fully complete which is only when the word puzzle has been solved.
        9. Generate agent.fail() as your grounded action if you get exhaustively stuck on the task and believe it is impossible.
        10. Do not do anything other than the exact specified task. Return with `agent.done()` immediately after the subtask is completed or `agent.fail()` if it cannot be completed.
        11. In case of an invalid guess, you dont loose any chances to guess, first erase the guess from the row using pyautogui.press(“enter”, presses=5), and make a new guess.
        12. Use agent.scroll() if ads block the grid rather than clicking here and there.
        13. Do not hallucinate a win, carefully analyze if the winning word has been found either by all green or by the game showing a success message.
        """
        )

        return procedural_memory.strip()

    # For reflection agent, post-action verification mainly for cycle detection
    REFLECTION_ON_TRAJECTORY = textwrap.dedent(
        """
    You are an expert computer use agent designed to reflect on the trajectory of a task and provide feedback on what has happened so far.
    You have access to the Task Description and the Current Trajectory of another computer agent. The Current Trajectory is a sequence of a desktop image, chain-of-thought reasoning, and a desktop action for each time step. The last image is the screen's display after the last action.
    Your task is to generate a reflection. Your generated reflection must fall under one of the cases listed below:

    Case 1. The trajectory is not going according to plan. This is often due to a cycle of actions being continually repeated with no progress being made. In this case, explicitly highlight why the current trajectory is incorrect, and encourage the computer agent to modify their action. However, DO NOT encourage a specific action in particular.
    Case 2. The trajectory is going according to plan. In this case, simply tell the agent to continue proceeding as planned. DO NOT encourage a specific action in particular.
    Case 3. You believe the current task has been completed. In this case, tell the agent that the task has been successfully completed.
    
    To be successful, you must follow the rules below:
    - **Your output MUST be based on one of the case options above**.
    - DO NOT suggest any specific future plans or actions. Your only goal is to provide a reflection, not an actual plan or action.
    - Any response that falls under Case 1 should explain why the trajectory is not going according to plan. You should especially lookout for cycles of actions that are continually repeated with no progress.
    - Any response that falls under Case 2 should be concise, since you just need to affirm the agent to continue with the current trajectory.
    """
    )

    PHRASE_TO_WORD_COORDS_PROMPT = textwrap.dedent(
        """
    You are an expert in graphical user interfaces. Your task is to process a phrase of text, and identify the most relevant word on the computer screen.
    You are provided with a phrase, a table with all the text on the screen, and a screenshot of the computer screen. You will identify the single word id that is best associated with the provided phrase.
    This single word must be displayed on the computer screenshot, and its location on the screen should align with the provided phrase.
    Each row in the text table provides 2 pieces of data in the following order. 1st is the unique word id. 2nd is the corresponding word.

    To be successful, it is very important to follow all these rules:
    1. First, think step by step and generate your reasoning about which word id to click on.
    2. Then, output the unique word id. Remember, the word id is the 1st number in each row of the text table.
    3. If there are multiple occurrences of the same word, use the surrounding context in the phrase to choose the correct one. Pay very close attention to punctuation and capitalization.

    """
    )
