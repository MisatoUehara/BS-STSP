@REM Required packages: matplotlib, networkx, gurobipy, numpy.
@REM Note that gurobipy requires a license for large instances.

@REM If you don't have the required packages, please run the following lines in your terminal to install them.
@REM pip install matplotlib
@REM pip install networkx
@REM pip install gurobipy
@REM pip install numpy




@REM If you have all the required python package, you can directly run the following code.
@REM B=100,200,300 need your manual setting in each model.py files. The default value is B=300 km.

python "model_B&C-DP-ACs.py"
python "model_B&C-DP-AFC.py"
python "model_B&C-DP.py"
python "model_LBBD.py"
python "model_B&C.py"
