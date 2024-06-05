
"""def hypersim_setup():
    hypersimDir = r"C:\\OPAL-RT\\HYPERSIM\\hypersim_2023.2.1.o404"
    if not os.path.isdir(hypersimDir):
        print("INVALID HYPERSIM DIRECTORY SPECIFIED IN THE SCRIPT")
        exit(1)
    sys.path.append(os.path.join(hypersimDir, 'Windows', 'HyApi', 'python'))
    import HyWorksApiGRPC as HyWorksApi
    HyWorksApi.startAndConnectHypersim()
    print(os.path.realpath(__file__))
    designPath = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'HVAC_230kV_9Bus_IEEE.ecf')
    print(designPath)
    HyWorksApi.openDesign(designPath)"""

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
            else:
                values = None
            return values
    return None