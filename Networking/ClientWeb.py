from flask import Flask, request, render_template_string, jsonify
import socket
import json
import threading
import time

# Remote server (Raspberry Pi) IP and port
REMOTE_SERVER_IP = "10.0.0.197"
REMOTE_SERVER_PORT = 5000

app = Flask(__name__)

# Global variables: socket connection with remote server and Lock for synchronization
remote_socket = None
socket_lock = threading.Lock()

def connect_to_remote():
    """Attempt to connect to the remote server and store the socket in global variable."""
    global remote_socket
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((REMOTE_SERVER_IP, REMOTE_SERVER_PORT))
            with socket_lock:
                remote_socket = s
            print("[Client] Connected to remote server.")
            break
        except Exception as e:
            print("[Client] Remote connection failed, retrying in 5 sec:", e)
            time.sleep(5)

# HTML Template: Uses onmousedown/onmouseup for continuous command sending
HTML = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>RC Car Control</title>
  <style>
    button {
      width: 120px;
      height: 50px;
      font-size: 18px;
      margin: 10px;
    }
    .container {
      text-align: center;
      margin-top: 50px;
    }
    .row {
      margin: 10px 0;
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>RC Car Control</h1>
    
    <!-- Row 1: Forward + Forward Turning (continuous) -->
    <div class="row">
      <button id="turnLeftForwardBtn" 
              onmousedown="startCommand('turn_left_forward')" 
              onmouseup="stopCommand()">Turn Left Fwd</button>
      <button id="forwardBtn" 
              onmousedown="startCommand('forward')" 
              onmouseup="stopCommand()">Forward</button>
      <button id="turnRightForwardBtn" 
              onmousedown="startCommand('turn_right_forward')" 
              onmouseup="stopCommand()">Turn Right Fwd</button>
    </div>
    
    <!-- Row 2: Left, Stop, Right (continuous for left/right) -->
    <div class="row">
      <button id="leftBtn" 
              onmousedown="startCommand('left')" 
              onmouseup="stopCommand()">Left</button>
      <button onclick="sendCommand('stop')">Stop</button>
      <button id="rightBtn" 
              onmousedown="startCommand('right')" 
              onmouseup="stopCommand()">Right</button>
    </div>
    
    <!-- Row 3: Backward + Backward Turning (continuous optional) -->
    <div class="row">
      <button id="turnLeftBackwardBtn" 
              onmousedown="startCommand('turn_left_backward')" 
              onmouseup="stopCommand()">Turn Left Bwd</button>
      <button id="backwardBtn" 
              onmousedown="startCommand('backward')" 
              onmouseup="stopCommand()">Backward</button>
      <button id="turnRightBackwardBtn" 
              onmousedown="startCommand('turn_right_backward')" 
              onmouseup="stopCommand()">Turn Right Bwd</button>
    </div>
    
    <!-- Row 4: Speed Control -->
    <div class="row">
      <button onclick="sendCommand('low')">Low Speed</button>
      <button onclick="sendCommand('medium')">Medium Speed</button>
      <button onclick="sendCommand('high')">High Speed</button>
    </div>
  </div>
  
  <script>
    let commandInterval = null;
    
    // Start sending command repeatedly while button is pressed
    function startCommand(command) {
      sendCommand(command); // Send immediately
      commandInterval = setInterval(() => {
        sendCommand(command);
      }, 100); // Send every 100ms
    }
    
    // Stop sending and send 'stop' command when mouse is released
    function stopCommand() {
      if (commandInterval) {
        clearInterval(commandInterval);
        commandInterval = null;
      }
      sendCommand('stop');
    }
    
    // Send single command to backend
    function sendCommand(command) {
      fetch('/command', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command: command })
      })
      .then(response => response.json())
      .then(data => console.log("Command sent:", data))
      .catch(error => console.error("Error:", error));
    }
  </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/command", methods=["POST"])
def command():
    data = request.get_json()
    cmd = data.get("command", "").strip().lower()
    print("[Client] Received command from browser:", cmd)
    with socket_lock:
        if remote_socket:
            try:
                # Send command to remote server (in JSON format)
                message = json.dumps({"command": cmd})
                remote_socket.sendall(message.encode())
                return jsonify({"status": "success", "command": cmd})
            except Exception as e:
                print("[Client] Error sending command to remote server:", e)
                return jsonify({"status": "error", "error": str(e)}), 500
        else:
            return jsonify({"status": "error", "error": "Not connected to remote server"}), 500

def run_flask():
    # Run client web server on 0.0.0.0:8080
    app.run(host="0.0.0.0", port=8080, debug=True, use_reloader=False)

if __name__ == "__main__":
    threading.Thread(target=connect_to_remote, daemon=True).start()
    run_flask()
