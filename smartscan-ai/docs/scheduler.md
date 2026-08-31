# Scheduler

The Scheduler module maps logical streams to abstract frequencies (F1..FN). 
It takes model inferences (e.g., predicting that F2 is noisy) and adjusts the logical topology to favor cleaner channels. 

**Note on Safety**: The scheduler operates entirely in a simulation matrix. No commands are dispatched to SDR devices or other real-world radio hardware.
