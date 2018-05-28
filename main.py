from tof import TOF, cv2, os
# Flask
from flask import Flask

# Init the app
app = Flask(__name__)

if __name__ == '__main__':
	#tof = TOF()
	#tof.root.mainloop()
	app.run()
	
@app.route('/')
def main():
	return 'Hello world!'