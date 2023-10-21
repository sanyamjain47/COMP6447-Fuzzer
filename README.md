# COMP6447-Fuzzer
Fuzzer Assignment for 6447
The idea is we split the "harness", "mutation" and "runner" in 3 different classes.

## Google Doc
https://docs.google.com/document/d/1-9S90sD_a_GG1sMvb5mJPy2Ij4wi4o61JWZzm5MMx8w/edit

Flow of code (JUST AN IDEA):

1. Take the input
2. Check/ Validate what type of the ipnut is it? All the files are in .txt extension so need to take a look into the file.
3. Based on the type, get a Mutation class. It would have some "general" mutation techniques and some specfic techniques to the type of the file.
4. Pass this to the runner which spawns the thread and run the binary against the mutated input.
5. This would check the segfault and hopefully work?

## Setup
```bash
python3 -m pip install --user virtualenv
git clone git@github.com:sanyamjain47/COMP6447-Fuzzer.git
cd COMP6447-Fuzzer
virtualenv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
```
