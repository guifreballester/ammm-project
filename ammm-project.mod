/*********************************************
 * OPL 12.6.0.0 Model
 * Author: s0ck
 * Creation Date: Oct 23, 2017 at 10:32:25 AM
 *********************************************/
int nHours = ...; 
int nNurses = ...; 
range H = 1..nHours; 
range N = 1..nNurses; 
int demand[h in H] = ...;
 
int cores_in_computer[c in C]; 
int threads_in_task[t in T]; 
 
dvar boolean x_w[n in N]; 
dvar boolean x_wr[n in N, h in H]; 

execute {
	for (var c=1;c<=nCPUs; c++){
 		var temp_cores=0;
 		for (var k=1; k<=nCores; k++){
   			temp_cores = temp_cores + CK[c][k];
   		}
   		cores_in_computer[c] = temp_cores; 		  
 	}
 	for (var t=1; t<=nTasks;t++) {
  		var temp_threads=0;
 		for (var h=1; h<=nThreads; h++){
   			temp_threads = temp_threads + TH[t][h];
   		}
   		threads_in_task[t] = temp_threads; 		  
 	} 	  	  
};

// Objective
maximize sum(c in C) z[c];
subject to{
	// Cada Head executat al 100% en un sol core
	forall(h in H)
	  sum(k in K) x_hk[h,k] == 1;
	  
	// Una task, amb tots els seus Threads,
	// sigui executada en els cores d'una sola CPU 
	forall(t in T, c in C)
	  sum(h in H: TH[t][h]==1, k in K: CK[c][k]==1) x_hk[h,k] == threads_in_task[t]*x_tc[t][c];
	  
 	// El total de threads d'un core no superi el recursos 
 	// total del Core
 	forall(c in C, k in K: CK[c][k]==1)
 	   sum(h in H) rh[h] * x_hk[h,k] <= rc[c];
 	   
	// Number of CPUs free
	forall(c in C)
		sum (t in T)x_tc[t][c] <=nTasks*(1-z[c]); 
}