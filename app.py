import sys
import os
import json
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit, QPushButton, QWidget, QInputDialog, QMessageBox
from PySide6.QtCore import Qt

import requests

import re

import re

class Formatter:
    def __init__(self, stop_tokens):
        self.stop_tokens = stop_tokens
    
    def user(self, input_text):
        return self.format_text(input_text, 'user')
    
    def bot(self, output_text):
        return self.format_text(output_text, 'bot')
    
    def system(self, prompt):
        return self.format_text(prompt, 'system')
    
    def format_text(self, text, role):
        formatted_text = text
        formatted_text = re.sub(r'\n', '', formatted_text)
        
        if role == 'user':
            formatted_text = self.add_user_tags(formatted_text)
        elif role == 'bot':
            formatted_text = self.add_bot_tags(formatted_text)
        
        return formatted_text
    
    def add_user_tags(self, text):
        formatted_text = text
        
        for stop_token in self.stop_tokens:
            formatted_text = re.sub(r'\b(' + re.escape(stop_token) + r')\b', r'|\1', formatted_text)
        
        return formatted_text
    
    def add_bot_tags(self, text):
        formatted_text = text
        
        for stop_token in self.stop_tokens:
            formatted_text = re.sub(r'\b(' + re.escape(stop_token) + r')\b', r'|\1', formatted_text)
        
        return formatted_text


class InferenceModel:
    def __init__(self, api_key, system_prompt="You are a helpful assistant. Help User with anything."):
        self.endpoint = 'https://api.together.xyz/v1/chat/completions'
        self.headers = {
            "Authorization": f"Bearer {api_key}",
        }
        self.default_params = {
            "model": "teknium/OpenHermes-2p5-Mistral-7B",
            "max_tokens": 4096,
            "temperature": 0.7,
            "top_p": 0.7,
            "top_k": 50,
            "repetition_penalty": 1,
            "stop": [
                "<|im_end|>",
                "<|im_start|>"
            ]
        }
        self.system_prompt = system_prompt
        self.reset_conversation()

    def reset_conversation(self, system_prompt=None):
        self.conversation_history = []
        if system_prompt is not None:
            self.system_prompt = system_prompt
        self.conversation_history.append(f"<|im_start|>system\n{self.system_prompt}<|im_end|>")

    def __call__(self, user_input, **kwargs):
        self.conversation_history.append(f"<|im_start|>user\n{user_input}<|im_end|>")
        prompt = "\n".join(self.conversation_history) + "\n<|im_start|>assistant\n"

        params = self.default_params.copy()
        params.update(kwargs)
        params["prompt"] = prompt

        response = requests.post(self.endpoint, json=params, headers=self.headers)
        response.raise_for_status()

        result = response.json()
        generated_text = result['choices'][0]['message']['content'].strip().replace("\n", "</br>")

        self.conversation_history.append(f"<|im_start|>assistant\n{generated_text}<|im_end|>")

        return generated_text

class ChatWindow(QMainWindow):
    def __init__(self, inference_model):
        super().__init__()
        self.setWindowTitle("Chat with OpenHermes")

        self.inference_model = inference_model

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        self.chat_history = QTextEdit(self)
        self.chat_history.setReadOnly(True)
        self.chat_history.acceptRichText()
        layout.addWidget(self.chat_history)

        send_button = QPushButton("Send", self)
        send_button.clicked.connect(self.send_message)
        layout.addWidget(send_button, alignment=Qt.AlignCenter)

        reset_button = QPushButton("Reset", self)
        reset_button.clicked.connect(self.reset_conversation)
        layout.addWidget(reset_button, alignment=Qt.AlignCenter)

        layout.setStretch(0, 6)  # Set the stretch factor for chat_history to 6
        layout.setStretch(1, 1)  # Set the stretch factor for send_button to 1
        layout.setStretch(2, 1)  # Set the stretch factor for reset_button to 1

    def send_message(self):
        user_input, ok = QInputDialog.getMultiLineText(self, "User Input", "Enter your message:")
        if ok and user_input:
            self.chat_history.append(f"<strong>User:</strong> {user_input}")

            generated_text = self.inference_model(user_input)
            self.chat_history.append(f"<strong>Assistant:</strong> {generated_text}<br/>")

    def reset_conversation(self):
        self.inference_model.reset_conversation()
        self.chat_history.clear()
        self.chat_history.append("<em>Conversation reset.</em>") 

def get_api_key():
    home_dir = os.path.expanduser("~")
    config_file = os.path.join(home_dir, ".snail_gui.json")

    if os.path.exists(config_file):
        with open(config_file, "r") as f:
            config_data = json.load(f)
            api_key = config_data.get("api_key")
            if api_key:
                return api_key

    while True:
        api_key, ok = QInputDialog.getText(None, "API Key", "Enter your API key:")
        if not ok:
            sys.exit(0)

        try:
            inference_model = InferenceModel(api_key)
            test_response = inference_model("Say the word hello.")
            if "hello" in test_response.lower():
                with open(config_file, "w") as f:
                    json.dump({"api_key": api_key}, f)
                return api_key
            else:
                QMessageBox.warning(None, "Invalid API Key", "The provided API key is invalid. Please try again.")
        except Exception as e:
            QMessageBox.warning(None, "Error", f"An error occurred: {str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    api_key = get_api_key()
    inference_model = InferenceModel(api_key)

    window = ChatWindow(inference_model)
    window.show()
    sys.exit(app.exec())