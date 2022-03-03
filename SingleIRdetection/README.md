# QTLab2122 - Single IR photon detection
Laboratory of Solid State and Quantum Technologies  
Laboratory classe for the Master's degree in Physic at the University of Milano-Bicocca.  
Official e-learning page [here](https://elearning.unimib.it/course/view.php?id=39139).

## Contributors
- [Eleonora Cipelli](https://github.com/EleonoraCipelli)     (mail: [e.cipelli@campus.unimib.it](mailto:e.cipelli@campus.unimib.it))
- [Pietro Campana](https://github.com/PietroCampana) (mail: [p.campana1@campus.unimib.it](mailto:p.campana1@campus.unimib.it))
- [Rodolfo Carobene](https://github.com/rodolfocarobene)     (mail: [r.carobene@campus.unimib.it](mailto:r.carobene@campus.unimib.it))

## How to use
After downloading any file, be sure to have all requirements. You can install all packages downloading **requirements.txt** and by running:
```
pip install -r requirements.txt
```

## Directories and Files description
* **notebooks:** some example of how to use scripts and classes
<br/><br/>
* **requirements.txt:** list of all required packages
* **README.MD:** this file!
<br/><br/>
* **instruments.py:** contains classes to communicate with Oxford ITC503 and HP VNA
* **resonance.py:** containes clases to analyze resonances, fit them and find the energy gap
* **tutto_ok.py:** a script to check if cryostate is behaving as expected, otherwise sends an e-mail alert
* **get_data.py:** a script to get acquire resonance spectra at different temps
