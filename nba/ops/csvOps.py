import csv

def writeToCsv(arrOfArrs, fileName, header=None):
    with open(fileName, "w") as f:
        writer = csv.writer(f,quoting=csv.QUOTE_NONNUMERIC)
        # write header if it exists
        if header != None:
            writer.writerow(header)

        writer.writerows(arrOfArrs)

def appendToCsv(arrOfArrs, filename):
    with open(filename, "a") as f:
        writer = csv.writer(f,quoting=csv.QUOTE_NONNUMERIC)
        writer.writerows(arrOfArrs)