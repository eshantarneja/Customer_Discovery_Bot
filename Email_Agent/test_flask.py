import os
from flask import Flask, jsonify
from datetime import datetime

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for testing"""
    return jsonify({
        'status': 'healthy', 
        'timestamp': datetime.now().isoformat(),
        'message': 'Flask server is running correctly!'
    })

if __name__ == '__main__':
    print("Starting test Flask server...")
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5001)))
