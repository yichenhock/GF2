# GF2 Software
## Logic Simulator

### Installation and Development Setup
In your terminal, run the following to clone the git repository
```
https://github.com/yichenhock/GF2.git
```
When using DPO computers running on Linux, run
```
export PATH=/usr/local/apps/anaconda3-5.3.1/bin:$PATH
```
To install required dependencies, run
```
python -m pip install -r requirements.txt
```

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
  
The panel on the right houses 4 tabs. The "Output" tab acts as the main terminal. The "Circuit Definition" tab allows the circuit definition to be viewed and edited. The "Inputs" tab allows the state of any input devices to be changed (such as turning switches on/off). The "Monitors" tab displays all current monitored outputs and allows the user to add/remove monitors.

For further information regarding how to use the logic simulator, please consult the User Guide.
  
  
### Unit Tests
All Python modules written for this simulator have associated unit tests.
  
To execute the unit tests, run
```
python -m pytest logsim/tests
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
