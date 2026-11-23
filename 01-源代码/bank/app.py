import os
from api.__init__ import create_app,_configure_cors
app = create_app('development')
_configure_cors(app, 'development')

if __name__ == '__main__':
    app.run(host=os.getenv('FLASK_HOST','127.0.0.1'), port=int(os.getenv('FLASK_RUN_PORT','8080')), debug=os.getenv('FLASK_DEBUG','0') == '1')
