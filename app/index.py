from flask import Blueprint, render_template, jsonify, request
from openai import OpenAI
from dotenv import load_dotenv
import json
import os
from .sql_server_connection import SQLServerConnection

# Load environment variables from .env file
load_dotenv()

index_bp = Blueprint('index', __name__)
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

@index_bp.route('/')
def index():
    return render_template('index.html')

@index_bp.route('/basket')
def basket():
    return render_template('basket.html')

@index_bp.route('/api/basket', methods=['GET', 'POST'])
def handle_basket():
    if request.method == 'POST':
        # Handle adding items to basket
        return jsonify({'success': True})
    else:
        # Return basket contents
        return jsonify({'items': []})

@index_bp.route('/menu')
def menu():
    # Create SQL Server connection
    sql_conn = SQLServerConnection()
    conn = sql_conn.get_connection()
    
    # Fetch menu items from database
    cursor = conn.cursor()
    cursor.execute("SELECT [ID], [nazwa], [skladniki], [cena], [image_name], [grupa] FROM [TESTAI].[dbo].[burr]")
    menu_items = cursor.fetchall()
    
    # Convert to list of dictionaries for easier handling in template
    menu_data = []
    for item in menu_items:
        menu_data.append({
            'id': item[0],
            'name': item[1],
            'ingredients': item[2],
            'price': item[3],
            'image_name': item[4],
            'category': item[5]
        })
    
    # Close connections
    cursor.close()
    conn.close()
    
    return render_template('menu.html', menu_items=menu_data)

@index_bp.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data['message']
    conversation_history = data.get('history', [])  # Get conversation history from request

    # Debug prints
    print("\n=== Debug Information ===")
    print("Received message:", user_message)
    print("Received conversation history:", json.dumps(conversation_history, indent=2))
    print("History length:", len(conversation_history))

    # Check if we've reached the message limit (5 exchanges = 10 messages including AI responses)
    if len(conversation_history) >= 10:  # 5 user messages + 5 AI responses
        return jsonify({
            "response": "I apologize, but we've reached the maximum number of messages for this conversation. Please clear the chat to start a new conversation.",
            "action": None,
            "history": conversation_history
        })

    # Create system message that defines the AI's capabilities and response format
    system_message = """
    You are a helpful shopping assistant for a restaurant. You can help users:
    1. Add items to their basket
    2. Remove items from their basket
    3. View their basket
    4. Answer questions about the menu

    When users want to add items to their basket, ALWAYS include a JSON action object in your response using this format:
    ACTION: {"type": "add_to_basket", "product": {"id": "item-id", "name": "Item Name", "price": price, "items": ["item1", "item2"]}}

    When users want to remove items, use this format:
    ACTION: {"type": "remove_from_basket", "index": index}

    Include this JSON exactly as shown, on its own line starting with "ACTION: ".
    """

    # Prepare messages including history
    messages = [{"role": "system", "content": system_message}]
    messages.extend([{"role": msg["role"], "content": msg["content"]} for msg in conversation_history])
    messages.append({"role": "user", "content": user_message})

    # Debug print the final messages being sent to OpenAI
    print("\nMessages being sent to OpenAI:")
    print(json.dumps(messages, indent=2))

    # Get chat completion from OpenAI
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )

    # Parse the response and extract any action
    ai_message = response.choices[0].message.content
    print("\nReceived AI response:", ai_message)
    action = None

    # Look for ACTION: in the response
    if "ACTION:" in ai_message:
        try:
            action_text = ai_message.split("ACTION:")[1].split("\n")[0].strip()
            action = json.loads(action_text)
            # Remove the ACTION: line from the displayed message
            ai_message = ai_message.replace(f"ACTION: {action_text}", "").strip()
            print("Extracted action:", action)
        except json.JSONDecodeError:
            print("Failed to parse action JSON")

    # Update conversation history
    conversation_history.append({"role": "user", "content": user_message})
    conversation_history.append({"role": "assistant", "content": ai_message})

    print("\nUpdated conversation history length:", len(conversation_history))
    print("=== End Debug Information ===\n")

    return jsonify({
        "response": ai_message,
        "action": action,
        "history": conversation_history
    })
