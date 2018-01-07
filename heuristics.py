import numpy as np

# Used to launch the heuristics

print '*' * 50
print "Welcome!"
print "Chose which heuristic to run: "
print "1 - GRASP"
print "2 - BRKGA"
heuristic = int(raw_input("Enter a number (1 or 2): "))
while heuristic not in (1, 2):
    print "Choose either 1 or 2"
    heuristic = int(raw_input("Enter a number (1 or 2): "))

if heuristic == 1:
    from GRASP import data

    print "Choose an instance to run"
    print "1 - Easy"
    print "2 - Medium"
    print "3 - Hard"
    instance = int(raw_input("Enter a number (1, 2 or 3): "))
    while instance not in (1, 2, 3):
        print "Choose either 1, 2 or 3"
        instance = int(raw_input("Enter a number (1 or 2): "))
    data.data = getattr(data, "data_%d" % instance)
    from GRASP import grasp

    print "Launching GRASP"
    time_taken = []
    solutions = []
    for alpha in np.arange(0.0, 1.0, 0.05):
        print "Starting again with alpha: ", alpha
        grasp.ALFA = alpha
        t, sol = grasp.grasp()
        time_taken.append(t)
        solutions.append(sol)

        print "Total time for each iteration", time_taken
        print "\n"
        print "Solutions for each iteration", solutions
else:
    from BRKGA_python import data
    print "Choose an instance to run"
    print "1 - Easy"
    print "2 - Medium"
    print "3 - Hard"
    instance = int(raw_input("Enter a number (1, 2 or 3): "))
    while instance not in (1, 2, 3):
        print "Choose either 1, 2 or 3"
        instance = int(raw_input("Enter a number (1 or 2): "))
    data.data = getattr(data, "data_%d" % instance)
    print "Launching BRKGA"
    from BRKGA_python import main

    main.main()
