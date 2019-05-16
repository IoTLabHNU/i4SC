class Cake:
    '''
    This class is used to define what a cake is and save some data that will be used later in the Bakery app
    ...
    Attributes
    ---
    custOr : str
        The order number when a cake is ordered from the baker
        
    zone : str
        The zone the the cake will be dropped off at the end
    
    TagID :
        The Identification number of the current RFID tag
    
    Methods
    -------
    
    getZone()
        Returns the zone of the current object of cake
    
    getCustOr()
        Returns the customer order number of the current object of cake
    
    setZone(zone)
        Sets the drop zone of the current object cake to zone
        
    setCustOr(custOr)
        sets the customer order number of the current object to a new customer order
        
    '''

    def __init__(self,custOr,zone,TagId):
        
        '''
           Parameters 
        --------------
            custOr : str
                The order number when a cake is ordered from the baker.
        
            zone : str
                The zone the the cake will be dropped off at the end.
    
            TagID :
                The Identification number of the current RFID tag.
        
        '''
        self.custOr = custOr
        self.zone = zone
        self.TagId = TagId
    
    def getZone(self):
        '''Returns the zone of the current object of cake
        '''
        
        return self.zone
    
    def getCustOr(self):
        '''Returns the customer order number of the current object of cake'''
        return self.custOr

    def setZone(self, zone):
        '''Sets the drop zone of the current object cake to zone
           
           Parameters
           ----------
           zone: str
               The new Zone the current object cake will have assigned to it.
                
        '''
        self.zone = zone

    def setCustOr(self, custOr):
        '''sets the customer order number of the current object to a new customer order
           
           Parameters
           ----------
           custOr: str
               The new customer order number the current object cake will have assigned to it.
        
        '''
        self.custOr = custOr
