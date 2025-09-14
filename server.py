from waitress import serve
from Employee_System.wsgi import application

if __name__ == '__main__':
    serve(application, port='8000')