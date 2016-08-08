from server_poc import server
from server_poc.examples.security.decorator import restricted_to
from server_poc.server import route


@route('/')
def root():
    print('Acessing root of Example')


@route('/user', '/usr')
@restricted_to('Admin')
def user(group):
    print('Accessing user of Example')
    print('Group: ' + group)


if __name__ == '__main__':
    server.execute('/')
    server.execute('/user', 'Manager')
    server.execute('/usr', 'Admin')
    server.execute('/user', group='Manager')
    server.execute('/usr', group='Admin')
    server.execute('/notexisting')
