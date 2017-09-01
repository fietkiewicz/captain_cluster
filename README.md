# captain_cluster
Captain Cluster is a graphical utility written in Python for running jobs on a High Performance Computing Cluster (HPCC). It was originally design for use on the HPCC at Case Western Reserve University. It provides convenience for simple workflows where server interaction is limited to running a single script and where there are only a few file transfers to and from the user’s computer. The user must already have a functioning script (either .pbs or .sh). A typical workflow using Captain Cluster would be as follows:

1.	Transfer files (including the main script) from the user’s computer to the server.
2.	Execute the main script. This can be a job script (.pbs) or a shell script (.sh) that submits jobs.
3.	Check whether jobs have finished. 
4.	Transfer files from the server to the user’s computer.

For details on usage, see Captain Cluster User Guide.pdf.

Acknowledgements: The primary software developers were Joonsue Lee, Jess Herringer, and Ethan Platt. Thanks to Hadrian Djohari and Sanjaya Gajurel at Case Western Reserve University for their assistance.

