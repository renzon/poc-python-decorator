# poc-python-decorator
Project to Analyse Java Annotation and compare it with Python Decorator

This project is using Python 3.5

## Case 1: Decorator which does nothing

Let's suppose the need for marking methods and only listing their names.
A Decorator can be used for that. 


### Creating Decorator mark

Decorator is a regular function.
But it receives another function as parameter, so it is a high order function:

```python
_marked = []

def mark(func):
    _marked.append(func)
    return func
```
### Decorating Functions

So `mark` can be used to mark functions/methods/classes:

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

It's important notice from above code that `@` is only syntactic sugar.
Given a decorator `d` and a function `f`, `f = d(f)` has exactly same effect as:

```python
@d
def f() :
   "f's body"
```

### Listing Annotated Methods

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
Marked 1
Not Marked
```

## Case 2: Annotation which does something

A micro framework to measure functions running time can be accomplished using previous approach.
The difference is that Decorator return now need to be another function.
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

Worth mentioning that `wrapper` is not aware of `func`.
So it define e variable number of arguments: `*args, **kwargs`.

Testing de timing function:

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

But this approach has a drawback: it has changes the original function name.
Once this an effect not desired there is a built in library to fix it.
So the :

A class using `Timing`can be also created:

```java
public class Counter {
	@Timing
	public void count() {
		for (int i = 0; i < 1000; ++i) {
			System.out.println(i);
		}
	}
}
```

It's important noting that just like the first case, `count` methods isn't modified:

```java
public static void main(String[] args) {
    new Counter().count();
}
```

Output:
```
...
997
998
999
```
So to calculate execution time a processing class must be developed:

```java
public class TimingRunner {
	public static void time(Object obj)
			throws IllegalAccessException, IllegalArgumentException, InvocationTargetException {
		for (Method m : obj.getClass().getMethods()) {
			if (m.isAnnotationPresent(Timing.class)) {
				long begin = new Date().getTime();
				m.invoke(obj);
				long end = new Date().getTime();
				System.out.println("Method " + m.getName() + " Executed in " + (end - begin) + "ms");
			}
		}
	}

	public static void main(String[] args)
			throws IllegalAccessException, IllegalArgumentException, InvocationTargetException {
		time(new Counter());
	}
```

Now before executing `count` initial time is kept in `begin` variable. 
After its execution elapsed time is calculate and printed:
 
```
...
997
998
999
Method count Executed in 14ms
```

# Annotation Framework

Several frameworks use Annotations as base for extension points.
So a Proof of Concept will be implemented to illustrate this.
Thus a simple version of server routing and security is going to be developed on next sections.

## Receiving parameters

Routing configuration is a common problem that every web framework must deal with.
Some of them use Annotation to configure paths to which a method should respond.
So the first step, again, is creating a Annotation.
But this time it needs defining tha paths:

```java
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.METHOD)
public @interface Route {
	String[] value();
}
```

It's imporant noticing the definition of `value`.
The sintax is different from a class attribute.
It seems line a method execution (`value()`), but it isn't.
Now it can be used to annotate methods:

```java
public class RouteExample {
	@Route("/")
	public void root() {
		System.out.println("Acessing root of Example");
	}

	@Route({ "/user", "/usr" })
	public void user(String username) {
		System.out.println("Acessing user of Example");
		System.out.println("Username: " + username);
	}
}
```

The difference now it that `Route` receives a parameter which is hold by `value`
Four facts worth mentioning:

1. Besides values been a String array (`String[]`) on `root` a simple string `"/"`is given as parameter.
 In one hand it makes code simples once it isn't necessary wrapping unitary parameter as array: `{"/"}`.
 But on the other hand it violates the supposed strong Java typing.
2. An annotation attribute can have any name.
 But if one different from `value` is chosen its name can't be omitted when passing parameter. 
 For example, if `paths` was the attribute's name, then annotated methods should be:
 
 ```java
  @Route(paths="/")
  public void root() {
		System.out.println("Acessing root of Example");
  }
 ```
3. Using a var args would be more consistent for values, but Java currently doesn't accept it on Annotations.
4. Only primitives, String, Class, Enum, Annotation or array of these types can be used as attributes.
 Thus no customized user objects allowed.

## Mapping paths to methods

Once `Router`is in place an Interface for a simple web service is defined:

```java
public interface Server {
	void execute(String path, String... params);

	void scan(Class<?> cls);

	void addSecurity(Class<? extends Annotation> cls, Class<? extends Securitizable> sec);
}
```

The first important method is `scan`.
It's purpose is scanning classes and mapping annotated methods to their paths.
An instance is created so Executor keep references to object and its method for further execution:

```java
Route routeAnnotation = m.getAnnotation(Route.class);
if (routeAnnotation != null) {
    String[] paths = routeAnnotation.value();
    try {

        Object target = cls.newInstance();
        Executor executor = new Executor(target, m);
        for (String path : paths) {
            routes.put(path, executor);
        }
    } catch (Exception e) {}
}
```
With mapped paths server can be used to delegate execution to annotated methods.
Thus Routing is the first extension point of Server's Proof of Concept:

```java
public static void main(String[] args) {
    Server server = new ServerImpl();
    // Scan could be done by libs, but keeping it simple
    server.scan(RouteExample.class);
    // Executing paths
    server.execute("/");
    server.execute("/user", "Manager");
    server.execute("/usr", "Admin");
    server.execute("/notexisting");
}

// Results:

Receiving Request on path: /
Acessing root of Example
Receiving Request on path: /user
Acessing user of Example
Username: Manager
Receiving Request on path: /usr
Acessing user of Example
Username: Admin
Receiving Request on path: /notexisting
404: Page not Found
```
	
## Security

Security issue differs from previous because it modifies execution flow.
The mains idea is provide an extension point so framework users can plug their own Annotations and security handlers.
So an Interface is created to handle security:

```java
public interface Securitizable {
	void check(String path, String... params) throws SecurityException;
	void extracParams(Annotation a);
}
```

Method `extractParams` is responsible for extraction possible configurations parameters from an Annotation.

Methos check is responsible for check execution. 
If it raises `SecurityException` the execution is interrupted.
 
Finalizing `Server`interface provide a configuration method `addSecurity` to connect Annotation with respetive Securitizable.
Interface is repeated here for convenience:

```java
public interface Server {
	void execute(String path, String... params);

	void scan(Class<?> cls);

	void addSecurity(Class<? extends Annotation> cls, Class<? extends Securitizable> sec);
}
```

Once classes are mapped they are used to generate security objects and adding them to `Executor` instances:

```java
private void configureSecurity(Executor executor, Annotation[] annotations)
        throws InstantiationException, IllegalAccessException {
    for (Annotation a : annotations) {
        Class<? extends Annotation> annotationType = a.annotationType();
        if (securityMap.containsKey(annotationType)) {
            Securitizable security = securityMap.get(annotationType).newInstance();
            security.extracParams(a);
            executor.add(security);
        }
    }
}
```

The execution method now includes security checking:

```java
public void execute(String path, String... params) {
    List<Object> list = new LinkedList<>();
    for (String s : params) {
        list.add(s);
    }
    try {
        for (Securitizable s : securities) {
            s.check(path, params);
        }
        // Executed only if each security doesn't throw Security Exception
        method.invoke(target, list.toArray());
    } catch (SecurityException e) {
        e.printStackTrace();
    } catch (Exception e) {
        // TODO Auto-generated catch block
        e.printStackTrace();
        throw new RuntimeException("Errors in params");
    }
}
```

After all this architecture the extension point can be tested.
First `RestrictTo` Annotation is created to define groups allowed to execute a method:

```java
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.METHOD)
public @interface RestrictTo {
	String[]value();
}
```

Second the respective interface implementation:
 
```java
public class RestrictToSecurity implements Securitizable {
	private Set<String> allowedUsers = new HashSet<>();

	@Override
	public void check(String path, String... params) throws SecurityException {
		if (params.length == 0) {
			throw new SecurityException("No defined user");
		}
		String user = params[0];

		if (!allowedUsers.contains(user)) {
			throw new SecurityException("User " + user + " cant access this path");
		}
	}

	@Override
	public void extracParams(Annotation a) {
		allowedUsers.addAll(Arrays.asList(((RestrictTo) a).value()));
	}
}
```

With those the example class can be modified to add security Annotation:

```java
public class SecurityExample {
	@Route("/")
	public void root() {
		System.out.println("Acessing root of Example");
	}

	@RestrictTo("Admin")
	@Route({ "/user", "/usr" })
	public void user(String username) {
		System.out.println("Acessing user of Example");
		System.out.println("Username: " + username);
	}
}
```

Now the complete Server example can run with security:

```java
public static void main(String[] args) {
    Server server = new ServerImpl();
    // Configuring security
    server.addSecurity(RestrictTo.class, RestrictToSecurity.class);
    // Scan could be done by libs, but keeping it simple
    server.scan(SecurityExample.class);
    // Executing paths
    server.execute("/");
    server.execute("/user", "Admin");
    server.execute("/usr", "Manager");
    server.execute("/notexisting");
}

// Results:

Receiving Request on path: /
Acessing root of Example
Receiving Request on path: /user
Acessing user of Example
Username: Admin
Receiving Request on path: /usr
server.security.SecurityException: User Manager cant access this path
	at server.examples.security.RestrictToSecurity.check(RestrictToSecurity.java:22)
	at server.Executor.execute(ServerImpl.java:97)
	at server.ServerImpl.execute(ServerImpl.java:24)
	at server.examples.security.SecurityMain.main(SecurityMain.java:16)
Receiving Request on path: /notexisting
404: Page not Found
```

Thus the mocro framework is completing showing the use of Annotations to add extension points.
Methods are been routed and security is properly configured using this kind of metadata.

# Conclusion

To finalize, the table bellow is created to compare Python Decorator versus Java Annotation:

      Feature              |      Python Decorator            |    Java Annotation
---------------------------|----------------------------------|-----------------------------------------------
Alters method/function     | Yes                              | No, need post processing through Reflection
Uses existing language     | Yes, function                    | No, Annotation was created
Uses only Object Orient.   | No, functional programming       | Yes
Unrestricted target        | Yes                              | No, need to define method, class, attribute
Automatic Maaping          | Yes, but module must be imported | No, class scan needed 
Unrestricted params        | Yes                              | No, can't define var args and general classes
Param keep code simple     | No, extra level of function      | Yes, only add attribute call
Exec. independent of order | No                               | Yes
Keep target integrety      | No, need fix with wraps          | Yes
# of methods \*            | | 10
Lines of Code \*\*         | | 187

\* Counted only for framework. Discarded Java Interfaces. 

\*\* Counted only for framwork. Interfaces included

The above the table is construct so "Yes" answer is positive and "No' negative.
So my personal conclusion is that Python Decorator is simpler than Java Annotation.
Besides that, different opinions are very welcome ;)
