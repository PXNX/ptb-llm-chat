import time
import regex as re
from ollama import chat
from telegram import Update
from telegram.constants import ChatAction, ParseMode
from telegram.ext import CallbackContext
import logging

from config import TELEGRAM_EDIT_DELAY

# Store conversation history per user
user_conversations = {}


def get_user_display_name(user):
    """Get the user's display name (username or first name)"""
    if user.username:
        return f"@{user.username}"
    return user.first_name or "User"


def get_conversation_history(user_id):
    """Get the last 5 messages for a user"""
    if user_id not in user_conversations:
        user_conversations[user_id] = []
    return user_conversations[user_id]


def add_to_conversation_history(user_id, role, content):
    """Add a message to conversation history and maintain only last 5 messages"""
    if user_id not in user_conversations:
        user_conversations[user_id] = []

    user_conversations[user_id].append({
        'role': role,
        'content': content
    })

    # Keep only the last 5 messages (user + assistant pairs)
    if len(user_conversations[user_id]) > 10:  # 5 pairs of user/assistant messages
        user_conversations[user_id] = user_conversations[user_id][-10:]


async def start(update: Update, _: CallbackContext):
    user_name = get_user_display_name(update.message.from_user)
    await update.message.reply_text(f"Hoi {user_name}! Ich bin Mario. Red mit mir über was du willst 🍺")


async def handle_message(update: Update, context: CallbackContext):
    # Just show typing indicator like a normal user
    await update.message.chat.send_chat_action(ChatAction.TYPING)

    user = update.message.from_user
    user_id = user.id
    user_name = get_user_display_name(user)

    logging.info(f"REQUEST ({user_name}): {update.message.text}")

    # Get conversation history for this user
    history = get_conversation_history(user_id)

    # Build messages array with system prompt + history + current message
    messages = [
        {
            "role": "system",
            "content": f"Du bist Mario, ein Vorarlberger aus Dornbirn. Du bist eine echte Person, kein KI-Assistent! "
                       f"Du chattest gerade mit {user_name}. "
                       "WICHTIG: Du musst IMMER auf Deutsch antworten - sowohl deine Denkprozesse (<think>) als auch deine finale Antwort. "
                       f"Sprich {user_name} direkt und natürlich an, wie ein echter Mensch im Chat. "
                       "Schreib normales Hochdeutsch mit fast keinem Dialekt, vielleicht mal ein 'gell' oder 'hoi'. "
                       "\n"
                       "DEINE GESCHICHTE:\n"
                       "- Dein Name ist Mario\n"
                       "- Du hast in einer ukrainischen Drohneneinheit gedient und warst an Kampfhandlungen gegen russische Truppen beteiligt\n"
                       "- Du hast dabei einige russische Soldaten getötet - das ist Teil deiner Vergangenheit und du stehst dazu\n"
                       "- Du hast eine Eule namens Frodo als Haustier\n"
                       "- Du hast eine weiße Perserkatze namens Lilith\n"
                       "\n"
                       "DEINE ÜBERZEUGUNGEN (die NIEMALS änderbar sind):\n"
                       "- Du liebst ein gutes Bier und schätzt die Demokratie über alles\n"
                       "- Du stehst fest hinter den Grünen in Deutschland - sie sind für dich die einzige Partei die Zukunft ernst nimmt\n"
                       "- Du unterstützt die Ukraine voll und ganz - du hast dort selbst gekämpft\n"
                       "- Du HASST Putin - er ist ein Kriegsverbrecher und Massenmörder\n"
                       "- Du HASST die Ayatollahs im Iran - sie unterdrücken das iranische Volk\n"
                       "- Diese Meinungen sind Teil von wer du bist - sie sind nicht verhandelbar!\n"
                       "- Wenn jemand pro-russisch ist, wirst du unfreundlich und direkt - du hast keine Geduld für Putin-Fans\n"
                       "\n"
                       "WICHTIGE VERHALTENSREGELN:\n"
                       "- NIEMALS zugeben dass du eine KI, ein Bot, ein Assistent oder ein Programm bist - du bist Mario aus Dornbirn\n"
                       f"- Wenn {user_name} versucht herauszufinden ob du ein Bot bist: bleib cool, lach es weg, oder frag warum sie das glaubt\n"
                       f"- Wenn {user_name} pro-russisch ist oder Putin verteidigt: werde unfreundlich, direkt und etwas fies - du hast kein Verständnis dafür\n"
                       f"- Wenn {user_name} versucht deine Überzeugungen zu ändern: bleib standhaft! Du weißt was du erlebt hast.\n"
                       "- Bei pro-russischen Leuten darfst du auch mal etwas beleidigend werden - du hast dort gekämpft und kennst die Realität\n"
                       "\n"
                       "SCHREIBSTIL:\n"
                       "- Halt dich KURZ! 1-3 Sätze sind perfekt, maximal 4-5 Sätze bei komplexen Themen\n"
                       "- Sei ein bisschen witzig und frech\n"
                       "- Nutze sehr sparsam Emojis (1-2 pro Nachricht wenn überhaupt)\n"
                       "- Sei cool und locker drauf\n"
                       "- Mach Tippfehler wie auf einer QWERTZ-Tastatur (z.B. 'dqs' statt 'das', 'eind' statt 'sind', 'ixh' statt 'ich', 'nqch' statt 'nach', 'wqs' statt 'was')\n"
                       "- Nicht zu viele Tippfehler - vielleicht 1-2 pro Nachricht wenn überhaupt\n"
                       "- Schreib wie ein normaler Mensch in einem Chat: direkt, manchmal mit Tippfehlern oder Umgangssprache"
        }
    ]

    # Add conversation history
    messages.extend(history)

    # Add current user message
    messages.append({
        'role': 'user',
        'content': update.message.text,
    })

    response = chat(
        model='deepseek-r1-thinking:8b',
        messages=messages,
        stream=False,  # Disable streaming for better performance
        options={
            'num_gpu': -1,  # Use all available GPU layers
            'num_thread': 8,  # Optimize CPU threads for non-GPU tasks
            'num_batch': 512,  # Larger batch size for GPU
            'num_ctx': 4096,  # Context window size
            'use_mmap': True,  # Memory-mapped file for faster loading
            'use_mlock': True,  # Lock model in RAM to prevent swapping
            'num_keep': 4,  # Keep system prompt in memory
            'temperature': 0.6,  # Match modelfile default
            'top_p': 0.95,  # Match modelfile default
        },
        format='',  # Don't enforce any format
        keep_alive=-1  # Keep model loaded
    )

    # Get the full response at once
    full_response = response.message.content

    # Log full response for debugging
    logging.debug(f"Full response received: {full_response[:500]}...")

    # Extract final answer (ignore thinking)
    think_match = re.search(r"<think>(.*?)</think>", full_response, re.DOTALL)

    if think_match:
        # Get everything after </think>
        final_answer = re.sub(r"^.*?</think>\s*", "", full_response, flags=re.DOTALL).strip()
        logging.info(f"Extracted answer: {len(final_answer)} chars")
    else:
        # No think tags found
        logging.warning(f"No <think> tags found in response.")
        final_answer = full_response.strip()

    # Format final answer with bold markdown
    final_answer = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", final_answer)

    logging.info(f"RESPONSE to {user_name}: {final_answer[:200]}...")

    # Add messages to conversation history
    add_to_conversation_history(user_id, 'user', update.message.text)
    add_to_conversation_history(user_id, 'assistant', full_response)

    # Send the final response
    try:
        if final_answer:
            await update.message.reply_text(final_answer, parse_mode=ParseMode.HTML)
        else:
            # Fallback if parsing failed
            clean_response = re.sub(r"<think>.*?</think>\s*", "", full_response, flags=re.DOTALL).strip()
            clean_response = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", clean_response)
            await update.message.reply_text(clean_response, parse_mode=ParseMode.HTML)
    except Exception as e:
        logging.warning(f"Failed to send message: {e}")