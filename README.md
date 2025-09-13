# SolarViewerWeb
This basic web app is designed to render data captured by [GitHub.com/AlexVerrico/SolarMonitor](https://github.com/AlexVerrico/SolarMonitor) into basic displays & graphs.  
You will need to have [GitHub.com/AlexVerrico/SolarMonitor](https://github.com/AlexVerrico/SolarMonitor) configured and running to create & populate the database file.  
Set up the python environment using venv - `python -m venv .venv && ./.venv/bin/python -m pip install -r requirements.txt` (this command may need to be adjusted if you are not running on Linux) 
Once you have all of this, copy config.example.py to config.py, and add your config values, then start the web app using `python main.py`

# WARNING
I have made no effort to find or resolve any security issues with this application. I would advise to only run this on a local network, and never expose it to the internet.