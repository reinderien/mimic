# mimic
*[ab]using UTF to create tragedy*

### Introduction

<img alt="monster" align="right"
     src="https://cloud.githubusercontent.com/assets/1236420/10557120/f1faedfe-746b-11e5-8a7b-671bd3e30691.jpg" />

mimic provokes:
- fun
- frustration
- curiosity
- murderous rage

It's inspired by [this terrible idea](https://twitter.com/peterritchie/status/534011965132120064?lang=en) floating around:

> MT: Replace a semicolon (;) with a greek question mark (;) in your friend's C# code and watch them pull their hair out over the syntax error

There are many more characters in the UTF character set that look, to some extent or another, like others -  homographs. Mimic substitutes common ASCII characters for obscure homographs.

Fun games to play with mimic:
- Pipe some source code through and see if you can find all of the problems
- Pipe someone else's source code through without telling them
- Be fired, and then killed

### Example usage

```
./mimic --list           # Show all of the homographs
./mimic --explain=o      # What crazy things can we do with this letter?
./mimic --me-harder 100  # Type some lines in and mess with every single char
cat mimic | ./mimic      # Pipe the source through itself at 1%

# Turn up the knob and save the results
cat mimic | ./mimic --me-harder 25 > mimicked
```

### Results

Observe the mayhem:

<img alt="some bad code"
     src="https://cloud.githubusercontent.com/assets/1236420/10557275/fe460966-7472-11e5-9929-7d5e54c8f26a.png" />
*"BUT WHY?"*

Or, if you've been mimicked a little harder,

<img alt="some worse code"
     src="https://cloud.githubusercontent.com/assets/1236420/10564914/f7963ae4-7591-11e5-9b45-f123e42b22f4.png" />

### See also

[Wikipedia: Unicode Equivalence] (https://en.wikipedia.org/wiki/Unicode_equivalence)

[Wikipedia: IDN homograph attack](https://en.wikipedia.org/wiki/IDN_homograph_attack)

[Online homograph generator](http://www.irongeek.com/homoglyph-attack-generator.php)
