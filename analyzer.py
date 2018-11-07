"""Traffic metrics calculation

This script calculates several different metrics from the HCM

"""



def main():
    """Run the analyzer with command-line parameters."""

    # parser for command line arguments
    parser = argparse.ArgumentParser(
        description="Calculate traffic metrics.")

    # road model and data input arguments
    parser.add_argument("model", help="road network model")
    parser.add_argument("data", help="traffic data")

    # DEBUG: always print results
    # optional arguments: print/store results 
    # parser.add_argument("-p", "--print", action="store_true",
    #     help="print results to console")
    # parser.add_argument("-s", "--store", action="store_true",
    #     help="store results to file")
    
    args = parser.parse_args() # parse the arguments

    # DEBUG: always print results
    args.print = True


class MetricAnalyzer():
    """docstring for MetricAnalyzer"""
    def __init__(self, road_model, data):
        
        self.model = road_model
        self.data = parse_xml(data)




    def parse_xml(self, data):
        """"""

        """
        result format: list of list of arrays
        [[{},{}],[{},{}]]

[
    [
        { "id":"truck0",
            "x":"-79.279196", "y":"43.766188",
            "angle":"72.706319",
            "type":"truck_truck",
            "speed":"0.720844",
            "pos":"7.920844",
            "lane":{'id':35349336,'lane':2,'type':'internal', 'direction':1}
            "slope":"0.000000"},
        { "id":"truck1",
            "x":"-79.279196", "y":"43.766188",
            "angle":"72.706319",
            "type":"truck_truck",
            "speed":"0.720844",
            "pos":"7.920844",
            "lane":"35349336_2",
            "slope":"0.000000"}
    ],
    [],
    [
        { "id":"truck0",
            "x":"-79.279196", "y":"43.766188",
            "angle":"72.706319",
            "type":"truck_truck",
            "speed":"0.720844",
            "pos":"7.920844",
            "lane":"35349336_2",
            "slope":"0.000000"}
    ]
]


        """
        data_array = None

        return data_array






if __name__ == "__main__":
    # Run the module with command-line parameters.
    main()

