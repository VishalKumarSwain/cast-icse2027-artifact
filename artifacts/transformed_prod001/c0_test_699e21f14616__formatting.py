def addTurbine(
    self,
    uniqueID,
    turbineType="SRT",
    diameter=float("NaN"),
    hubHeigt=float("NaN"),
    x_horizontal=float("NaN"),
    y_vertical=float("NaN"),
):
    if uniqueID in self.createdSRTs:
        print(
            "A wind turbine with the same unique ID in wind farm [",
            str(self.uID),
            "] already exists. New turbine not added.",
        )
    else:
        if type(uniqueID) == str and len(uniqueID.split()) == 1:
            if uniqueID in globals().keys():
                print(
                    "A wind turbine witht the same uniqe ID globally exists. New turbine not added."
                )
            else:
                if turbineType == "SRT":
                    globals()[uniqueID] = toUserVariable = SRT(
                        uniqueID,
                        diameter=diameter,
                        hubHeigt=hubHeigt,
                        x_horizontal=x_horizontal,
                        y_vertical=y_vertical,
                    )
                    self.__numOfSRT += 1
                    self.createdSRTs.append(uniqueID)
                elif turbineType == "MRT":
                    globals()[uniqueID] = toUserVariable = MRT(
                        uniqueID,
                        diameter=diameter,
                        hubHeigt=hubHeigt,
                        x_horizontal=x_horizontal,
                        y_vertical=y_vertical,
                    )
                    self.__numOfMRT += 1
                    self.createdMRTs.append(uniqueID)
                else:
                    print("Turbine type not supported")
        else:
            print("Name should be a string without spaces.")
        return toUserVariable
