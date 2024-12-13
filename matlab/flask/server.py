from flask import Flask, request, jsonify
from csma_ca_simulation import create_users, simulate_transmission, PRINT_MODE

app = Flask(__name__)

@app.route('/simulate', methods = ['POST'])
def run_simulation():
  try:
    data = request.json
    
    num_users = int(data.get("num_users",40))
    duration = int(data.get("duration", 60))
    rate = int(data.get("rate", 24))
    mode = data.get("mode", "a")
    output_mode = PRINT_MODE.get(data.get("output_mode", 2),PRINT_MODE[2])

    users = create_users(num_users)
    
    result = simulate_transmission(users, duration, rate, mode, output_mode)
    
    return jsonify({
      "success": True,
      "rate": result,
      "details": f"Simulation completed for {num_users} users in {duration} seconds with {output_mode} output mode."
    })
  
  except Exception as e:
    return jsonify({
      "Success": False,
      "error": str(e)
    }),500
    
if __name__ == 'main':
    app.run(host = '0.0.0.0',port = 5000)