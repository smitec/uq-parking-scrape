import requests
import json
from datetime import datetime
from html.parser import HTMLParser

DATA_FOLDER = "./json"

r = requests.get("https://pg.pf.uq.edu.au/embedded")

OUTSIDE = 1
IN_TABLE = 2
IN_ROW = 3
IN_CELL = 4

class ParkingParser(HTMLParser):
    state = OUTSIDE
    results = {}
    cell_index = -1
    row_index = -1
    key = ""

    def handle_starttag(self, tag, attrs):
        if self.state == OUTSIDE:
            if tag == 'table' and dict(attrs).get("id","") == "parkingAvailability":
                self.state = IN_TABLE
                self.row_index = -1
                #print("In Table")
        elif self.state == IN_TABLE:
            if tag == 'tr':
                self.state = IN_ROW
                self.row_index += 1
                self.cell_index = -1
                #print("In Row " + str(self.row_index))
        elif self.state == IN_ROW:
            if tag == 'td' or tag == 'th':
                self.state = IN_CELL
                self.cell_index += 1
                #print("In Cell " + str(self.cell_index))

    def handle_endtag(self, tag):
        #print(tag, self.state)
        if self.state == IN_TABLE and tag == 'table':
            self.state = OUTSIDE
            #print("Back to Outside")
        elif self.state == IN_ROW and tag == 'tr':
            self.state = IN_TABLE
            #print("Back to Table")
        elif self.state == IN_CELL and (tag == 'td' or tag == 'th'):
            self.state = IN_ROW
            #print("Back to Row")

    def handle_data(self,data):
        if self.state == IN_CELL:
            if self.row_index == 0: # Header Row
                #print("Header Row Skip")
               return # Just skip it
            if self.cell_index == 0:
                self.results[data] = [0,0]
                self.key = data
            elif self.cell_index == 1:
                if data == 'Not Monitored':
                    self.results[self.key] = [-1, -1]
                else:
                    self.results[self.key][0] = int(data)
            elif self.cell_index == 2:
                self.results[self.key][1] = int(data)

parser = ParkingParser()
parser.feed(r.text)

time = str(datetime.now())

final = {
        "data": parser.results,
        "response": r.status_code, 
        "timestamp": time
        }

f = open(DATA_FOLDER + "/" + time.replace(" ", "_") + ".json", "w")
f.write(json.dumps(final))
f.close()
