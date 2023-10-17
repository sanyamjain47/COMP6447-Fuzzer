# COMP6447-Fuzzer
Fuzzer Assignment for 6447
The idea is we split the "harness", "mutation" and "runner" in 3 different classes.

Flow of code (JUST AN IDEA):

1. Take the input
2. Check/ Validate what type of the ipnut is it? All the files are in .txt extension so need to take a look into the file.
3. Based on the type, get a Mutation class. It would have some "general" mutation techniques and some specfic techniques to the type of the file.
4. Pass this to the runner which spawns the thread and run the binary against the mutated input.
5. This would check the segfault and hopefully work?
