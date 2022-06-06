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
    ├── notebooks          # Code to analyse data and analysis results
    ├── plot               # Plots 
    ├── plot_IQ            # Plots from IQ conversion
    ├── scripts            # Programs to communicate with the instruments and for the data acquisition
    |    └── src           # Classes of the synthetizer and of the acquisition card + useful functions 
    ├── tests              # Some tests for savgol and trigger
    ├── requirements.txt   # Libraries needed to run the code
    └── README.md          # README file


## Content of the scripts ans src folders

  * ```acquisition.py```: acquire data using PXIe and a trigger (edge or immediate)
  * ```continuos_acquisition.py```: acquire data continuously using PXIe 
  * ```join_hdf5.py```: to join many hdf5 files that contain the same datasets/groups
  * ```logging_config.py```: needed for log files
  * ```loop.py```: to run some scripts in loop 
  * ```mixer_cal.py```: for the mixer calibration
  * ```savgol_filter.py```: to align different sample (needed before the application of the optimum filter)
  * ```scan_freq.py```: perform a scan over a range of frequencies to find the resonances
  * ```segmentation.py```: to divide in samples a continuos acquisition
  * ```synt_control.py```: to set a frequency for the synthetizer or iterate over different frequencies
  * ```threshold.py```: iterate over different thresholds to select the best one for our signals

  * ```FSW_0010.py```: control the synthetizer QuickSynt FSW-0010 
  * ```PXIe_5170R.py```: control the high speed digitizer PXIe-5170R
  * ```utils.py```: generic utility functions

 