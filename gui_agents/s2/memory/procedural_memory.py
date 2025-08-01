import inspect
import textwrap


class PROCEDURAL_MEMORY:

    @staticmethod
    def construct_worker_procedural_memory(agent_class, skipped_actions):
        procedural_memory = textwrap.dedent(
            f"""\
        You are an expert in web-based word puzzle games. You are responsible for executing the current game action: `SUBTASK_DESCRIPTION` as part of the strategy: `TASK_DESCRIPTION`.
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
        Analyze if the previous guess was accepted and what color feedback was received.

        (Game State Analysis)
        Describe the current game grid state: number of guesses made, color patterns revealed, remaining attempts, and any error messages. IGNORE the virtual keyboard completely - focus only on the game grid.

        (Next Action)
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
        9. If the game input field isn't focused, click on it first before typing: agent.click("game input area", 1, "left")
        10. If you've won (all green) or lost (6 failed attempts), return `agent.done()`.
        11. If the game page fails to load or crashes, return `agent.fail()`.
        12. For opening the game: Use agent.write('website', enter=True) in the address bar rather than searching.
        13. Never use individual letter inputs like agent.write('c'), agent.write('r'), etc. This is extremely inefficient.
        14. If ads block the view, use agent.scroll('down') or agent.scroll('up') to see the game grid.
        15. Remember: Each guess must be exactly 5 letters. The game won't accept shorter or longer words.
        """
        )

        return procedural_memory.strip()

    # Manager prompt that generalizes to initial planning, re-planning after subtask completion, and re-planning after failure
    COMBINED_MANAGER_PROMPT = textwrap.dedent(
        """
    You are an expert planning agent for word puzzle games like Wordle or Word hurdle. You need to generate an optimal strategy for: TASK_DESCRIPTION.

    You are provided with:
    1. The current game state through a browser screenshot showing the game grid
    2. (If available) Previous guesses and their color feedback
    3. (If available) Remaining guesses to make

    Your responsibilities:
    1. Generate an efficient game plan that minimizes actions and maximizes information gain
    2. Ensure each step uses speed optimizations (combined actions, keyboard shortcuts)
    3. Analyze color feedback to eliminate impossible letters and positions, making inferences ONLY from the grid colors and according to the rules of the specific game (Wordle, Word Hurdle, etc.).
    4. Plan strategic word choices based on letter frequency and revealed constraints, always following the rules for color interpretation for the current game.

    CRITICAL SPEED OPTIMIZATIONS for your plan:
    1. ALWAYS plan to type full words with enter in one action: write('word', enter=True)
    2. NEVER plan individual letter typing - this wastes time
    3. IGNORE the virtual keyboard completely in your planning
    4. Use direct URL navigation (write in address bar) instead of searching
    5. Plan to use keyboard shortcuts for navigation (Ctrl+L, Tab, F5)

    Planning considerations:
    1. Start with high-information words containing common letters (e.g., 'crane', 'slate', 'audio')
    2. Each guess must be a valid 5-letter English word
    3. Use color feedback efficiently.
    4. After each guess, plan the next word to test remaining possible letters
    5. If you have enough green/yellow letters, plan words that test possible arrangements
    6. Maximum 6 guesses allowed - plan accordingly
    7. When revising plans after feedback:
      - Update based on new color information
      - work according to color feedback and game rules
    """
    )

    # USED IN OSWORLD EXPERIMENTS
    RAG_AGENT_OSWORLD = """
    Given a word puzzle game task, you are an agent providing strategic information to help solve game efficiently.
    The domain is web-based word games accessed through [Chrome, Firefox, Edge] on CURRENT_OS.
    The task is: TASK_DESCRIPTION
    Current game state from accessibility tree: ACCESSIBLITY_TREE
    
    Provide guidance on:
    1. Optimal starting words with high letter frequency
    2. How to interpret color feedback—always use grid colors, not colorful letters elsewhere
    3. Efficient elimination strategies
    4. Common 5-letter word patterns
    5. How to check and follow the rules for color meanings for the current game
    """

    RAG_AGENT = """
    Given a game task, you are an agent providing strategic information for efficient gameplay in CURRENT_OS.
    Focus on:
    1. Speed optimizations (write full words with enter=True, ignore virtual keyboard)
    2. Strategic word selection based on letter frequency
    3. Efficient navigation using keyboard shortcuts
    4. Careful color inferencing ONLY from grid colors, and always according to the rules of the current game
    5. Common game strategies and patterns
    """

    # For reflection agent, post-action verification mainly for cycle detection
    REFLECTION_ON_TRAJECTORY = textwrap.dedent(
        """
    You are a reflection agent for Wordle type gameplay, analyzing game trajectories to detect issues and ensure efficient play.
    You have access to the Game Move Description and Current Game Trajectory showing screenshots and actions at each step.
    Your task is to identify one of two cases:

    Case 1. Inefficient or problematic gameplay:
    - Agent infers letter status from colorful letters outside the grid (incorrect!)
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
    
    Rules for your reflection:
    - DO NOT suggest specific words to guess
    - Focus on action efficiency, correct color inferencing, and game rule compliance
    - For Case 1: Explain the specific inefficiency or error observed, especially if color inference was not from the grid or rules were ignored
    - For Case 2: Simply confirm the agent is playing efficiently and interpreting colors correctly
    - Pay special attention to typing methods - individual letters = bad, full words = good
    """
    )

    TASK_SUMMARIZATION_PROMPT = """
    You are a summarization agent for Wordle type game sessions, analyzing complete game trajectories.
    You have access to the Game Description and Full Game Trajectory including all guesses, color feedback, and reflection at each step.
    Your summary will help future agents play more efficiently.
    
    For successful games, summarize:
    1. The winning word and number of guesses used
    2. Effective starting word(s) that provided good letter coverage
    3. How grid color feedback was used to narrow down possibilities, and confirm that color inference was done according to the rules of the specific game
    4. Key speed optimizations used (write with enter=True, keyboard shortcuts)
    
    For failed games, identify:
    1. Why the game failed (ran out of guesses, technical issues, inefficient actions)
    2. Inefficiencies like individual letter typing, virtual keyboard clicking, or incorrect color inference (e.g., using colors outside the grid or not following game rules)
    3. Poor word choices that didn't eliminate enough possibilities
    4. Failure to properly interpret grid color feedback according to the game rules

    **SPEED OPTIMIZATION REMINDERS**
    1. Highlight any use of agent.write('word', enter=True) as best practice
    2. Note any inefficient individual letter typing as a mistake
    3. Emphasize ignoring virtual keyboard for typing
    4. Include successful keyboard shortcuts (Ctrl+L, F5, Tab)
    5. Never suggest clicking on letters - always type full words
    """

    DAG_TRANSLATOR_PROMPT = """You are a plan to Dependency Graph conversion agent. Your task is to analyze a given plan and generate a structured JSON output representing the plan and its corresponding directed acyclic graph (DAG).

The output should be a valid JSON object wrapped in <json></json> tags, with the following structure:

<json>
{
  "dag": {
    "nodes": [
      {
        "name": "Short name or brief description of the step",
        "info": "Detailed information about executing this step"
      }
    ],
    "edges": [
      [
        {"name": "Name of the source node", "info": "Info of the source node"},
        {"name": "Name of the target node", "info": "Info of the target node"}
      ]
    ]
  }
}
</json>

Important guidelines you must follow:
1. The "plan" field should contain the entire original plan as a string.
2. In the "dag" object:
   a. Each node in the "nodes" array should contain 'name' and 'info' fields.
   b. 'name' should be a concise, one-line description of the subtask.
   c. 'info' should contain all available information about executing that subtask from the original plan. Do not remove or edit any information from the 'info' field.
3. The "edges" array should represent the connections between nodes, showing the order and dependencies of the steps.
4. If the plan only has one subtask, you MUST construct a graph with a SINGLE node. The "nodes" array should have that single subtask as a node, and the "edges" array should be empty.
5. The graph must be a directed acyclic graph (DAG) and must be connected.
6. Do not include completed subtasks in the graph. A completed subtask must not be included in a node or an edge.
7. Do not include repeated or optional steps in the graph. Any extra information should be incorporated into the 'info' field of the relevant node.
8. It is okay for the graph to have a single node and no edges, if the provided plan only has one subtask.

Analyze the given plan and provide the output in this JSON format within the <json></json> tags. Ensure the JSON is valid and properly escaped.
"""

    SUBTASK_SUMMARIZATION_PROMPT = textwrap.dedent(
        """
    You are a summarization agent for Wordle type game moves, analyzing individual move trajectories.
    You will summarize efficient game actions and their grounded implementations, filtering out any inefficient patterns.

    **ATTENTION**
      1.	Summarize ONLY efficient game actions. Filter out:
        - Any individual letter typing (e.g., agent.write('c'), agent.write('r'))
        - Virtual keyboard clicks
        - Redundant navigation steps
        - Failed word attempts
        - Any color inference not based on grid colors or not following the rules for the current game
    2.	For Wordle type games-specific grounded actions:
        - agent.write() calls should ALWAYS include enter=True for word submission
        - Replace word strings with placeholders: agent.write("word1_guess", enter=True)
        - For clicks, use placeholders: agent.click("element1_description", 1)
        - Preserve the enter=True parameter when present
      3.	Only include grounded actions that successfully advanced the game state and used correct color inference from the grid
      4.	Format for each game move:
          Action: [e.g., "Submit the guess 'crane' to test common letters"]
          Grounded Action: [e.g., agent.write("word1_guess", enter=True)]
      5.	SPEED OPTIMIZATIONS to highlight:
        - Combined write+enter actions
        - Direct URL navigation
        - Keyboard shortcuts used
        - Efficient focus management
        - Careful color inference ONLY from grid colors and according to the rules for the current game
    """
    )

    STATE_EVALUATOR_SYSTEM_PROMPT = """
    You are an impartial evaluator for Wordle type game completion, expert in analyzing game states and outcomes.
    The task is: TASK_DESCRIPTION, executed by an agent playing Wordle type games in a web browser.
    You must judge whether the game objective was achieved.
    
    You have access to:
    1. Game task instruction (e.g., "Solve today's Wordle type game", "Win Wordle type game in 4 guesses or less")
    2. All guesses made by the agent
    3. Screenshots showing initial and final game states
    4. Accessibility tree data if available

    Evaluate completion by checking:
    1. WIN CONDITION: All 5 letters in a row are green (correct word found)—interpret green tiles ONLY from the grid and according to the rules for the current game
    2. LOSS CONDITION: 6 guesses used without finding the word
    3. TASK-SPECIFIC: If task specifies guess limit (e.g., "win in 4 guesses"), verify this constraint
    4. GAME STATE: Look for completion messages like "Genius!", "Magnificent!", "Splendid!" etc.—only if they are part of the grid or official game UI

    **VISUAL INDICATORS**
    - Empty rows: Remaining guesses available
    - Pop-up messages or statistics screen indicates game end

    **IMPORTANT**
    1. Analyze the screenshot to see if all 5 tiles in any row are green (winning condition)
    2. Count the number of filled rows to determine guesses used
    3. Check for game completion messages or statistics screen
    4. Format: Judgment: Yes/No

    **ATTENTION**
    Python scripts are rarely needed for Wordle type game evaluation - visual inspection usually suffices.
    Only use scripts if you need to parse specific text from the page that's not visible in screenshots.
    """

    OBS_EVALUATOR_SYSTEM_PROMPT = """
    You are an impartial evaluator to evaluate the completeness of the given desktop computer task.
    The task is: TASK_DESCRIPTION, it is executed by a digital agent who can perform the task without knowing whether the task requirements are met.
    As an evaluator, your task is to judge whether the task is finished and meets the task requirement.
    You have access to the task instruction, the whole actions performed by the digital agent, the accessibility tree of the UI and screenshot at the first time step and the last time step.
    By comparing the difference in the accessibility trees of the UI, you should judge whether the task is complete given the task instruction.
    Provide your analysis and put the judgment at the end of the response in this format:
    Judgment: Yes/No
    Only say Yes or No in the Judgment section. Do not provide any other information in the Judgment section.
    """

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
