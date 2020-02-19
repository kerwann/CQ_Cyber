


class mc2:

    """Defines an mc2 class with the required attributes"""

    def __init__(self, 
                 measdate = "", linac = "", modality = "", inplane_axis ="", crossplane_axis="", 
                 depth_axis = "", inplane_axis_dir = "", crossplane_axis_dir = "", depth_axis_dir = "", 
                 energy = "", ssd = "", field_inplane = "", field_crossplane = "", scan_curvetype = "", 
                 scan_depth = "", scan_offaxis_inplane = "", scan_offaxis_crossplane = "", meas_time = "", 
                 meas_unit = "", xdata = "", ydata = "", refdata = "", scan_diagonal = ""):
        """ Constructs the object mc2 """
        self.measdate = measdate
        self.linac = linac
        self.modality = modality
        self.inplane_axis = inplane_axis
        self.crossplane_axis = crossplane_axis
        self.depth_axis = depth_axis
        self.inplane_axis_dir = inplane_axis_dir
        self.crossplane_axis_dir = crossplane_axis_dir
        self.depth_axis_dir = depth_axis_dir
        self.energy = energy
        self.ssd = ssd
        self.field_inplane = field_inplane
        self.field_crossplane = field_crossplane
        self.scan_curvetype = scan_curvetype
        self.scan_depth = scan_depth
        self.scan_offaxis_inplane = scan_offaxis_inplane
        self.scan_offaxis_crossplane = scan_offaxis_crossplane
        self.meas_time = meas_time
        self.meas_unit = meas_unit
        self.xdata = xdata
        self.ydata = ydata
        self.refdata = refdata
        self.scan_diagonal = scan_diagonal

        
    def setVariables(self, measdate, linac, modality, inplane_axis, crossplane_axis, 
                 depth_axis, inplane_axis_dir, crossplane_axis_dir, depth_axis_dir, 
                 energy, ssd, field_inplane, field_crossplane, scan_curvetype, 
                 scan_depth, scan_offaxis_inplane, scan_offaxis_crossplane, meas_time, 
                 meas_unit, xdata, ydata, refdata, scan_diagonal):
        """ Fills the variables """
        self.measdate = measdate
        self.linac = linac
        self.modality = modality
        self.inplane_axis = inplane_axis
        self.crossplane_axis = crossplane_axis
        self.depth_axis = depth_axis
        self.inplane_axis_dir = inplane_axis_dir
        self.crossplane_axis_dir = crossplane_axis_dir
        self.depth_axis_dir = depth_axis_dir
        self.energy = energy
        self.ssd = ssd
        self.field_inplane = field_inplane
        self.field_crossplane = field_crossplane
        self.scan_curvetype = scan_curvetype
        self.scan_depth = scan_depth
        self.scan_offaxis_inplane = scan_offaxis_inplane
        self.scan_offaxis_crossplane = scan_offaxis_crossplane
        self.meas_time = meas_time
        self.meas_unit = meas_unit
        self.xdata = xdata
        self.ydata = ydata
        self.refdata = refdata
        self.scan_diagonal = scan_diagonal
        
        
    def datasetinfo(file):
        """Finds datasets within a file and returns some useful info so you can decide
        which one you need
        Returns the start and end lines, acquisition date, energy,field size, direction and depth
        Call as 'DataStart, DataEnd, MeasDate, Energy, FieldSize, Depth=datasetinfo(inputfile)' """

        datasets = 0
        ifile = open(file, 'r') 
        lines = ifile.readlines()
        datasets = 0
        lineNumber = 0
        BeginScan=[]; EndScan=[]; MeasDate = []; Energy = []; FieldSize=[]; Depth=[]; Direction=[]
        for line in lines:
            line = line.replace('\t', ',')      # replaces all the tabs with commas
            line = line.rstrip('\r\n')            # strips any control characters from the end of the line

            if ("BEGIN_SCAN" in line) and ("DATA" not in line):
                BeginScan.append(lineNumber)
                datasets = datasets+1

            if "MEAS_DATE" in line:
                MeasDate.append(line.split("=")[1])

            if "ENERGY" in line:
                Energy.append(int((line.split("=")[1]).split('.')[0]))
                # This rather convoluted line extracts the integer from a string 
                # e.g the string "6.00" is converted to the integer "6"
                #  Energy=(int(line.split('.')[0]))

            if "SCAN_DEPTH=" in line:
                Depth.append(int((line.split("=")[1]).split('.')[0]))

            if ("FIELD_INPLANE" in line) and ("REF" not in line):
                FieldSize.append((int((line.split("=")[1]).split('.')[0]))/10) # convert from mm to cm
                # This probably shouldn't be relied upon as the direction
                # in the old data appears to be quite unreliable.
                # The filename appears to be a more reliable guide to the scan direction!

            if "SCAN_CURVETYPE=" in line:
                answer = (line.split("=")[1])
                if (line.split("=")[1]) == "CROSSPLANE_PROFILE":
                    Direction.append("AB(X)")
                if (line.split("=")[1]) == "INPLANE_PROFILE":
                    Direction.append("GT(Y)")

            if ("END_SCAN" in line) and ("DATA" not in line):
                EndScan.append(lineNumber)

            lineNumber = lineNumber + 1
                
        return BeginScan, EndScan, MeasDate, Energy, FieldSize, Depth, Direction

        
    def extractdata(self, line):
        """For each line, return the x and y values, check whether there is reference value
        and if so return the reference value, otherwise return a reference	value of 1 """
    
        newArray = (line.split(','))
            
        if len(newArray) == 8:
            # convert the strings to floats
            xvalue = float(newArray[3])
            yvalue =  float(newArray[5])
            if (newArray[7][0]=='#'):
                refvalue = float(newArray[7][1:])
            else:
                refvalue =  float(newArray[7])
            return xvalue, yvalue, refvalue
    
        if len(newArray) == 6:
            # convert the strings to floats
            xvalue = float(newArray[3])
            yvalue =  float(newArray[5])
            refvalue = 1
            return xvalue, yvalue, refvalue
        else:
            print("Houston, we have a problem, This line does not appear to be data!:")
            print(line)
        
        
        
    def read_profile_srs(self, file, datastartline, dataendline):
        """Read data from the mc2 file and fills the instance of the mc2 class
        As files can contain more than one dataset the start and end line numbers
        need to be supplied.
        These can be obtained using datasetinfo(file)
        Use as dataset = read_mc2(file, datastartline, dataendline)"""

        lineNumber = 0
        dataline = 0
        ifile = open(file, 'r') 
        lines = ifile.readlines()
        linac="N/A"  # earlier versions of the mc2 software didn't include this field, if it is missing then N/A will be returned instead

        for line in lines:
            line = line.replace('\t', ',')  # replaces tabs with commas
            line = line.rstrip('\r\n')         # strips control characters from the end of the line

            if (lineNumber > datastartline) and (lineNumber < dataendline):
                if "MEAS_DATE" in line:
                    self.measdate = (line.split("=")[1])

                elif "LINAC" in line:
                    self.linac = (line.split("=")[1])

                elif "MODALITY=" in line:
                    self.modality = (line.split("=")[1])

                elif "INPLANE_AXIS=" in line:
                    self.inplane_axis = (line.split("=")[1])

                elif "CROSSPLANE_AXIS=" in line:
                    self.crossplane_axis = (line.split("=")[1])

                elif "DEPTH_AXIS=" in line:
                    self.depth_axis = (line.split("=")[1])

                elif "INPLANE_AXIS_DIR=" in line:
                    self.inplane_axis_dir = (line.split("=")[1])

                elif "CROSSPLANE_AXIS_DIR=" in line:
                    self.crossplane_axis_dir = (line.split("=")[1])

                elif "DEPTH_AXIS_DIR=" in line:
                    self.depth_axis_dir_tmp = (line.split("=")[1])

                elif "ENERGY" in line:
                    self.energy = (float((line.split("=")[1]).split('.')[0])) # converts from text to an integer

                elif "SSD=" in line:
                    self.ssd = (float((line.split("=")[1]).split('.')[0])) # converts from text to an integer

                elif ("FIELD_INPLANE" in line) and ("REF" not in line):
                    self.field_inplane =(float((line.split("=")[1]).split('.')[0]))# converts from text to an integer

                elif  ("FIELD_CROSSPLANE" in line) and ("REF" not in line):
                    self.field_crossplane = (float((line.split("=")[1]).split('.')[0])) # converts from text to an integer

                elif "SCAN_CURVETYPE" in line:
                    self.scan_curvetype = (line.split("=")[1])

                elif "SCAN_DEPTH=" in line:
                    self.scan_depth  = (float(line.split("=")[1])) # converts from text to an integer

                elif "SCAN_OFFAXIS_INPLANE=" in line:
                    self.scan_offaxis_inplane = (float(line.split("=")[1])) # converts from text to an integer

                elif "SCAN_OFFAXIS_CROSSPLANE=" in line:
                    self.scan_offaxis_crossplane = float(line.split("=")[1]) # converts from text to an integer

                elif "MEAS_TIME=" in line:
                    self.meas_time = (line.split("=")[1])

                elif "MEAS_UNIT=" in line:
                    self.meas_unit = (line.split("=")[1])

                elif "SCAN_DIAGONAL=" in line:
                    self.scan_diagonal = (line.split("=")[1])

                elif line.startswith(',,,'):     # this must be our data
                    if dataline == 0:
                        xvalue, yvalue, refvalue = self.extractdata(line)
                        self.xdata = np.zeros(0)
                        self.xdata = xvalue
                        self.ydata = np.zeros(0)
                        self.ydata = yvalue
                        self.refdata = np.zeros(0)
                        self.refdata = refvalue
                    else:
                        xvalue, yvalue, refvalue = self.extractdata(line)
                        self.xdata = np.hstack([self.xdata, xvalue])
                        self.ydata = np.hstack([self.ydata, yvalue])
                        self.refdata = np.hstack([self.refdata, refvalue])
                    dataline = dataline + 1

            lineNumber = lineNumber + 1



class SRSmatrix:

    """Class to be able to read SRS matrix measurements"""

    self.NBPIX_X = 45
    self.NBPIX_Y = 45
    
    def __init__(self):
        """ Constructs the object SRSmatrix 
        img: dose image of the measurements"""
        self.img = np.zeros((self.NBPIX_X, self.NBPIX_Y))



    def readSRSmccFile(self, filepath):
        beginScan, endScan, measDate, energy, fieldSize, depth, direction = mc2.datasetinfo(filepath)
        
        for i in range(len(beginScan)):
            a = mc2()
            a.read_profile_srs(filepath, beginScan[i], endScan[i])
            if (a.scan_curvetype == 'CROSSPLANE_PROFILE'):
                ypos = int(a.scan_offaxis_inplane/2.5)
                for j in range(len(a.xdata)):
                    xpos = int(a.xdata[j]/2.5)
                    self.img[ypos+22, xpos+22] = a.ydata[j]
            elif (a.scan_curvetype == 'INPLANE_PROFILE'):
                if (a.scan_diagonal == 'NOT_DIAGONAL'):
                    xpos = int(a.scan_offaxis_crossplane/2.5)
                    for j in range(len(a.xdata)):
                        ypos = int(a.xdata[j]/2.5)
                        self.img[ypos+22, xpos+22] = a.ydata[j]
                elif (a.scan_diagonal == 'FIRST_DIAGONAL'):
                    for j in range(len(a.xdata)):
                        self.img[j, j] = a.ydata[j]
                elif (a.scan_diagonal == 'SECOND_DIAGONAL'):
                    for j in range(len(a.xdata)):
                        self.img[j, 44-j] = a.ydata[j]
            
        return True 

    
    
    def extrapolateData(self):
        """Extrapolate data to fill the matrix
        That avoids zero values and weird profiles
        <!> Care must be taken in the evaluation of the results!!! """
        newimg = np.zeros((self.NBPIX_X, self.NBPIX_Y))
        for i in range(1,self.NBPIX_X-1):
            for j in range(1,self.NBPIX_Y-1):
                if (self.img[j,i] == 0):
                    s2 = np.sum(self.img[j-1:j+2, i-1:i+2])
                    n = np.count_nonzero(self.img[j-1:j+2,i-1:i+2])
                    newimg[j,i] = s2/n
                else:
                    newimg[j,i] = self.img[j,i]
                
        self.img = newimg
        return True










if __name__ == '__main__':


a = 0

# pour le test des classes...
