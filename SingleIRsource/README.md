# QTLab2122 - Development of single IR photon source
Laboratory of Solid State and Quantum Technologies.
Laboratory classe for the Master's degree in Physics at the University of Milano-Bicocca.  
Official e-learning page [here](https://elearning.unimib.it/course/view.php?id=39139).

## How to use "requirements.txt"?
1. Go into the project and run:
```
python -m venv daqenv
```
or
```
virtualenv daqenv
```
2. Now you can "activate" the environment by running the activation script.
```
source daqenv/bin/activate
```
(or **activate.bat**, **activate.ps1** depending on the operating system used)

3. Now you can install all the packages needed with the following line:
```
pip install -r requirements.txt
```
4. To exit the virtual environment use the deactivate command.

## Contributors
- [Aurora Perego](https://github.com/AuroraPerego) (mail: [a.perego39@campus.unimib.it](mailto:a.perego39@campus.unimib.it))
- [Marco Gobbo](https://github.com/marcogobbo)     (mail: [m.gobbo4@campus.unimib.it](mailto:m.gobbo4@campus.unimib.it))

## Project folders
    
    SingleIRsource
    │  
    ├── daqenv             # Virtual environment
    ├── data_analysis      # Code to analyse data and analysis results (no data yet)
    ├── h5_files           # Data acquired will be saved here
    ├── plot               # Plots 
    ├── programs           # Programs to communicate with the instruments and for the data acquisition
    |    └── instruments   # Classes of the synthetizer and of the acquisition card + useful functions 
    ├── simulated          # Analysis on simulated waveform to test some components of the code 
    ├── requirements.txt   # Libraries needed to run the code
    └── README.md          # README file