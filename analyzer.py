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
        data_array = None

        return data_array






if __name__ == "__main__":
    # Run the module with command-line parameters.
    main()

