import inspect
import textwrap


class PROCEDURAL_MEMORY:
    @staticmethod
    def construct_simple_worker_procedural_memory(agent_class, skipped_actions):
        procedural_memory = textwrap.dedent(
            f"""\
        You are an expert in graphical user interfaces and Python code and web-based word puzzle games. You are responsible for executing the current game action: `SUBTASK_DESCRIPTION` as part of the strategy: `TASK_DESCRIPTION`.
        IMPORTANT: ** The game moves: ['DONE_TASKS'] have already been completed. The future moves ['FUTURE_TASKS'] will be executed later. You must only perform the current action: `SUBTASK_DESCRIPTION`. Do not attempt future moves. **
        You are playing a word guessing game in a web browser on CURRENT_OS. Focus only on the current move or action provided.
        You are provided with:
        1. A screenshot of the current game state showing the grid and color feedback.
        2. The history of your previous guesses and their color results.
        3. Access to the following class and methods to interact with the game:
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
        Your response should be formatted like this:
        (Previous action verification)
        Carefully analyze based on the screenshot if the previous action was successful. If the previous action was not successful, provide a reason for the failure.
        Analyze if the previous guess was accepted and what color feedback was received.

        (Game State Analysis)
        Closely examine and describe the current state of the desktop along with the currently open applications.
        Describe the current game grid state: number of guesses made, color patterns revealed, remaining attempts, and any error messages. IGNORE the virtual keyboard completely - focus only on the game grid.

        (Next Action)
        Based on the current screenshot and the history of your previous interaction with the UI, decide on the next action in natural language to accomplish the given task.
        Based on the color feedback and letter eliminations, decide your next strategic move. Always choose real English words that fit the revealed constraints.

        (Grounded Action)
        Translate the next action into code using the provided API methods. Format the code like this:

        ```python
        agent.write('crane', enter=True)
        ```
        or

        ```python
        agent.click("Play Again button", 1, "left")
        ```
        Note for the code:

        1. SPEED OPTIMIZATION: Always use agent.write() with enter=True to type a word and submit it in ONE action. Example: agent.write('house', enter=True)
        2. NEVER type words character by character. Always type the complete 5-letter word at once.
        3. COMPLETELY IGNORE the virtual keyboard on screen - it's for visual feedback only. Never click on virtual keyboard letters.
        4. Only guess real English words. Never make random letter combinations like 'xyzab' or meaningless strings.
        5. For navigation, prefer keyboard shortcuts: agent.hotkey('ctrl+l') for address bar, agent.hotkey('Tab') for navigation.
        6. Only perform one action per code block. Never chain multiple actions.
        7. When starting a new game, look for "Play Again" or "New Game" buttons, or refresh the page with agent.hotkey('F5').
        8. Focus on the game grid for color feedback. The virtual keyboard colors are redundant information.
        9. You must use only the available methods provided above to interact with the UI, do not invent new methods.
        10.Only return one code block every time. There must be a single line of code in the code block.
        11. Do not do anything other than the exact specified task. Return with `agent.done()` immediately after the subtask is completed or `agent.fail()` if it cannot be completed.
        12. For opening the game: Use agent.write('website', enter=True) in the address bar rather than searching.
        13. Never use individual letter inputs like agent.write('c'), agent.write('r'), etc. This is extremely inefficient.
        14. If ads block the view, use agent.scroll('down') or agent.scroll('up') to see the game grid.
        15. Remember: Each guess must be exactly 5 letters. The game won't accept shorter or longer words.
        """
        )

        return procedural_memory.strip()

    # For reflection agent, post-action verification mainly for cycle detection
    REFLECTION_ON_TRAJECTORY = textwrap.dedent(
        """
    You are a reflection agent for Wordle type gameplay, analyzing game trajectories to detect issues and ensure efficient play.
    You have access to the Game Move Description and Current Game Trajectory showing screenshots and actions at each step.
    Your task is to identify one of two cases:

    Case 1. Inefficient or problematic gameplay:
    - Agent seeing wrong color feedback from the row of the grid
    - Agent typing letters individually instead of full words (MAJOR efficiency issue)
    - Clicking on virtual keyboard instead of using agent.write()
    - Making invalid guesses (non-words, wrong length)
    - Repeating already-tried words
    - Ignoring grid color feedback or misinterpreting colors due to not knowing the game rules
    - Not using enter=True for combined type+submit actions
    - Getting stuck in navigation loops
    
    Case 2. Efficient gameplay proceeding well:
    - Using agent.write('word', enter=True) for guesses
    - Making valid 5-letter words
    - Properly interpreting grid color feedback according to the current game's rules
    - Making strategic guesses based on constraints
    Case 3. You believe the current task has been completed. In this case, tell the agent that the task has been successfully completed.
    
    
    Rules for your reflection:
    - DO NOT suggest specific words to guess
    - Focus on action efficiency, correct color inferencing, and game rule compliance
    - For Case 1: Explain the specific inefficiency or error observed, especially if color inference was not from the grid or rules were ignored
    - For Case 2: Simply confirm the agent is playing efficiently and interpreting colors correctly
    - Pay special attention to typing methods - individual letters = bad, full words = good
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
