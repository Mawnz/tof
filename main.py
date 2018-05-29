from tof import TOF, cv2, os, threading
# Flask, render_template used for rendering html templates
from flask import Flask, render_template, json

# https://code.tutsplus.com/tutorials/creating-a-web-app-from-scratch-using-python-flask-and-mysql--cms-22972
# https://stackoverflow.com/questions/21765692/flask-render-template-with-path?rq=1
# Init the app
app = Flask(__name__, template_folder = 'html')

app_thread = None
tof_thread = None

# Simple route
@app.route('/')
def main():
	return render_template('index.html')

@app.route('/times', methods = ['GET'])
def get_current_times():
	return json.dumps(tof_thread.getTimes())

@app.route('/kill', methods = ['GET'])
def killThreads():
	tof_thread.onClose()
	return json.dumps({'message': 'Why you kill me'})
# Run everything
if __name__ == '__main__':
	# Need to run the server on a different thread than the webserver
	tof_thread = TOF()
	#app.run('0.0.0.0', '5000')
	app_thread = threading.Thread(target=app.run, args=())

	tof_thread.start()
	app_thread.start()