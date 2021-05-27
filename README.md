# Funnel-Satellite

This project tracks data from http://nestio.space/api/satellite/data and provides information via a Django development server.

## Setup Instructions
These are the steps to run the development server on a computer running Windows with an Ubuntu terminal. The Ubuntu terminal for Windows OS can be installed here: https://ubuntu.com/tutorials/ubuntu-on-windows#1-overview

### Create the environment
* Clone this repository: `$ git clone https://github.com/eleanorstuart/Funnel-Satellite.git`
* Check for a virtualenv installation: `$ virtualenv --version`. If no installation is present, install the module: `$ pip install virtualenv`
* Create a new virtual environment for this project: `$ python3 -m virtualenv funnelenv`
* Enter the virtual environment: `$ source funnelenv/bin/activate`
* Within the project folder install the required packages: `$ pip install -r requirements.txt`

### Run the development server
Open 3 terminals, navigate to the project folder, and enter the virtual environment. 
* The first terminal is used to start Redis: `$ redis-server`
* The second terminal is used to start Celery: `$ celery -A FunnelSatellite worker -B -l INFO`
* The third terminal is used to start Django: `$ python manage.py runserver`
* In your browser, go to http://localhost:8000/ to access the Funnel Satellite Tracker
 


