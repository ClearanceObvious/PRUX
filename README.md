# PRUX
Python-Rux, Rux version of roblox remade better with proper features and no bugs and little limitations.

# Running prux
Command Prompt:
```
py main.py filename.rux
```


# Language Basics
These are some basics about the RUX language so far

> ### Variables & Arithmetic

```js
let name = "Michael";

let greeting = "Welcome, " + name;

let x = 10;
let y = 5;

let result = x / y + 1;

```

> ### Functions

```js
let greetPerson := (personName) {
  return "Welcome, " + personName + ". Enjoy your stay!";
}

let greeting = greetPerson("Michael");

```

> ### If Statements

```js
let name = "Michael";
let age = 15;

if (name == "Michael" && age == 15) {
  log("Correct!");
} else if (name == "Michael" && age < 15) {
  log("Correct but invalid age!");
} else {
  log("Incorrect");
}
```

> ### Loops

```js
while (true) {
  log("Infinite Loop!");
}

for (let x = 0; !(x >= 10); x += 1) {
  log("Iteration: " + x);
}
```

> ### Arrays

```js
let names = ["Michael", "Chloe", "Sundae"];
log(names[0]);
names[0] = null;
log(names[0]);
```

> ### Objects

```js
let user = [
  name = "Michael";
  age = 15
];

log(user.name);
log(user.age);
```

> ### Importing Files

```js
import "filename.rux"

//Gets imported to the global scope
importedFunction()
```

> ### Exporting

```js
// Returns in the main body of the program signal export calls.
// Only objects are exportable, anything else will result in an error

let x = 100;

return [
  x = x
];

```

# Limitations

> ### Inner Function Scopes
```js
let f1 := (x) {
  let f2 := () {
    return x;   // Does not find x as valid variable
  }
}
```

> ### Nested Function Calls
```js
let f2 := () { return 0; }
let f1 := () { return f2; }

f1()(); //Invalid
```
```js
let func1 := () { return [ 0 ]; }

let functions = [func1, 0];

let zero = functions[0]()[0]; //Invalid
```

# Built In Functions
> ### log
```js
// <null> log(<string> message)

log("Hello World!");
```
> ### sleep
```js
// <null> sleep(<number> amount_of_seconds)

sleep(1);
```
> ### input
```js
// <string> input(<string> input_text)

let answer = input("What's your name?");
log(answer);
```
