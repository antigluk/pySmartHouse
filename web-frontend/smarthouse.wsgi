import sys
sys.path.insert(0, '/home/aiko/frontend')

activate_this = '/home/aiko/frontend/.env/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

from smarthouse import app as application
