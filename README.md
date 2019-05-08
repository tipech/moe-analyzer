# MOE analyzer

A tool to calculate and visualize the performance of a traffic system based on specific Measures Of Effectiveness (MOEs), using real or simulated data. The calculations are based on the specifications provided by the US Federal Highway Administration's Highway Capacity Manual, although they are designed to support much higher granularity data. For more information on the MOEs and their calculation, refer to the [HCM](https://ops.fhwa.dot.gov/publications/fhwahop08054/execsum.htm). Also, for information on traffic simulations and road networks, see [SUMO](http://sumo.sourceforge.net/).

This repository contains:
 - the module responsible for the MOE calculation (analyzer)
 - supporting classes and object types (model)
 - a sophisticated web-based GUI for interaction with the module and visualizion of results (ui)
 - a number of sample traffic networks and intersections of various sizes and conditions (samples)


### UI usage
The GUI tool can be executed from the ui directory by using:
`python backend.py`
This will start a Python Flask webserver on localhost:5000, which you can access through a web browser. There you can proceed to select one of the provided sample road networks and appropriate simulations and explore the resulting visualizations of the MOEs under different parameters.

Some features available are:
 - Interactive map of the road network
 - Automatic generation of possible vehicles paths though the network
 - Detailed MOE results for every road network edge, every end-to-end path or the entire system
 - Ability to create custom user-specified systems by combining individual network edges
 - Ability to provide custom Passenger Car Equivalent values for vehicle types
 - Different levels of interpolation for the visualization

Additional user-specified networks and simulation files can be added to the ui/data/networks and ui/data/simulations directories respectively. Thanks to the web UI, it very easy to use the tool in separate browser tabs for comparing different systems/parameters.

![Configuration UI](https://github.com/tipech/moe-analyzer/blob/master/samples/sample_ui_1.png "Configuration UI")

![Results UI](https://github.com/tipech/moe-analyzer/blob/master/samples/sample_ui_2.png "Results UI")


### Calculation process
The algorithm's functionality can be split into 3 steps, network model creation, vehicle data loading and MOE calculation.

##### Network model construction
This part is handled the Nework object in model/network.py . The tools NETCONVERT and NETEDIT are part of the SUMO platform and can be used to obtain a road network .xml file, usually by downloading and converting portions of a map from OpenStreetMap. The program creates "base components", i.e. Junction, Edge and Lane objects, as needed. It then arranges them as a directed network structure and then applies graph theory algorithms to identify all possible paths in the system and especially the shortest paths from entrances to exits.

##### Vehicle data loading
This process is handled by classes in the file analyzer/loaders.py, in a streaming way that would allow for real-time processing of incoming data if that stream was available. Because a generator "loader" object is used, it is very easy to provide different variations of loaders to satisfy different needs, e.g. an XMLloader versus a JSONloader, or a loader that introduces noise into the system for experimenting with robustness.

##### MOEs calculation
The main analyzer component receives the constructed model and starts reading from the data loader module as necessary in order to complete all MOE calculations for a single time instance. Vehicle entries are used to determine which vehicles entered which systems, which left, and which moved within systems. This information is used to increment/decrement vehicle and distance counters for each single-edge or multi-edge system, which are then used to calculate all MOEs according to the HCM formulas. Final results are returned in a large dictionary that contains all values for all metrics for a single instance in time, indexed by the id of the corresponding edge/path/group system.

