# SSH to the pi
# ssh pi@10.1.1.135

# BE SURE TO ACTIVATE THE Flask VENV!!!!!!
source /home/pi/venvs/ZTimeClockWebApp/bin/activate  # just run the activate file on Windows

cd /home/pi/projects/ZTimeClock/Webserver
export FLASK_APP=server  # use set FLASK_APP=server on Windows
# Enable debug mode
export FLASK_ENV=development  # use set FLASK_ENV=development on Windows
flask run --host=0.0.0.0
# http://10.107.200.19:5000/