How it works
------------

This README contains manual for generating and calculating answers
to the "Theory without divergences" in turbulence in *d_to_infty* case.

###### Generating all the diagrams in N loops, such that satisfy the requirement of existence of "spine" and "half-spine"
```bash
$ python spine.py
```

or if you want run in parallel:

```bash
$ ipython parallel_spine.py
```

NB: in the parallel case ipcluster MUST be already started with the profile_default.

Results:
* directory `./diags_N_loops/` created
* file `./diags_N_loops/count` created
* files `./diags_N_loops/diag` created – contain lists of dynamic diags that correspond to this static diag


###### Filtering zero diagrams: (it works fast enough, no need to parallelize).
```bash
$ python filter_zero.py
```

Result:
* directory `./diags_N_loops/nonzero` created – contains lists of all nonzero dynamic diagrams

###### Writing down integrands:
```bash
$ ipython parallel_scheduler.py <loops>
```

###### Computations:
```bash
$ ipython parallel_scheduler_maple.py
```

