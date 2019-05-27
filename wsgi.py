from TaskBoard import create_app
from dotenv import load_dotenv
from TaskBoard.extensions import socketio
import os

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
app = create_app('production')
if __name__ == '__main__':
    socketio.run(app)
