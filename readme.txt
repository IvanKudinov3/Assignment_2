HARBORFLOW PORT INTELLIGENCE CONSOLE - TEAM README

Run instructions
----------------
Command:"busy anaconda of diversity"
Python version tested: Python 3.14.7

Team members and concrete contributions
---------------------------------------
Name:Ivan Kudinov
Contribution: Task 1: List registered vessels. Task 2: Inspect a vessel manifest, task 3: Identify priority cargo.

Name: Toste Lagerström
Contribution: Task 4:Export a customer operation profile. Task 5: Find port calls by month. 

Name:Vladyslav Pasalskyi
Contribution:Task 6: sanitizes an incident report. Task 7: analyzes the longest stable event sequence.

Name: Syed Mujtaba Kazmi
Contribution: Task 8: Assess weather risk for upcoming calls. Task 9: Search incident reports.

Architecture
------------
main.py responsibilities: start the menu, and match the users input with a function. Call the function from the imported .py file.
data_access.py responsibilities: access JSON and csv files in dataset directory
operations.py responsibilities: Contains main functions required for the tasks.
text_tools.py responsibilities: Contains only main functions for task 6 and task 7

File and error-handling design
------------------------------
How paths are resolved:All file paths are constructed dynamically using relative paths based on the project's root directory.
How malformed or missing input is handled: Program uses try with exceptions like FileNotFoundError and json.JSONDecodeError. This prevents program from crashing. Invalid or damaged date are also skipped and counted by list without crashing the current function.
How generated files are updated safely: Existing files are loaded entirely into memory before modyfing them. After saving a file it overwrites it preventing duplicates or losing data.

Known limitations:

1. The program operates on the assumptions that certain keys, rows and columns in CSV and JSON files are present. The program does not check for all the keys in JSON and if one of them is absent, the program would crash. 
2. If incident files that malformed or lack incident_id, title or report are skipped without a message to the user.(Task 6). Between several manifests that share the same call_id, only the first one found will be used.(Task 7)
-----------------
Write "None known" or describe each known limitation.
