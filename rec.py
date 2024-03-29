import numpy as np
import numpy.matlib

# Extracts guest history from simulated transactional data.
class GuestData:
        
    def __init__(self, guest, guestList, keywordMatrix, testTransData):
        self.guestList = guestList
        self.guest = guest
        self.testTransData = testTransData
        self.keywordMatrix = keywordMatrix
       
    # Get indices of specific guest dishes and place all
    # dish serial numbers into array. Finally generate an
    # item matrix of guest's data.    
    def getGuestConsumptionData(self):
        
        guestIdCol = 2
        guestNameCol = 1
        guestIdIdx = int(np.where(self.guestList[:,guestIdCol] == str(self.guest))[0])
        guestName = str(self.guestList[guestIdIdx,guestNameCol])
        
        # testTransactionalData: Item, GuestID
        itemSerialNumberCol = 0
        
        itemIdx = np.where(self.testTransData.T[1] == guestIdIdx)[0]
        itemSerialNum = self.testTransData[itemIdx,itemSerialNumberCol]
        
        guestConsumptionData = np.zeros\
        ((len(itemSerialNum), np.ma.size(self.keywordMatrix,axis=1)))
        
        for row, val in enumerate(itemSerialNum):
            guestConsumptionData[row,:] = self.keywordMatrix[int(val),:]
    
        return guestConsumptionData, itemSerialNum, guestName

# Affinity is a measure of similarity, therefore we want to find the similarity between
# the items consumed and the precalculated genre/cluster medoids. Recency weighting is
# applied to transaction history, giving recent history the greatest emphasis
class Affinity:
    
    def __init__(self, guestConsumptionData, numGenresOfItems, medoidVectors):
        self.numGenresOfItems = numGenresOfItems
        self.guestConsumptionData = guestConsumptionData
        self.medoidVectors = medoidVectors
        
    # Returns pairwise distance of guestConsumptionData vs. medoid vectors    
    @staticmethod
    def pairwiseDistance(binaryString1, binaryString2):
        
        if len(binaryString1) != len(binaryString2):
            raise Exception('Binary strings must be of equal length! \n')
        else:
            stringLength = len(binaryString1)
            
        numMismatches = np.sum(np.logical_xor(binaryString1, binaryString2))
        distance = numMismatches / stringLength
        
        return distance
    
    # Determine affinity
    def getAffinityVector(self):
        
        numDaysOfData = len(self.guestConsumptionData)
        
        # Find distances from guestConsumptionData to precomputed cluster medoids
        distanceMatrixTest = np.zeros((self.numGenresOfItems, numDaysOfData))
        
        for idx1 in range(self.numGenresOfItems):
            for idx2 in range(numDaysOfData):
                distanceMatrixTest[idx1,idx2] = \
                self.pairwiseDistance\
                (self.guestConsumptionData[idx2,:],self.medoidVectors[idx1,:])
                
        # Normalize so that all distances are between 0 and 1
        distanceMatrixTest = distanceMatrixTest/(np.amax(distanceMatrixTest))
        
        # Convert to affinity matrix
        affinityMatrixTest = 1 - distanceMatrixTest
        
        #Impose recency weighting. If "recenceyBlock = 5", the last 5 days affinity
        #values will be given the greatest emphasis, the affinity values from the 5
        #days before will be given second greatest emphasis. The emphasis values
        #decrease exponentially.
        
        recencyBlock= 5
        recencyWeightFactor = 0.8
        factor = 0
        weightVector = np.zeros((1, numDaysOfData))
        
        for idx in range(numDaysOfData,0,-recencyBlock):
            startIdx = idx
            endIdx = max(startIdx-recencyBlock+1, 1)
            weightVector[0,endIdx-1:startIdx] = recencyWeightFactor**factor
            factor += 1
            
        weightVector = np.matlib.repmat(weightVector, self.numGenresOfItems, 1) #duplicate vector
        affinityMatrixTest = affinityMatrixTest * weightVector; #elementwise mult
        affinityVectorTest = np.sum(affinityMatrixTest, axis=1)
        affinityVectorTest = affinityVectorTest / np.sum(affinityVectorTest)
        
        return affinityVectorTest
    
class Recommend:
    
    topResults = 3 #return the given number of top results, default    
    
    def __init__(self, affinityVector, dailyGenres, dailyMenu, itemSerialNum):
        self.affinityVector = affinityVector
        self.dailyGenres = dailyGenres
        self.dailyMenu = dailyMenu
        self.itemSerialNum = itemSerialNum
        
    @classmethod
    def set_top_results(cls, top):
        cls.topResults = top
        
    def generateRecommendations(self):

        #rank recommended genres in descending order
        rankedRecommendedGenres = \
        list(np.flip(np.argsort(self.affinityVector)))
        
        recent = []
        topRecommendations = []
        for rankedGenre in rankedRecommendedGenres:
            for idx, genre in enumerate(self.dailyGenres):
                if rankedGenre == genre:
                    if list(self.itemSerialNum).count(self.dailyMenu[idx]) > 0:
                        recent.append(self.dailyMenu[idx])
                        continue
                    else:
                        topRecommendations.append(self.dailyMenu[idx])
                                               
        return topRecommendations[0:self.topResults], recent
