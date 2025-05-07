import os
import random
import re
from pydantic import BaseModel
from typing import List
from dotenv import load_dotenv

# Load environment variables (keep if you use .env for other things)
load_dotenv()

# --------------------------
# Pydantic Models
# --------------------------
class EmojiSuggestion(BaseModel):
    emojis: List[str]
    message: str

# --------------------------
# Sentiment Analysis
# --------------------------
class SentimentAnalyzer:
    def __init__(self):
        # Updated excited strong list to include moderate ones for more options
        self.emoji_library = {
            'happy': {
                'mild': ["😊", "🙂", "😄", "😀"],
                'moderate': ["😃", "😁", "😆", "😊"],
                'strong': ["🤩", "🥳", "😻", "🎉", "🎊"]
            },
            'sad': {
                'mild': ["😔", "😞", "🥺", "😟"],
                'moderate': ["😢", "😥", "😭", "愁"],
                'strong': ["😩", "😣", "😿", "😭", "💔"]
            },
            'love': {
                'mild': ["🥰", "😍", "❤️", "😘"],
                'moderate': ["💖", "💕", "💞", "💓"],
                'strong': ["💘", "💝", "💟", "🥰", "😍"]
            },
            'excited': {
                'mild': ["😎", "😏", "😺", "👍"],
                'moderate': ["🤩", "🥳", "😻", "🙌"],
                'strong': ["🤩", "🥳", "😻", "🙌", "🎉", "🎊", "😸", "🚀", "🔥"]
            },
            'greeting': {
                'mild': ["👋", "🤚", "🖐️", "🤝"],
                'moderate': ["✌️", "🤞", "👌", "🤙"],
                'strong': ["🤟", "🖖", "✋", "👊", "🙏"]
            },
            'angry': {
                'mild': ["😠", "😒", "😤", "🙄"],
                'moderate': ["😡", "🤬", "😠", "😤"],
                'strong': ["👿", "😠", "😡", "🤬"]
            },
            'danger': {
                'mild': ["⚠️", "🚨", "🆘", "🛑"],
                'moderate': ["😰", "😨", "😬", "😱"],
                'strong': ["😱", "🔥", "🆘", "💣", "💥"]
            },
            'confused': {
                'mild': ["😕", "🤔", "🧐", "🤷"],
                'moderate': ["😖", "😣", "🤨", "😟"],
                'strong': ["😵", "😓", "🤯", "🤔", "❓"]
            },
            'neutral': {
                'mild': ["😐", "😑", "😶", "😌"],
                'moderate': ["😒", "🙄", "😏", " bland"],
                'strong': ["🤨", "🧐", "😶‍🌫️", "🗿", "🧊"]
            }
        }

        # Added "marvelous" to happy, love, excited keywords
        # **ADDED "laughing" to the happy keywords**
        self.sentiment_map = {
            'happy': ["happy", "joy", "good", "great", "awesome", "cheerful", "glad", "fun", "party", "friends", "enjoying", "amazing", "wonderful", "nice", "pleased", "satisfied", "excited", "thrilled", "elated", "jubilant", "marvelous", "laughing", "exited"],
            'sad': ["sad", "bad", "upset", "unhappy", "depressed", "sorry", "down", "terrible", "horrible", "lose", "miss", "lonely", "grief", "woe"],
            'love': ["love", "heart", "adore", "cherish", "care", "affection", "like", "favorite", "beautiful", "fond", "attached", "crush", "passion", "romance", "sweetheart", "darling", "marvelous"],
            'excited': ["excited", "wow", "amazing", "thrilled", "fun", "enthusiastic", "yay", "hooray", "cant wait", "soon", "ready", "eager", "anticipating", "adventure", "journey", "explore", "marvelous"],
            'greeting': ["hello", "hi", "hey", "greetings", "yo", "sup", "morning", "afternoon", "evening", "goodbye", "bye", "ciao", "hola"],
            'angry': ["angry", "furious", "mad", "irritated", "annoyed", "frustrated", "pissed", "rage", "enraged", "livid", "upset", "hate", "dislike"],
            'danger': ["danger", "warning", "alert", "emergency", "urgent", "stop", "careful", "risk", "problem", "issue", "hazard", "threat", "unsafe"],
            'confused': ["confused", "why", "huh", "what", "puzzled", "dont understand", "unclear", "question", "?", "explain", "baffled", "perplexed"]
        }

        # Keywords that indicate a strong sentiment even without modifiers
        self.strong_keywords = {"marvelous", "amazing", "wonderful", "terrible", "horrible", "furious", "enraged", "urgent", "emergency", "shocked", "astounded"} # "laughing" not considered inherently strong here

        self.intensity_words = {
            'slightly': 1, 'a little': 1, 'very': 2, 'really': 2, 'pretty': 2,
            'extremely': 3, 'seriously': 3, 'so': 2, 'completely': 3,
            'totally': 3, 'absolutely': 3, 'quite': 2
        }

        self.intensity_levels = {1: 'mild', 2: 'moderate', 3: 'strong'}

        self.sentiment_priority = {
            'excited': 1, 'love': 2, 'happy': 3, 'angry': 4, 'danger': 5,
            'sad': 6, 'greeting': 7, 'confused': 8, 'neutral': 9
        }

    def detect_sentiment(self, message: str) -> List[tuple[str, int]]:
        lower_msg = message.lower()
        words = re.findall(r'\b\w+\b|[^\w\s]', lower_msg)
        sentiment_intensities = {}

        # Pass 1: Detect sentiments and set base/strong intensity
        for sent, keywords in self.sentiment_map.items():
            for keyword in keywords:
                if re.search(r'\b' + re.escape(keyword) + r'\b', lower_msg):
                    base_intensity = 1
                    if keyword in self.strong_keywords:
                        base_intensity = 3 # Strong keywords start at level 3

                    # Set or update intensity if current match is stronger
                    if sent not in sentiment_intensities or base_intensity > sentiment_intensities[sent]:
                        sentiment_intensities[sent] = base_intensity

        # Pass 2: Adjust intensity based on preceding intensity words
        words_with_index = list(enumerate(words))
        for sent, current_intensity in list(sentiment_intensities.items()): # Iterate over a copy
             for keyword in self.sentiment_map.get(sent, []): # Get keywords for this detected sentiment
                keyword_indices = [i for i, word in words_with_index if word == keyword]
                for keyword_idx in keyword_indices:
                    for i in range(max(0, keyword_idx - 3), keyword_idx):
                        word_before = words[i]
                        if word_before in self.intensity_words:
                            # Take the max between existing intensity and intensity word
                            sentiment_intensities[sent] = max(current_intensity, self.intensity_words[word_before])

        detected_sentiments = [(sent, intensity) for sent, intensity in sentiment_intensities.items()]

        # Handle question marks
        if "?" in message and 'confused' not in [s[0] for s in detected_sentiments]:
             detected_sentiments.append(('confused', 1))

        # Add neutral if no other specific sentiment detected
        if not any(s[0] not in ['neutral', 'greeting'] for s in detected_sentiments):
             if 'neutral' not in [s[0] for s in detected_sentiments]:
                  detected_sentiments.append(('neutral', 1))

        # Sort and unique
        detected_sentiments.sort(key=lambda x: self.sentiment_priority.get(x[0], 99))
        unique_sentiments = {}
        for sent, intensity in detected_sentiments:
             if sent not in unique_sentiments or intensity > unique_sentiments[sent][1]:
                 unique_sentiments[sent] = (sent, intensity)
        detected_sentiments = list(unique_sentiments.values())
        detected_sentiments.sort(key=lambda x: self.sentiment_priority.get(x[0], 99))

        return detected_sentiments


    def get_emojis(self, sentiments: List[tuple[str, int]]) -> List[str]:
        emojis = []
        sentiment_intensity_map = dict(sentiments)
        unique_sentiments = list(sentiment_intensity_map.keys())
        emoji_count_target = len(unique_sentiments) if unique_sentiments else 1

        used_emojis = set()

        for sentiment in unique_sentiments:
            specific_intensity = sentiment_intensity_map.get(sentiment, 1)
            specific_intensity_level = self.intensity_levels.get(specific_intensity, 'mild')

            # Get emojis for this specific sentiment and its detected intensity level
            available_emojis = self.emoji_library.get(sentiment, {}).get(specific_intensity_level, self.emoji_library['neutral']['mild'])

            # Fallback if specific level is empty for this sentiment, try moderate/strong/mild in order
            if not available_emojis:
                 for level in ['strong', 'moderate', 'mild']:
                      available_emojis = self.emoji_library.get(sentiment, {}).get(level, [])
                      if available_emojis:
                           break
                 if not available_emojis: # Final fallback to neutral if still empty
                      available_emojis = self.emoji_library['neutral']['mild']


            chosen_emoji = None
            attempts = 0
            while chosen_emoji is None and attempts < len(available_emojis) * 3:
                 potential_emoji = random.choice(available_emojis)
                 if potential_emoji not in used_emojis:
                     chosen_emoji = potential_emoji
                 attempts += 1

            if chosen_emoji is not None:
                used_emojis.add(chosen_emoji)
                emojis.append(chosen_emoji)

        # Fill remaining spots with neutral if target not met
        while len(emojis) < emoji_count_target:
             neutral_options = [e for e in self.emoji_library['neutral']['mild'] if e not in used_emojis]
             if neutral_options:
                 chosen_emoji = random.choice(neutral_options)
                 used_emojis.add(chosen_emoji)
                 emojis.append(chosen_emoji)
             else:
                 break

        # Ensure at least one emoji if nothing was added
        if not emojis:
             emojis.append(random.choice(self.emoji_library['neutral']['mild']))

        return emojis

# --------------------------
# AI Agent (Simplified)
# --------------------------
class AIAgent:
    def __init__(self):
        self.sentiment = SentimentAnalyzer()

    def suggest_emojis(self, message: str) -> EmojiSuggestion:
        try:
            sentiments = self.sentiment.detect_sentiment(message)
            emojis = self.sentiment.get_emojis(sentiments)
            return EmojiSuggestion(emojis=emojis, message=message)
        except Exception as e:
            print(f"An error occurred during emoji suggestion: {e}")
            return EmojiSuggestion(emojis=["❓"], message=message)

# --------------------------
# CLI Interface
# --------------------------
def main():
    print("\n🌟 Ultimate Emoji Suggester 🌟")
    print("----------------------------")
    print("Enter a message to get emoji suggestions!")
    print("Type 'q' to quit\n")

    agent = AIAgent() # Simplified agent

    while True:
        try:
            message = input("Your message: ").strip()
            if message.lower() == 'q':
                print("\nGoodbye! 👋")
                break

            if not message:
                print("Please enter a message.")
                continue

            suggestion = agent.suggest_emojis(message)
            print(f"\nFor: {suggestion.message}")
            print("Emojis:", " ".join(suggestion.emojis))

            print("="*50 + "\n")

        except EOFError:
             print("\nGoodbye! 👋")
             break
        except KeyboardInterrupt:
             print("\nGoodbye! 👋")
             break
        except Exception as e:
             print(f"An unexpected error occurred in the CLI: {e}")

if __name__ == "__main__":
    main()