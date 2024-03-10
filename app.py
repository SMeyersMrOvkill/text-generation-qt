from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QTextEdit
import requests
import keys

class ChatInterface(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()
        self.init_connections()

    def init_ui(self):
        self.setWindowTitle('Simple Chat Interface')

        # Create input and send buttons
        self.input_field = QLineEdit()
        self.send_button = QPushButton('Send')

        # Create output area
        self.output_area = QTextEdit()

        # Set up layout
        layout = QVBoxLayout()
        layout.addWidget(self.input_field)
        layout.addWidget(self.send_button)
        layout.addWidget(self.output_area)

        self.setLayout(layout)
        self.show()

    def init_connections(self):
        self.send_button.clicked.connect(self.send_message)

    def send_message(self):
        message = str(self.input_field.text())
        self.output_area.append(f'You: {message}')
        self.input_field.clear()

        # Send message to OpenAI API and update output area with response
        api_key = keys.API_KEY
        endpoint = 'https://api.together.xyz/v1/chat/completions'
        data = {
            "model": "teknium/OpenHermes-2p5-Mistral-7B",
            "max_tokens": 3035,
            "prompt": f"<|im_start|>user\n{message}<|im_end|>\n<|im_start|>assistant\n",
            "temperature": 0.7,
            "top_p": 0.7,
            "top_k": 50,
            "repetition_penalty": 1,
            "stop": [
                "\n\n\n",
                "<|im_start|>",
                "<|im_end|>",
            ],
            "repetitive_penalty": 1,
            "update_at": "2024-03-10T00:56:13.102Z"
        }

        response = requests.post(endpoint, json=data, headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        })

        if response.status_code == 200:
            response_text = response.json().get("choices")[0].get("message").get("content")
            self.output_area.append(f'AI: {response_text}')
        else:
            self.output_area.append(f"API call failed with status code {response.status_code}\n{response.content}")

if __name__ == "__main__":
    app = QApplication([])
    window = ChatInterface()
    app.exec()
