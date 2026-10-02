# BS_STSP - Battery Swap Stochastic Traveling Salesman Problem

All code, data and results for the paper "Modeling Battery Swap Stochastic Traveling Salesman Problem with Logic-Based Benders Decomposition".


## Structure

```
BSS_TSP/
├── src/                    # code for modeling and acceleration strategies 
│   ├── models/             # model with different formulations
│   │   ├── run_loop.sh     # batch script for run a group of models (e.g B=100)
│   │   ├── model_LBBD.py
│   │   ├── model_B&C.py
│   │   └── ...
│   ├── DP.py               # dynamic programming
│   ├── draw_instance.py
│   ├── draw_stacked_bar.py
│   ├── functions.py        # other functions
│   └── para.py             # parameters for instances and scenarios
├── data/
├── results/
└── README.md
```

## Requirements

- python (3.8.10)
- gurobipy  (3.11.4, with license)
- networkx 
- numpy (optional, for draw_instances.py)
- matplotlib (optional, for draw_instances.py)

## Reproduction

1. clone repository and open:
```bash
cd BS_STSP/src/models
```

2. install required packages and refer to run_loop.bat


3. run a group of models (e.g B=300, default):
```bash
run_loop.bat
```

4. change B in model.py files and run the next group:
```bash
run_loop.bat
```

### Visualization

We provide draw_instance.py for instance visualization, but we suggest referring to https://vrp-rep.github.io/mapper for both instance and route visualization.

### Experimental Results

They are summarized in Table 4 in our paper.

## Model Description

- **model_LBBD.py** - model in logic-based benders decomposition (LBBD) formulation, exact model
  
- **model_B&C.py** - model in branch and check (B&C) formulation, exact model
  
- **model_B&C-DP.py** - model in B&C formulation and the subproblem is solved by dynamic programming (DP), exact model
  
- **model_B&C-DP-ACs.py** - model in B&C formulation and the simple feasibility cut and optimality cut are replaced with analytical cuts (ACs, including exact feasibility cut and inexact optimality cut), inexact model
  
- **model_B&C-DP-AFC.py** - model in B&C formulation and only simple feasibility cut is replaced with analytical feasibility cut (AFC), replace model_B&C-DP-ACs.py especially when B=100, exact model


## Acknowledgments

- We thank Montoya et al. (2017) [[1]](#references) for the dataset.
- We thank the developers of https://vrp-rep.github.io/mapper for the visualization tools



## References

[1] Montoya, A., Guéret, C., Mendoza, J. E., & Villegas, J. G. (2017). The electric vehicle routing problem with nonlinear charging function. *Transportation Research Part B: Methodological*, 103, 87-110. https://doi.org/10.1016/j.trb.2017.02.004

---