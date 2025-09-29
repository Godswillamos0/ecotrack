import os
import sqlite3
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory

# Load env vars
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

# Connect to SQLite (creates file if not exists)
conn = sqlite3.connect("chat_history.db")
cursor = conn.cursor()

# Create table for storing history
cursor.execute("""
CREATE TABLE IF NOT EXISTS chats (
    user_id TEXT,
    role TEXT,
    message TEXT
)
""")
conn.commit()

# Initialize model
llm = ChatGroq(
    groq_api_key=groq_api_key,
    model="llama-3.3-70b-versatile",
    temperature=0.7,
)

# Memory object
memory = ConversationBufferMemory(return_messages=True)

# LangChain conversation wrapper
conversation = ConversationChain(
    llm=llm,
    memory=memory,
    verbose=True
)

# Helper to save chat to DB
def save_message(user_id, role, message):
    cursor.execute(
        "INSERT INTO chats (user_id, role, message) VALUES (?, ?, ?)",
        (user_id, role, message)
    )
    conn.commit()

# Helper to load user history into memory
def load_history(user_id):
    cursor.execute("SELECT role, message FROM chats WHERE user_id=? ORDER BY rowid", (user_id,))
    rows = cursor.fetchall()
    memory.chat_memory.messages.clear()
    for role, msg in rows:
        if role == "user":
            memory.chat_memory.add_user_message(msg)
        else:
            memory.chat_memory.add_ai_message(msg)

# Main chat function
def chat(user_id, user_input):
    # Load history for this user
    load_history(user_id)

    # Generate response
    response = conversation.predict(input=user_input)

    # Save both user + AI messages
    save_message(user_id, "user", user_input)
    save_message(user_id, "ai", response)

    return response

# Example usage
if __name__ == "__main__":
    uid = "user_123"
    print(chat(uid, "What is my name?"))
    #print(chat(uid, "Can you remind me what I just asked?"))

