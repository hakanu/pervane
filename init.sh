init_or_update() {
        echo "Initializing or updating"
	deactivate
	if [ -d "$DIR" ]; then
		echo "Virtualenv is already initialized"
	else
                echo "Initializing virtualenv..."
		virtualenv -p python3 env
	fi
	source env/bin/activate
	pip install flask markdown2 Flask-Caching Flask-HTTPAuth

	# Download the latest version.
	wget https://raw.githubusercontent.com/hakanu/pervane/master/serve.py
}

start() {
	echo "Running the server"
	export FLASK_APP=serve.py;  flask run 
}

init_or_update
start

