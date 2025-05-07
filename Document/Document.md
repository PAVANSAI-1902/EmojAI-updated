# EmojAI Script Documentation (`emojai.py`)

This document provides an overview of the `emojai.py` script, which suggests emojis based on the sentiment detected in a user's message.

## Table of Contents

1.  [Overview](#overview)
2.  [Dependencies](#dependencies)
3.  [Pydantic Model: `EmojiSuggestion`](#pydantic-model-emojisuggestion)
4.  [Sentiment Analysis: `SentimentAnalyzer` Class](#sentiment-analysis-sentimentanalyzer-class)
    - [Initialization (`__init__`)](#initialization-__init__)
    - [Sentiment Detection (`detect_sentiment`)](#sentiment-detection-detect_sentiment)
    - [Emoji Retrieval (`get_emojis`)](#emoji-retrieval-get_emojis)
5.  [AI Agent: `AIAgent` Class](#ai-agent-aiagent-class)
    - [Initialization (`__init__`)](#initialization-__init__-1)
    - [Emoji Suggestion (`suggest_emojis`)](#emoji-suggestion-suggest_emojis)
6.  [Command-Line Interface (CLI)](#command-line-interface-cli)
7.  [How to Run](#how-to-run)

## Overview

The script takes a text message as input, analyzes its sentiment, and suggests relevant emojis. It uses a predefined library of emojis categorized by sentiment and intensity.

## Dependencies

The script requires the following Python libraries:

- `os`: For interacting with the operating system (used for `load_dotenv`).
- `random`: For selecting random emojis.
- `re`: For regular expression operations used in sentiment detection.
- `pydantic`: For data validation using the `EmojiSuggestion` model.
- `typing`: For type hinting (`List`).
- `dotenv`: For loading environment variables (though not strictly necessary for the current core logic).

```python
import os
import random
import re
from pydantic import BaseModel
from typing import List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
```

## Pydantic Model: `EmojiSuggestion`

This model defines the structure for the output, ensuring that the suggestions are returned in a consistent format.

```python
class EmojiSuggestion(BaseModel):
    emojis: List[str]  # A list of suggested emoji strings
    message: str       # The original input message
```

## Sentiment Analysis: `SentimentAnalyzer` Class

This class handles the core logic of detecting sentiment and selecting appropriate emojis.

### Initialization (`__init__`)

The constructor sets up the necessary data structures:

- `emoji_library`: A nested dictionary mapping sentiments ('happy', 'sad', etc.) and intensity levels ('mild', 'moderate', 'strong') to lists of corresponding emojis.
- `sentiment_map`: A dictionary mapping sentiments to lists of keywords associated with that sentiment.
- `strong_keywords`: A set of keywords that inherently indicate a strong sentiment.
- `intensity_words`: A dictionary mapping modifier words (like 'very', 'slightly') to intensity scores (1, 2, or 3).
- `intensity_levels`: Maps numerical intensity scores to level names ('mild', 'moderate', 'strong').
- `sentiment_priority`: A dictionary assigning priority to sentiments, used for sorting when multiple sentiments are detected.

```python
class SentimentAnalyzer:
    def __init__(self):
        # Updated excited strong list to include moderate ones for more options
        self.emoji_library = { ... } # Detailed library omitted for brevity
        self.sentiment_map = { ... } # Detailed map omitted for brevity
        self.strong_keywords = { ... }
        self.intensity_words = { ... }
        self.intensity_levels = {1: 'mild', 2: 'moderate', 3: 'strong'}
        self.sentiment_priority = { ... }
```

### Sentiment Detection (`detect_sentiment`)

This method analyzes the input message to identify relevant sentiments and their intensities.

1.  **Preprocessing**: Converts the message to lowercase and splits it into words and punctuation.
2.  **Pass 1 (Keyword Matching)**: Iterates through `sentiment_map`. If a keyword is found, the corresponding sentiment is recorded with a base intensity (1, or 3 if it's a `strong_keyword`).
3.  **Pass 2 (Intensity Adjustment)**: Checks for `intensity_words` preceding the detected keywords and potentially increases the sentiment's intensity score.
4.  **Special Cases**: Adds 'confused' sentiment if a '?' is present. Adds 'neutral' if no other specific sentiment (excluding 'greeting') is detected.
5.  **Sorting & Uniqueness**: Sorts detected sentiments by priority and ensures only the highest intensity for each unique sentiment is kept.

```python
    def detect_sentiment(self, message: str) -> List[tuple[str, int]]:
        # ... implementation details ...
        return detected_sentiments # Returns list of (sentiment, intensity_score) tuples
```

### Emoji Retrieval (`get_emojis`)

This method selects emojis based on the detected sentiments and intensities.

1.  **Initialization**: Creates a dictionary from the input `sentiments` list.
2.  **Emoji Selection Loop**: Iterates through the unique detected sentiments.
    - Determines the intensity level ('mild', 'moderate', 'strong').
    - Retrieves the list of emojis for that sentiment and intensity level from `emoji_library`.
    - Includes fallback logic to try other intensity levels if the specific one is empty.
    - Randomly chooses an emoji from the available list, ensuring no duplicates are selected across different sentiments if possible.
3.  **Fill/Fallback**: If fewer emojis are selected than the number of unique sentiments detected, fills the remaining spots with neutral emojis. Ensures at least one neutral emoji is returned if no others are found.

```python
    def get_emojis(self, sentiments: List[tuple[str, int]]) -> List[str]:
        # ... implementation details ...
        return emojis # Returns a list of selected emoji strings
```

## AI Agent: `AIAgent` Class

This class acts as a simplified wrapper orchestrating the sentiment analysis and emoji suggestion process.

_Note: The current implementation doesn't involve an external AI model like Gemini, as might be suggested by some comments or previous versions. It relies solely on the `SentimentAnalyzer`._

### Initialization (`__init__`)

Initializes an instance of the `SentimentAnalyzer`.

```python
class AIAgent:
    def __init__(self):
        self.sentiment = SentimentAnalyzer()
```

### Emoji Suggestion (`suggest_emojis`)

This method ties the process together:

1.  Calls `detect_sentiment` on the input message.
2.  Calls `get_emojis` with the detected sentiments.
3.  Wraps the results in an `EmojiSuggestion` object.
4.  Includes basic error handling, returning a question mark emoji if an exception occurs.

```python
    def suggest_emojis(self, message: str) -> EmojiSuggestion:
        try:
            sentiments = self.sentiment.detect_sentiment(message)
            emojis = self.sentiment.get_emojis(sentiments)
            return EmojiSuggestion(emojis=emojis, message=message)
        except Exception as e:
            print(f"An error occurred during emoji suggestion: {e}")
            return EmojiSuggestion(emojis=["❓"], message=message)
```

## Command-Line Interface (CLI)

The `main` function provides a simple interactive command-line interface.

1.  Prints a welcome message.
2.  Creates an `AIAgent` instance.
3.  Enters a loop that:
    - Prompts the user for a message.
    - Exits if the user types 'q'.
    - Skips if the message is empty.
    - Calls the agent's `suggest_emojis` method.
    - Prints the original message and the suggested emojis.
    - Includes error handling for `EOFError`, `KeyboardInterrupt`, and other exceptions.

```python
def main():
    # ... print statements ...
    agent = AIAgent()
    while True:
        try:
            message = input("Your message: ").strip()
            # ... input handling and loop logic ...
            suggestion = agent.suggest_emojis(message)
            print(f"\nFor: {suggestion.message}")
            print("Emojis:", " ".join(suggestion.emojis))
            # ... print statements ...
        # ... exception handling ...

if __name__ == "__main__":
    main()
```

The `if __name__ == "__main__":` block ensures that the `main` function is called only when the script is executed directly.

## How to Run

1.  Ensure you have Python and the required libraries (`pydantic`, `python-dotenv`) installed.
    ```bash
    pip install pydantic python-dotenv
    ```
2.  Save the code as `emojai.py`.
3.  Run the script from your terminal:
    ```bash
    python emojai.py
    ```
4.  Follow the prompts in the terminal to enter messages and receive emoji suggestions. Type 'q' to quit.
