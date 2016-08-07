from server_poc import server
from server_poc.server import route


@route('/')
def root():
    print('Acessing root of Example')


@route('/user', '/usr')
def user(username):
    print('Accessing user of Example')
    print('Username: ' + username)


if __name__ == '__main__':
    server.execute('/')
    server.execute('/user', 'Manager')
    server.execute('/usr', 'Admin')
    server.execute('/notexisting')
