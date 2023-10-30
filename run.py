from blog import app
import os

app.secret_key = os.urandom(24)
#app.run(debug=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)