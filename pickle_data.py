import pickle 
import encode  

def storeData(data,pickleName): 
    dbfile = open(pickleName, 'ab') 
    pickle.dump(data, dbfile)                      
    dbfile.close() 
  
def loadData(pickleName): 
    dbfile = open(pickleName, 'rb')      
    db = pickle.load(dbfile) 
    dbfile.close() 
    return db
