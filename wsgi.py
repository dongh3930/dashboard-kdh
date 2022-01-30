from app.main import app
import os 

server = app.server
if __name__ == "__main__":
        app.run_server(host='0.0.0.0', port=port, debug=True)
