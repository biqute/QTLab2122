# QTLab2122 - Development of single IR photon source 
Laboratory of Solid State and Quantum Technologies.
Laboratory classe for the Master's degree in Physic at the University of Milano-Bicocca.  
Official e-learning page [here](https://elearning.unimib.it/course/view.php?id=39139).

## How to use "requirements.txt"?
1. Go into the project and run:
```
python -m venv .venv
```
("venv" can be whatever you want). In this way you'll create your own environment.

2. Now you can "activate" the environment by running the activation script.
If you are on Windows use 
```
.venv\Scripts\activate.bat
```
otherwise use 
```
source .venv/bin/activate.
```
3. Now you can install all the packages needed with the following line:
```
pip install -r requirements.txt
```
4. To exit the virtual environment use the deactivate command.

N.B.: if you don't want to create a new environment (needed to avoid conflicts), you can just do step 3.