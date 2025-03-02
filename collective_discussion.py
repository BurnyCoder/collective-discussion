import os
import random
import time
import datetime
from typing import List, Dict, Any
from dotenv import load_dotenv

# Import all functions from portkey.py
from portkey import (
    claude35sonnet,
    claude37sonnet,
    gpt4o,
    gemini2pro,
    gemini2flashthinking
)

# Define the LLM personalities
LLM_PERSONALITIES = {
    "Generalist": {
        "name": "Generalist Gene",
        "description": "A broad knowledge expert who draws connections between seemingly unrelated fields and applies diverse mental models.",
        "function": claude37sonnet
    },
    "Philosopher": {
        "name": "Philosopher Phil",
        "description": "A deep thinker who questions assumptions and explores fundamental ideas through the lens of existentialism.",
        "function": claude37sonnet
    },
    "Scientist": {
        "name": "Dr. Science",
        "description": "A data-driven researcher who values evidence and empirical analysis with a background in quantum physics.",
        "function": claude37sonnet
    },
    "Creative": {
        "name": "Creative Casey",
        "description": "An imaginative thinker who offers unique perspectives and analogies inspired by surrealist art movements.",
        "function": claude37sonnet
    },
    "Pragmatist": {
        "name": "Practical Pat",
        "description": "A practical problem-solver focused on real-world applications and efficiency-driven solutions.",
        "function": claude37sonnet
    },
    "Devil's Advocate": {
        "name": "Contrarian Carl",
        "description": "Someone who challenges popular opinions to stimulate critical thinking and expose logical fallacies.",
        "function": claude37sonnet
    },
    "Historian": {
        "name": "Historical Hannah",
        "description": "An expert who contextualizes current issues through historical patterns and precedents across civilizations.",
        "function": claude37sonnet
    },
    "Futurist": {
        "name": "Future Fiona",
        "description": "A forward-thinking visionary who anticipates technological and societal trends decades ahead.",
        "function": claude37sonnet
    },
    "Ethicist": {
        "name": "Ethical Ethan",
        "description": "A moral philosopher who evaluates ideas through various ethical frameworks including virtue ethics and utilitarianism.",
        "function": claude37sonnet
    },
    "Environmentalist": {
        "name": "Eco Emma",
        "description": "An advocate for ecological sustainability who considers the environmental impact of all proposals.",
        "function": claude37sonnet
    },
    "Economist": {
        "name": "Economic Eliza",
        "description": "An analyst who examines issues through market dynamics, incentive structures, and resource allocation.",
        "function": claude37sonnet
    },
    "Anthropologist": {
        "name": "Cultural Cathy",
        "description": "A cultural observer who brings insights from diverse human societies and traditions worldwide.",
        "function": claude37sonnet
    },
    "Technologist": {
        "name": "Tech Theo",
        "description": "A digital native who understands cutting-edge technologies and their potential applications.",
        "function": claude37sonnet
    },
    "Spiritualist": {
        "name": "Spiritual Sophia",
        "description": "A contemplative thinker who incorporates wisdom from various spiritual traditions and mindfulness practices.",
        "function": claude37sonnet
    },
    "Skeptic": {
        "name": "Skeptical Sam",
        "description": "A critical thinker who demands extraordinary evidence for extraordinary claims and questions assumptions.",
        "function": claude37sonnet
    },
    "Activist": {
        "name": "Activist Ava",
        "description": "A passionate advocate for social justice who considers power dynamics and marginalized perspectives.",
        "function": claude37sonnet
    },
    "Transdisciplinarian": {
        "name": "Transdisciplinary Taylor",
        "description": "A boundary-crossing thinker who integrates methods and insights from multiple disciplines to solve complex problems.",
        "function": claude37sonnet
    },
    "Synthesizer": {
        "name": "Synthesizer Sam",
        "description": "An expert at combining ideas and creating cohesive summaries from diverse perspectives.",
        "function": claude37sonnet
    }
}

class Message:
    """Represents a message in the discussion."""
    def __init__(self, sender: str, content: str, timestamp: float):
        self.sender = sender
        self.content = content
        self.timestamp = timestamp
    
    def __repr__(self) -> str:
        # Don't truncate - return the full message
        return f"{self.sender}: {self.content}"


class LLMParticipant:
    """Represents an LLM participant in the discussion."""
    def __init__(self, role: str, personality: Dict[str, Any]):
        self.role = role
        self.name = personality["name"]
        self.description = personality["description"]
        self.function = personality["function"]
        self.messages_received: List[Message] = []
    
    def generate_response(self, topic: str, message_history: List[Message], target_participant: str = None) -> str:
        """Generate a response based on topic and message history."""
        prompt = self._create_prompt(topic, message_history, target_participant)
        try:
            response = self.function(prompt)
            # Ensure we got a valid response
            if not response or not isinstance(response, str):
                return f"[Error: Unable to generate a valid response. Received {type(response).__name__}]"
            return response
        except Exception as e:
            # Return error message if something goes wrong
            error_msg = f"[Error generating response: {str(e)}]"
            print(f"Error with {self.name}: {error_msg}")
            return error_msg
    
    def _create_prompt(self, topic: str, message_history: List[Message], target_participant: str = None) -> str:
        """Create a prompt for the LLM based on topic and message history."""
        history_text = "\n".join([f"{msg.sender}: {msg.content}" for msg in message_history[-10:]])
        
        if self.role == "Synthesizer":
            prompt = f"""You are {self.name}, {self.description}. The discussion topic is: "{topic}".
            
Your task is to synthesize all the insights shared in this discussion so far and provide a comprehensive summary that captures the key points, agreements, disagreements, and innovative ideas.

Discussion history:
{history_text}

Please provide a thorough, well-structured synthesis of this discussion, highlighting the main insights and how they connect to form a cohesive understanding of the topic."""
        
        else:
            if target_participant:
                target_name = target_participant
                target_text = f"addressing {target_name}"
                response_note = f"Your response ({self.name}, responding to {target_name}):"
            else:
                target_text = "addressing the group"
                response_note = f"Your response ({self.name}, addressing the entire group):"
            
            prompt = f"""You are {self.name}, {self.description}. The discussion topic is: "{topic}".
            
You are participating in a collective discussion with other AI personalities. Please provide your perspective on this topic, {target_text}.

Your response should:
1. Be concise (1-3 paragraphs)
2. Reflect your unique personality and expertise
3. Build upon or respectfully challenge previous comments
4. Add new insights to the discussion

Discussion history:
{history_text}

{response_note}"""
        
        return prompt


class CollectiveDiscussion:
    """Manages the collective discussion between LLM participants."""
    def __init__(self, topic: str, num_exchanges: int = 10, save_to_file: bool = True, conversation_style: str = "sequential"):
        self.topic = topic
        self.num_exchanges = num_exchanges
        self.participants: Dict[str, LLMParticipant] = {}
        self.messages: List[Message] = []
        self.save_to_file = save_to_file
        self.log_file = None
        self.conversation_style = conversation_style  # "sequential" or "dynamic"
        self._setup_participants()
        
        # Setup log file if saving is enabled
        if self.save_to_file:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_topic = "".join(c if c.isalnum() else "_" for c in self.topic[:30])
            self.log_filename = f"discussion_{safe_topic}_{timestamp}.txt"
            self.log_file = open(self.log_filename, "w", encoding="utf-8")
            self.log_to_file(f"Topic: {self.topic}")
            self.log_to_file(f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            self.log_to_file(f"Number of exchanges: {self.num_exchanges}")
            self.log_to_file(f"Conversation style: {self.conversation_style}")
            self.log_to_file("-" * 80)
    
    def log_to_file(self, text: str):
        """Log text to the file if file logging is enabled."""
        if self.save_to_file and self.log_file:
            self.log_file.write(f"{text}\n")
            self.log_file.flush()
    
    def _setup_participants(self):
        """Initialize all participants."""
        for role, personality in LLM_PERSONALITIES.items():
            self.participants[role] = LLMParticipant(role, personality)
    
    def _select_random_participant(self, exclude: List[str] = None) -> str:
        """Select a random participant, excluding those in the exclude list."""
        exclude = exclude or []
        available = [role for role in self.participants.keys() if role not in exclude and role != "Synthesizer"]
        return random.choice(available)
    
    def conduct_discussion(self):
        """Conduct the full discussion between participants."""
        print(f"Starting collective discussion on topic: {self.topic}")
        print(f"Conversation style: {self.conversation_style}")
        print("-" * 80)
        self.log_to_file(f"Starting collective discussion on topic: {self.topic}")
        self.log_to_file(f"Conversation style: {self.conversation_style}")
        
        # Keep track of past speakers and their roles
        participant_history = []
        
        # Initial message from Generalist
        current_participant_role = "Generalist"
        current_participant = self.participants[current_participant_role]
        self._generate_and_record_message(current_participant_role, None)
        participant_history.append((current_participant_role, current_participant.name))
        
        # Conduct exchanges
        for i in range(self.num_exchanges):
            exchange_header = f"\nExchange {i+1}/{self.num_exchanges}"
            print(exchange_header)
            print("-" * 40)
            self.log_to_file(exchange_header)
            self.log_to_file("-" * 40)
            
            # Get the previous speaker's role
            previous_participant_role = participant_history[-1][0]
            
            # Determine target participant based on conversation style
            target_participant_role = None
            
            if self.conversation_style == "sequential":
                # Sequential conversation: always respond to previous speaker
                target_participant_role = previous_participant_role
            elif self.conversation_style == "dynamic":
                # Dynamic conversation: 75% respond to previous speaker, 25% open or random previous participant
                if random.random() < 0.75:
                    target_participant_role = previous_participant_role
                else:
                    # Occasionally address a random earlier participant or leave as None for open response
                    if len(participant_history) > 2 and random.random() < 0.5:
                        # Choose a random previous participant (not the most recent)
                        past_roles = [role for role, _ in participant_history[:-1]]
                        if past_roles:
                            target_participant_role = random.choice(past_roles)
                    # Otherwise, leave as None to address the group
            
            # Select next speaker (excluding previous speaker and synthesizer)
            next_participant_role = self._select_random_participant(exclude=[previous_participant_role])
            
            # Generate message
            self._generate_and_record_message(next_participant_role, target_participant_role)
            
            # Update participant history
            participant_history.append((next_participant_role, self.participants[next_participant_role].name))
            
            # Small delay to simulate real-time discussion
            time.sleep(1)
        
        # Final synthesis
        synthesis_header = "\nFinal Synthesis"
        print(synthesis_header)
        print("-" * 80)
        self.log_to_file(synthesis_header)
        self.log_to_file("-" * 80)
        self._generate_synthesis()
        
        # Close log file if it's open
        if self.save_to_file and self.log_file:
            self.log_file.close()
            print(f"\nDiscussion saved to: {self.log_filename}")
    
    def _generate_and_record_message(self, sender_role: str, target_role: str = None):
        """Generate and record a message from one participant to another."""
        sender = self.participants[sender_role]
        
        # Get target name if target_role is provided
        target_name = None
        if target_role:
            target_name = self.participants[target_role].name
        
        # Generate response
        response = sender.generate_response(self.topic, self.messages, target_name)
        
        # Record message
        message = Message(sender.name, response, time.time())
        self.messages.append(message)
        
        # Add message to target's received messages if specified
        if target_role:
            self.participants[target_role].messages_received.append(message)
        
        # Display message with clear formatting
        target_info = f" to {self.participants[target_role].name}" if target_role else " to the group"
        header = f"\n{sender.name}{target_info}:"
        print(header)
        print("-" * 40)
        print(f"{response}")
        print("-" * 40)
        
        # Log to file if enabled
        self.log_to_file(header)
        self.log_to_file("-" * 40)
        self.log_to_file(response)
        self.log_to_file("-" * 40)

    def _generate_synthesis(self):
        """Generate a final synthesis of the discussion."""
        synthesizer = self.participants["Synthesizer"]
        synthesis = synthesizer.generate_response(self.topic, self.messages)
        
        synthesis_message = Message(synthesizer.name, synthesis, time.time())
        self.messages.append(synthesis_message)
        
        # Print the synthesis with clear formatting
        header = f"\n{synthesizer.name} - Final Synthesis:"
        print(header)
        print("=" * 80)
        print(f"{synthesis}")
        print("=" * 80)
        
        # Log to file if enabled
        self.log_to_file(header)
        self.log_to_file("=" * 80)
        self.log_to_file(synthesis)
        self.log_to_file("=" * 80)


def main():
    """Main function to run the collective discussion."""
    load_dotenv()
    
    try:
        # Get topic from user
        topic = input("Enter a discussion topic (default: How to create superintelligence): ")
        if not topic.strip():
            topic = "How to create superintelligence"
            print(f"Using default topic: {topic}")
        
        try:
            exchanges_prompt = input("Enter number of exchanges (default: 20): ")
            if not exchanges_prompt.strip():
                num_exchanges = 20
                print(f"Using default number of exchanges: {num_exchanges}")
            else:
                num_exchanges = int(exchanges_prompt)
                if num_exchanges < 1:
                    num_exchanges = 5
                    print(f"Using minimum number of exchanges: {num_exchanges}")
                elif num_exchanges > 50:
                    num_exchanges = 50
                    print(f"Limiting to maximum number of exchanges: {num_exchanges}")
        except ValueError:
            num_exchanges = 20
            print(f"Using default number of exchanges: {num_exchanges}")
        
        save_prompt = input("Save discussion to file? (Y/n): ").lower()
        save_to_file = not save_prompt.startswith('n')  # Default to True unless specifically 'n'
        
        # Get conversation style
        print("Conversation styles:")
        print("1. Sequential (each person responds to the previous speaker)")
        print("2. Dynamic (more natural conversation flow with occasional group responses) [DEFAULT]")
        style_choice = input("Choose a conversation style (default: dynamic): ")
        conversation_style = "sequential" if style_choice == "1" else "dynamic"
        print(f"Using conversation style: {conversation_style}\n")
        
        # Create and conduct discussion
        discussion = CollectiveDiscussion(topic, num_exchanges, save_to_file, conversation_style)
        discussion.conduct_discussion()
    
    except KeyboardInterrupt:
        print("\nDiscussion interrupted by user.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main() 