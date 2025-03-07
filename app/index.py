from flask import Blueprint, render_template, jsonify, request
from openai import OpenAI
from dotenv import load_dotenv
import json
import os
from .sql_server_connection import SQLServerConnection
import requests

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

@index_bp.route('/api/basket/get', methods=['GET'])
def get_basket():
    # Add debug logging
    print("\n=== Basket Debug Information ===")
    print("Raw basket data from request:", request.args.get('basket'))
    print("All request args:", request.args)
    print("Request URL:", request.url)
    
    basket_data = request.args.get('basket')
    if basket_data:
        try:
            # URL decode the basket data before parsing
            decoded_basket = requests.utils.unquote(basket_data)
            print("Decoded basket data:", decoded_basket)
            parsed_basket = json.loads(decoded_basket)
            print("Parsed basket data:", parsed_basket)
            return jsonify({'basket': parsed_basket})
        except json.JSONDecodeError as e:
            print("JSON decode error:", str(e))
            return jsonify({'error': 'Invalid basket data'}), 400
    return jsonify({'basket': []})

@index_bp.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    print("\n=== Chat Debug Information ===")
    print("Raw request data:", data)
    print("Basket data received in chat:", data.get('basket'))
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

    # Update the system message to include information about the basket tool
    system_message = """
    You are a helpful shopping assistant for a restaurant. You can help users:
    1. Add items to their basket
    2. Remove items from their basket
    3. View their basket
    4. Answer questions about the menu
    5. If user question is not related to the menu or basket, say that you are not able to help with that.

    To check the basket contents, use the following function:
    get_basket(basket_data: string) -> list of items

    When users want to add items to their basket, ALWAYS include a JSON action object in your response using this format:
    ACTION: {"type": "add_to_basket", "product": {"id": "item-id", "name": "Item Name", "price": price, "items": ["item1", "item2"]}}

    When users want to remove items, use this format:
    ACTION: {"type": "remove_from_basket", "index": index}

    Include this JSON exactly as shown, on its own line starting with "ACTION: ".
    """

    # Add function calling capability
    tools = [{
        "type": "function",
        "function": {
            "name": "get_basket",
            "description": "Get the current contents of the user's basket",
            "parameters": {
                "type": "object",
                "properties": {
                    "basket_data": {
                        "type": "string",
                        "description": "JSON string containing basket data"
                    }
                },
                "required": ["basket_data"]
            }
        }
    }]

    # Prepare messages including history
    messages = [{"role": "system", "content": system_message}]
    messages.extend([{"role": msg["role"], "content": msg["content"]} for msg in conversation_history])
    messages.append({"role": "user", "content": user_message})

    # Debug print the final messages being sent to OpenAI
    print("\nMessages being sent to OpenAI:")
    print(json.dumps(messages, indent=2))

    # Get chat completion from OpenAI with function calling
    response = client.chat.completions.create(
        model="gpt-4-0125-preview",  # Make sure to use a model that supports function calling
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )

    # Handle the response and tool calls
    ai_message = response.choices[0].message
    tool_calls = ai_message.tool_calls

    # If the AI wants to check the basket
    if tool_calls:
        for tool_call in tool_calls:
            if tool_call.function.name == "get_basket":
                # Instead of using the tool call's basket_data, use the one from the original request
                basket_data = data.get('basket', '[]')  # Get basket data from original request
                print("Using basket data for API call:", basket_data)  # Debug log
                
                # Make the API call to get basket contents
                basket_url = f"{request.host_url}api/basket/get?basket={basket_data}"
                print("Making request to:", basket_url)  # Debug log
                basket_response = requests.get(basket_url)
                basket_contents = basket_response.json()
                print("Basket API response:", basket_contents)  # Debug log

                # Add the basket information to the conversation
                messages.append({
                    "role": "assistant",
                    "content": ai_message.content,
                    "tool_calls": [tool_call]
                })
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(basket_contents)
                })

                # Get a new response with the basket information
                final_response = client.chat.completions.create(
                    model="gpt-4-0125-preview",
                    messages=messages
                )
                ai_message = final_response.choices[0].message

    # Parse the response and extract any action
    print("\nReceived AI response:", ai_message)
    action = None
    
    # Get the content from the ChatCompletionMessage object
    ai_message_content = ai_message.content if hasattr(ai_message, 'content') else str(ai_message)

    # Look for ACTION: in the response
    if "ACTION:" in ai_message_content:
        try:
            action_text = ai_message_content.split("ACTION:")[1].split("\n")[0].strip()
            action = json.loads(action_text)
            # Remove the ACTION: line from the displayed message
            ai_message_content = ai_message_content.replace(f"ACTION: {action_text}", "").strip()
            print("Extracted action:", action)
        except json.JSONDecodeError:
            print("Failed to parse action JSON")

    # Update conversation history with string content, not the object
    conversation_history.append({"role": "assistant", "content": ai_message_content})

    print("\nUpdated conversation history length:", len(conversation_history))
    print("=== End Debug Information ===\n")

    return jsonify({
        "response": ai_message_content,
        "action": action,
        "history": conversation_history
    })
