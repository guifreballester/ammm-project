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
 dvar boolean working[n in N];
 
 dvar int+ max_h[n in N];
 dvar int+ min_h[n in N];

 dvar boolean worksBefore[n in N][h in 2..hours];
 dvar boolean worksAfter[n in N][h in 1..hours-1];
 dvar boolean rests[n in N][h in H];
 
  minimize sum(n in N) working[n]; // do not change this for A)
 
 subject to {
 
 	// Each nurse should work at least minHours hours
 	forall(n in N)
 	  	sum (h in H) works[n][h] >= minHours * working[n];
 	
 	// Each nurse should work at most maxHours hours && working
 	forall(n in N)
 	  	sum (h in H) works[n][h] <= maxHours * working[n];
 	  	
	  	 
 	// Fulfill demand
 	forall(h in H)
 	  	 sum(n in N) works[n][h] >= demand[h];
 	
 	// Each nurse should work at most maxConsec consecutive hours
 	forall(n in N, h in (1..(hours-maxConsec))) {
 		(sum ( consec in (0..(maxConsec))) works[n][h+consec])<=maxConsec;
 	} 

 	
 	
 	//set max_h
 	forall (n in N, h in H){
 		max_h[n] >= works[n][h] * h;	
 	}
 	
 	//set min_h
 	forall (n in N, h in H){
 		min_h[n] <= h + (1-works[n][h]) *hours;	
 	}
 	
 	//presence
 	forall (n in N){
 		max_h[n] - min_h[n] +1 <= maxPresence;	
 	}
 	
 	
 	
 	//worksBefore
 	forall (n in N, h in 2..hours){
 		sum (h_w in 1..h-1) works[n][h_w] <= worksBefore[n][h] * hours ;	
 	}
 	
 	//worksAfter
 	forall (n in N, h in 1..hours-1){
 		sum (h_w in h+1..hours) works[n][h_w] <= worksAfter[n][h] * hours ;	
 	}
 	
 	//rests
 	forall (n in N, h in H){
 		rests[n][h] == 1-works[n][h];	
 	}
 	
 	//impose no more than 2 rests in a row
 	forall (n in N, h in 2..hours-1){
 		worksAfter[n][h]+worksBefore[n][h]+rests[n][h]+rests[n][h+1] <= 3;	
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
 
