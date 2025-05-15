Deployment process to a local machine...

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the development server
python run.py

# Load webfront from browser
"http://127.0.0.1:5001/“
