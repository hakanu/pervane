# Example bash script to run pervane locally.
echo "Starting dev server in debug mode"
source envu/bin/activate
cd pervane
python3 serve.py --debug=true --dir=example