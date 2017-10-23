/*********************************************
 * OPL 12.6.0.0 Model
 * Author: oliveras
 * Creation Date: Jun 8, 2017 at 11:46:35 AM
 *********************************************/

 // A
 int numNurses = ...;
 int hours = ...;
 range N = 1..numNurses;
 range H = 1..hours;
 
 int demand [h in H]= ...;
 int minHours = ...;
 int maxHours = ...;
 int maxConsec = ...;
 
 // B
 int maxPresence = ...;
 
 // A
 dvar boolean works[n in N][h in H]; // this set of variable should suffice for A). Tells whether nurse n works at hour h
 
 minimize 1; // do not change this for A)
 subject to {
 
 	// Each nurse should work at least minHours hours
 	forall(n in N)
 	  	sum (h in H) works[n][h] >= minHours;
 	
 	// Each nurse should work at most maxHours hours
 	forall(n in N)
 	  	sum (h in H) works[n][h] <= maxHours;
 	  	
 	// Maximum nurses available
 	forall(h in H)
 	  	 sum(n in N) works[n][h] <= numNurses;
 	  	 
 	// Fulfill demand
 	forall(h in H)
 	  	 sum(n in N) works[n][h] >= demand[h];
 	
 	// Each nurse should work at most maxConsec consecutive hours
 	forall(n in N, h in (1..(hours-maxConsec))) {
 		(sum ( consec in (0..(maxConsec))) works[n][h+consec])<=maxConsec;
 	} 
 }
 
 execute { // Should not be changed. Assumes that variables works[n][h] are used.
  	for (var n in N) {
		write("Nurse ");
		if (n < 10) write(" ");
		write(n + " works:  ");
		var minHour = -1;
		var maxHour = -1;
		var totalHours = 0;
		for (var h in H) {
		  	if (works[n][h] == 1) {
		  		totalHours++;
		  		write("  W");	
		  		if (minHour == -1) minHour = h;
		  		maxHour = h;			  	
		  	}
		  	else write("  .");
   		}
   		if (minHour != -1) write("  Presence: " + (maxHour - minHour +1));
   		else write("  Presence: 0")
   		writeln ("\t(TOTAL " + totalHours + "h)");		  		  
	}		
	writeln("");
	write("Demand:          ");
	
	for (h in H) {
	if (demand[h] < 10) write(" ");
	write(" " + demand[h]);	
	}
	writeln("");
	write("Assigned:        ");
	for (h in H) {
		var total = 0;
		for (n in N)
			if (works[n][h] == 1) total = total+1;
		if (total < 10) write(" ");
		write(" " + total);		
	}		
}  
 
