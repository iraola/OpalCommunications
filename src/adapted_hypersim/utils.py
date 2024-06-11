import os
import sys

def hypersim_setup():
    hypersimDir = r"C:\\OPAL-RT\\HYPERSIM\\hypersim_2024.1.0.o39"
    if not os.path.isdir(hypersimDir):
        print("INVALID HYPERSIM DIRECTORY SPECIFIED IN THE SCRIPT")
        exit(1)
    sys.path.append(os.path.join(hypersimDir, 'Windows', 'HyApi', 'python'))
    import HyWorksApiGRPC as HyWorksApi
    HyWorksApi.startAndConnectHypersim()
    print(os.path.realpath(__file__))
    designPath = r"C:\Users\Hypersim\Documents\marcel\HYPERSIM\HYPERSIM_IEEE9Bus_50Hz\HVAC_230kV_9bus_IEEE.ecf"
    print(designPath)
    HyWorksApi.openDesign(designPath) 

def get_type_values(driver, types, indexes):
    suffix = driver.split(".")[-1]
    for type in types.keys():
        if suffix in types[type]:
            if type == "Generator" and len(indexes) == 2:
                values = (['lfVolt', 'lfP'], indexes)
            elif type == "Load" and len(indexes) == 2:
                values = (['Po', 'Qo'], indexes)
            elif type == "Switch" and len(indexes) == 3:
                values = (['STATEa', 'STATEb', 'STATEc'], indexes)
            elif type == "Switch" and len(indexes) == 1:
                values = (['STATEa'], indexes)
            elif type == "Voltmeter" and len(indexes) == 3:
                values = (['Va', 'Vb', 'Vc'], indexes)
            elif type == "Voltmeter" and len(indexes) == 1:
                values = (['Va'], indexes)
            elif type == "Ammeter" and len(indexes) == 3:
                values = (['Ia', 'Ib', 'Ic'], indexes)
            elif type == "Ammeter" and len(indexes) == 1:
                values = (['Ia'], indexes)
            elif type == "Wattmeter" and len(indexes) == 3:
                values = (['Wa', 'Wb', 'Wc'], indexes)
            elif type == "Wattmeter" and len(indexes) == 1:
                values = (['Wa'], indexes)
            elif type == "Varmeter" and len(indexes) == 3:
                values = (['VAa', 'VAb', 'VAc'], indexes)
            elif type == "Varmeter" and len(indexes) == 1:
                values = (['VAa'], indexes)
            else:
                values = None
            return values
    return None