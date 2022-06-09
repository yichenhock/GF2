# GF2 Software
## Logic Simulator

### Installation and Development Setup
In your terminal, run the following to clone the git repository
```
git clone https://github.com/yichenhock/GF2.git
```
When using DPO computers running on Linux, run
```
export PATH=/usr/local/apps/anaconda3-5.3.1/bin:$PATH
```
To install required dependencies, pip should be enabled and upgraded to the latest version (ideally). Run
```
python -m pip install -r requirements.txt
```
If wxpython fails to install using pip, ensure Anaconda is installed, and run

```
conda install -c conda-forge/label/gcc7 wxpython
```

This code was developed using Python 3.7 and 3.9, and wxPython version 4.1.1. Older or newer version combinations have not been tested.
The following code has been tested and run on Windows and Linux, except for translation, which has only been tested on Linux.

### Running the Simulator
The logic simulator can be run in two modes:
1) A text-based mode in the terminal
2) A graphical mode using a GUI

To launch the simulator in the terminal, run
```
python logsim/logsim.py -c <file path>
```
Where <file path> refers to the circuit definition input file path.
  
To launch the GUI, run
```
python logsim/logsim.py [<file path>]
```
Note that the file path is optional here. If not provicded, the GUI will prompt the user to browse for a file. 
  
Please note that the circuit definition file must be a .txt file.
  
When running in text-based mode, commands can be input into the terminal to run the simulation. Entering "h" into the terminal will list the possible user commands, such as setting switches or adding/removing monitor outputs.

Upon startup in graphical mode, the GUI that appears will look like this:
![gui_screenshot](https://user-images.githubusercontent.com/35310170/171794423-ec032add-9e44-47c6-aa03-a5c8cd2b14b1.png)
<!-- ![GUI Image](https://user-images.githubusercontent.com/73239265/171258402-575e7b14-da80-4474-a7ec-2107f4d075f9.png) -->

The toolbar at the top has buttons to perform various functions (such as running the program or browsing for circuit defintion files). The "Help" button within the toolbar gives more detailed instructions on how to navigate the GUI.
  
The main canvas is shown on the left of the GUI and displays the signal levels of any monitors defined within the circuit definition file or set later within the GUI. These signal levels will be automatically drawn upon running the simulation. 
  
The panel on the right houses 4 tabs. The "Output" tab acts as the main terminal. The "Circuit Definition" tab allows the circuit definition to be viewed and edited. The "Inputs" tab allows the state of any input devices to be changed (such as turning switches on/off). The "Monitors" tab displays all current monitored outputs and allows the user to add/remove monitors. The "Connections" tab allows existing connections between devices to be viewed and destroyed. New connections can also be created.

### Translation

The program supports automatic translation to simplified Chinese when the system locale is set to match. In Linux, navigate to the level above the folder named logsim and run
	
```
LANG=zh_CH.utf8 python3 logsim/logsim.py [<file path>]
```
	
Translation should be compatible with Windows when the locale is changed, but has not been tested. 
	
For further information regarding how to use the logic simulator, please consult the User Guide.
  
### Unit Tests
All Python modules written for this simulator have associated unit tests.
  
To execute the unit tests, run
```
python -m pytest logsim
```

### Code Conventions
All newly written Python modules should be fully compliant with PEP 8 and PEP 257, including the unit test files. To verify this compliance, ```pycodestyle``` and ```pydocstyle``` are used (libraries included in ```requirements.txt```).
	
To verify compliance using ```pycodestyle``` for a specific file, run
```
python -m pycodestyle <file path>
```

To verify compliance using ```pydocstyle``` for a specific file, run
```
python -m pydocstyle <file path>
```

### Authors
Yi Chen Hock, Michael Stevens, Cindy Wu, 2022
	
Based on work by Mojisola Agboola, 2017
