# mimic
*[ab]using UTF to create tragedy*

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

Example usage:

```
./mimic --list       # Show all of the homographs
./mimic --explain=o  # What crazy things can we do with this letter
cat mimic | ./mimic  # Pipe the source through itself at 1%

# Turn up the knob and save the results
cat mimic | ./mimic --me-harder 25 > mimicked
```
