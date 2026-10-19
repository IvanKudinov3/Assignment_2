HARBORFLOW PORT INTELLIGENCE CONSOLE - TEAM README

Run instructions
----------------
Command:
Python version tested:

Team members and concrete contributions
---------------------------------------
Name:Ivan Kudinov
Contribution: task 1: List registered vessels, task 2: Inspect a vessel manifest, task 3: Identify priority cargo.

Name:
Contribution:

Name:
Contribution:

Name (if applicable):
Contribution:

Architecture
------------
main.py responsibilities: start the menu, and match the users input with a function. Call the function from the imported .py file.
data_access.py responsibilities: access JSON and csv files in dataset directory
operations.py responsibilities: Contains main functions required for the tasks.
text_tools.py responsibilities: 

File and error-handling design
------------------------------
How paths are resolved: 
How malformed or missing input is handled:
How generated files are updated safely:

Known limitations:

1. The program operates on the assumptions that certain keys, rows and columns in CSV and JSON files are present. The program does not check for all the keys in JSON and if one of them is absent, the program would crash.   
-----------------
Write "None known" or describe each known limitation.
