from distutils.core import setup
import py2exe

# https://www.pythoncentral.io/py2exe-python-to-exe-introduction/
setup(
		windows = ['main.py'],
		options = {
			'py2exe': {
				'packages': ['tof']
			}
		}
	)