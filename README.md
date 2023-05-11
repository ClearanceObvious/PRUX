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

> ### Built-in Functions
```js
log("Hello!");
sleep(1);
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

# Cool Features
> ### Dynamic If Statements
```js
//Allows Rewrital of Else Statements within blocks and Else if Statements are able to be defined after else statements too
if (1) {

} else if (2) {

} else {

} else if (3) {

} else {

}
```
