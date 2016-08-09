# poc-python-decorator
Project to Analyse Java Annotation versus Python Decorator.
See tha Java counterpart in 
[poc-java-annotation](https://github.com/renzon/poc-java-annotation#poc-java-annotation).
Each following session has also links to its counterpart.

This project is using Python 3.5.

## Case 1: Decorator which does nothing

[Java Case 1: Annotation which does nothing](https://github.com/renzon/poc-java-annotation#case-1-annotation-which-does-nothing)

Let's suppose the need for marking methods and only listing their names, without execution.
A Decorator can be used for that. 


### Creating Decorator mark

Decorator is a regular function.
But it receives another function as parameter. 
Thus it's a high order function:

```python
_marked = []

def mark(func):
    _marked.append(func)
    return func
```
### Decorating Functions

So `mark` can be used to mark functions, methods orclasses:

```python
from mark.decorator import mark


def marked_1():
    print('Marked 1')


marked_1 = mark(marked_1)


@mark
def marked_2():
    print('Marked 1')


def not_marked():
    print('Not Marked')
``` 

It's important notice on above code that `@` is only syntactic sugar.
Given a decorator `d` and a function `f`, `f = d(f)` has exactly same effect as:

```python
@d
def f() :
   "f's body"
```

### Listing Decorated Functions

So to list marked functions names:

```python
from mark import decorator
# Need only be imported to mark functions/methods
from mark import marked

if __name__ == '__main__':
    for f in decorator._marked:
        print(f.__name__)

# Output
marked_1
marked_2
```

Worth mentioning that functions keep their usual behavior:

```python
from mark import marked

if __name__ == '__main__':
    marked.marked_1()
    marked.marked_2()
    marked.not_marked()
    
# Output
Marked 1
Marked 2
Not Marked

```

[Java Case 1: Annotation which does nothing](https://github.com/renzon/poc-java-annotation#case-1-annotation-which-does-nothing)

## Case 2: Decorator which does something

[Case 2: Annotation which does something](https://github.com/renzon/poc-java-annotation#case-2-annotation-which-does-something)

A micro framework to measure functions running time can be accomplished using previous approach.
The difference is that decorator need to return another function.
This new function, `wrapper`, will measure the time:

```python
from time import clock


def timing(func):
    def wrapper(*args, **kwargs):
        begin = clock()
        ret = func(*args, **kwargs)
        elapsed = clock() - begin
        elapsed * 1000  # transforming im ms
        print("Function %s executed in %s ms" % (func.__name__, elapsed))
        return ret

    return wrapper
```

Worth mentioning that `wrapper` is not aware of `func` parameters.
So it define a variable number of arguments: `*args, **kwargs`.

Testing timing decorator:

```python
from timing.timer import timing


@timing
def count():
    for i in range(1000):
        print(i)


if __name__ == '__main__':
    count()
    print(count.__name__)


# Output
...
997
998
999
Function count executed in 0.003266999999999999 ms
wrapper
```

Different from Java, the `count` reference is changed at import time.
It holds the value of `wrapper`, a inner function of `timing`.

But this approach has a drawback: it changes the original function name.
Once this an effect not desired there is a built in library to fix it.
So the `wraps`decorator is changed:

```python
from functools import wraps
from time import clock


def timing(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        begin = clock()
        ret = func(*args, **kwargs)
        elapsed = clock() - begin
        elapsed * 1000  # transforming im ms
        print("Function %s executed in %s ms" % (func.__name__, elapsed))
        return ret

    return wrapper
```

Now output shows the original function name:

```
997
998
999
Function count executed in 0.002604999999999996 ms
count
```

[Case 2: Annotation which does something](https://github.com/renzon/poc-java-annotation#case-2-annotation-which-does-something)

# Decorator Framework

Several frameworks use Decorator as base for extension points.
So a Proof of Concept will be implemented to illustrate this.
Thus a simple version of server routing and security is going to be developed on next sections.

## Receiving parameters

[Java - Receiving parameters](https://github.com/renzon/poc-java-annotation#receiving-parameters)

Routing configuration is a common problem that every web framework must deal with.
Some of them use Decorator to configure paths to which a method should respond.
So the first step, again, is creating a Decorator.
But this time it needs to receive paths as parameters:

```python
_routes = {}


def route(*paths):
    def decorator(func):
        for p in paths:
            _routes[p] = func
        return func

    return decorator


def execute(path, *args, **kwargs):
    print('Receiving Request on path: %s' % path)
    if path not in _routes:
        print('404 page not Found')
        return 
    _routes[path](*args, **kwargs)
    
#Output    
Receiving Request on path: /
Acessing root of Example
Receiving Request on path: /user
Accessing user of Example
Username: Manager
Receiving Request on path: /usr
Accessing user of Example
Username: Admin
Receiving Request on path: /notexisting
404 page not Found    
```

It's important noticing an extra function is created to receive paths parameters.
So inside `route` the decorator itself is created and returned to be applied on target functions.
Once it returns `func` itself, there is no need to use `wraps` on this case.
  
[Java - Receiving parameters](https://github.com/renzon/poc-java-annotation#receiving-parameters)
	
## Security

[Java Security](https://github.com/renzon/poc-java-annotation#security)

Security can be solved mixing Decorator with params and generating a new function.
This is the most complex one:

```python
from functools import wraps


def restricted_to(*groups):
    allowed_groups = set(groups)

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if 'group' not in kwargs and len(args) == 0:
                print('No defined group')
                return
            group = kwargs['group'] if 'group' in kwargs else args[0]
            if group in allowed_groups:
                func(*args, **kwargs)
            else:
                print('Group %s cant access this path' % group)

        return wrapper

    return decorator
```
Worth mentioning that this can be used to add cross cutting concerns in whatever framework.
So it can be used to add security:

```python
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
    
#Output
Receiving Request on path: /
Acessing root of Example
Receiving Request on path: /user
Group Manager cant access this path
Receiving Request on path: /usr
Accessing user of Example
Group: Admin
Receiving Request on path: /user
Group Manager cant access this path
Receiving Request on path: /usr
Accessing user of Example
Group: Admin
Receiving Request on path: /notexisting
404 page not Found

```
The last thing it's important notice is that decorator order matters.
Once they are applied down to up, unwanted behavior can occur.
For example changing `route` and `restrict_to` decorators oder:

```python

@restricted_to('Admin')
@route('/user', '/usr')
def user(group):
    print('Accessing user of Example')
    print('Group: ' + group)


# Output

Receiving Request on path: /user
Accessing user of Example
Group: Manager
Receiving Request on path: /usr
Accessing user of Example
Group: Admin
Receiving Request on path: /user
Accessing user of Example
Group: Manager
Receiving Request on path: /usr
Accessing user of Example
Group: Admin
```

So in this case `route` would map an unsecured function which can be dangerous.
It would be possible checking routed function before applying security.
Creating a single decorator unifying both would be another solution.
But that is out of scope of this project.

[Java Security](https://github.com/renzon/poc-java-annotation#security)

# Conclusion

To finalize, the table bellow is created to compare Python Decorator versus Java Annotation:

      Feature              |      Python Decorator            |    Java Annotation
---------------------------|----------------------------------|-----------------------------------------------
Alters method/function     | Yes                              | No, need post processing through Reflection
Uses existing language     | Yes, function                    | No, Annotation was created
Uses only Object Orient.   | No, functional programming       | Yes
Unrestricted target        | Yes                              | No, need to define method, class, attribute
Automatic Mapping          | Yes, but module must be imported | No, class scan needed 
Unrestricted params        | Yes                              | No, can't define var args and general classes
Unrestricted param types   | Yes                              | No, only primitives, Class, Enum or array of these types
Param keep code simple     | No, extra level of function      | Yes, only add attribute call
Exec. independent of order | No                               | Yes
Keep target integrity      | No, need fix with wraps          | Yes
# of methods/functions \*  | 3                                | 10
Lines of Code \*\*         | 40                               | 187

\* Counted only for framework. Discarded Java Interfaces. 

\*\* Counted only for framework. Interfaces included

The above the table is construct so "Yes" answer means positive and "No" negative.
So my personal conclusion is that Python Decorator is simpler than Java Annotation.
Besides that, different opinions are very welcome ;)
