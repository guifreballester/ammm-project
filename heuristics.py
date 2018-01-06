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
    from BRKGA_python import main
    print "Launching BRKGA"
    main.main()
