import numpy as np
import numpy.matlib
from random import randint,shuffle,sample
from itertools import chain

# In the absence of real data, we simulate a keyword matrix. The keword matrix of "m" rows
# (items) and "n" columns (keywords) is a representation of a menu of items represented
# by keywords corresponding to each item. Wherever the keyword applies to the item, the
# corresponding matrix cell takes a 1. For simplicity, genres/clusters are pre-determined.
class SimKeywordMatrix:

    ratioOnes = 1
    mutationProb = 0.3 # in fraction
    numKeywordsPerGenre = 10
    
    def __init__(self, numGenresOfItems, numItemsInEachGenre):
        self.numGenresOfItems = numGenresOfItems
        self.numItemsInEachGenre = numGenresOfItems
        
    @classmethod
    def set_ratioOnes(cls, ones):
        cls.ratioOnes = ones
    
    @classmethod
    def set_mutationProb(cls, mutation):
        cls.mutationProb = mutation
        
    @classmethod
    def set_numKeywordsPerGenre(cls, keys):
        cls.numKeywordsPerGenre = keys
    
    def keywordMatrix(self):
    
        # m, total number of dishes
        totalNumDishes = self.numGenresOfItems*self.numItemsInEachGenre
        # n, total number of keywords
        totalNumKeywords = self.numGenresOfItems*self.numKeywordsPerGenre 
        # add extra colums for serial number and genre/cluster number
        numColKeywordMatrix = totalNumKeywords+2
        
        # initialize mxn matrix
        keywordMatrix = np.zeros((totalNumDishes, numColKeywordMatrix))
        # add dish serial number column
        keywordMatrix[:,0] = np.array(range(totalNumDishes))
        # add dish genre column (numeric, encoded from 0 to numGenresOfItems-1)
        keywordMatrix[:,1] = np.repeat(range(self.numGenresOfItems), self.numItemsInEachGenre)
        
        numOnes = int(self.ratioOnes*self.numKeywordsPerGenre) # ratio of 1's per dish
        numZeros = int(self.numKeywordsPerGenre - numOnes) # ratio of 0's per dish
        numSamples = int(self.mutationProb*self.numKeywordsPerGenre) # of 1's to replace
        idxMat = np.zeros((totalNumDishes,numOnes))
        
        nextGenre = 0 # initialize next genre shift
        nextNativeSpace = 0 # initialize next native space shift
        
        for _ in range(self.numGenresOfItems):
        
            for item in range(self.numItemsInEachGenre): 
        
                # temp array for matrix keywordMat row
                temp = np.array([0] * numZeros + [1] * numOnes) 
                np.random.shuffle(temp) # shuffle order of 1's and 0's
        
                nativeList = list(temp) # create iterable version of temp
                
                # set each value in native list in keywordMat and testKeywordMat
                for i, val in enumerate(nativeList):
                    keywordMatrix[(item+nextGenre),(i+nextNativeSpace+2)] = val
                
                # identify index of each 1 in native space, store in idxMat
                idxMat[(item+nextGenre),:] = np.where(temp == 1)[0] + nextNativeSpace
                # select at random 1's from native space
                newIdx = sample(list(idxMat[(item+nextGenre),:]),numSamples)
                
                # set native and non-native space for re-seeding
                if nextNativeSpace == 0:
                    nonNative = list(range(self.numKeywordsPerGenre,totalNumKeywords))
                                
                elif nextNativeSpace == totalNumKeywords - self.numKeywordsPerGenre:
                    nonNative = list(range(0,nextNativeSpace))
                    
                else:
                    nonNative = list(chain(range(0,nextNativeSpace),\
                    range(self.numKeywordsPerGenre,totalNumKeywords)))
                
                # pick 1's at random from native space, make array
                reseedIdx = sample(nonNative,len(newIdx))
                
                # replace samples with zeros, re-seed 1's in non-native space
                for j, val2 in enumerate(newIdx):
                    keywordMatrix[(item+nextGenre),int(val2)+2] = 0
                    keywordMatrix[(item+nextGenre),reseedIdx[j]+2] = 1  
            
            # advance class and native space
            nextGenre += self.numItemsInEachGenre
            nextNativeSpace += self.numKeywordsPerGenre
        
        return keywordMatrix

# To determine the medoid of each cluster/genre, we first find the distance between 
# each item and all other items. The item whose average distance to all other items is
# the smallest is the medoid of the cluster.
class Medoids:
    
    def __init__(self, keywordMatrix, numGenresOfItems):
        self.keywordMatrix = keywordMatrix
        self.numGenresOfItems = numGenresOfItems

    # Function calculates the SokalMichener distance between each item and all other
    # items. Distance will take a value between 0 and 1. 
    @staticmethod
    def distanceMatrix(keywordMatrix):
        
        binaryMatrix = keywordMatrix[:,2:]
        
        stringLength = np.size(binaryMatrix, axis=1)
        numVectors = np.size(binaryMatrix, axis=0)
        distanceMatrix = np.zeros((numVectors,numVectors))
        
        for idx1 in range(numVectors):
            binaryString1 = binaryMatrix[idx1,:]
            for idx2 in range(idx1+1,numVectors):
                binaryString2 = binaryMatrix[idx2,:]
                numMismatches = np.sum(np.logical_xor(binaryString1, binaryString2))
                distanceMatrix[idx1,idx2] = numMismatches / stringLength
                distanceMatrix[idx2,idx1] = distanceMatrix[idx1,idx2]   
    
        return distanceMatrix
    
    # Calculate medoids of each cluster/genre, that is the item whose average distance
    # to all other items within a cluster is smallest. Returns array of corresponding
    # item indeces.
    def medoidVector(self):
        
        distanceMatrix = self.distanceMatrix(self.keywordMatrix)
        
        clusterAssignments = []
    
        for index in range(self.numGenresOfItems):
            indeces = list(np.where(self.keywordMatrix[:,1] == index)[0])
            clusterAssignments.append(indeces)
        
        # medoids are meaningful only in the number of elements > 2
        medoidList = np.zeros(self.numGenresOfItems)
        
        for cidx in range(self.numGenresOfItems):
            
            # find elements in current cluster
            elementsInCluster = clusterAssignments[cidx]
            numElementsInCluster = len(elementsInCluster)
            
            if numElementsInCluster == 1:
                medoidList[cidx] = elementsInCluster[0]
            elif numElementsInCluster == 2:
                medoidList[cidx] = elementsInCluster[0]
            else:
                avgDistVector = np.zeros(numElementsInCluster)
                
                for nidx in range(numElementsInCluster):
                     currentPoint = elementsInCluster[nidx]
                     otherPoints = np.setdiff1d(elementsInCluster,currentPoint)
                     avgDistVector[nidx] = \
                     np.mean(distanceMatrix[currentPoint,otherPoints])
                
                minDistIdx = list(np.where(avgDistVector == np.min(avgDistVector))[0])
                minDistIdx = minDistIdx[0]
                medoidList[cidx] = elementsInCluster[minDistIdx]
            
            medoidVectors = self.keywordMatrix[medoidList.astype(int),2:]
                
        return medoidVectors

# In the absence of real data we generate random transactional data. The goal is to
# take a list of fictional users (from file 'guestList.npy') and assign one random item
# for each day, simulating daily consumption. Total number of transactions is the product
# of the total number of guests and number of days (31, default).
class SimTransData:
    
    numDays = 31
    
    def __init__(self, guestList, keywordMat):
        self.guestList = guestList
        self.keywordMat = keywordMat
        
    @classmethod
    def set_num_days(cls, days):
        cls.numDays = days
        
    def generateTransData(self):
        
        numDishes = len(self.keywordMat) #number of dishes available
        numGuests = np.arange(1,len(self.guestList),1)
        
        #total number of transactions in x months, for y guests
        numEntries = self.numDays*len(numGuests)
     
        numTestCol = 2 #columns in test matrix
        testRow = 0 # initialize test index
        
        #testConsumptionDataCounts: Dish, GuestID  
        testTransData = np.zeros((numEntries, numTestCol))
        
        for _ in range(self.numDays): #day loop, 31 days default
            for guest in numGuests: #guest loop
                
                dishSerialNum = randint(0,numDishes-1) #set random dish
                            
                #populate Check Sales matrix
                testTransData[testRow,0] = dishSerialNum
                testTransData[testRow,1] = guest
                testRow += 1 #increase testRow by 1
                
        shuffle(testTransData[:0])
        
        return testTransData

# In absence of real data, we generate a hypothetical daily menu, assuming items on
# the menu rotate on any given time period. The default numer of items is ten. The repeat
# factor limits the number of items from the same genre to appear on the menu. Daily
# factor is the ceiling integer of the quotient of number of daily items and number of
# genres in keyword matrix.
class SimDailyMenu:
    
    dailyItems = 10
    
    def __init__(self, numGenres, numItems, labels):
        self.totalNumItems = numGenres*numItems
        self.repeatFactor = int(-(self.dailyItems//-numGenres))
        self.labels = labels

    @classmethod
    def set_daily_items(cls, items):
        cls.dailyItems = items
        
    def generateDailyMenu(self):
        
        dailyMenu = []
        dailyGenres = []

        while  len(dailyMenu) < self.dailyItems:
            item = randint(0,self.totalNumItems-1)
            genre = self.labels[item]
            if item in dailyMenu:
                continue #no dish is repeated
            elif dailyGenres.count(genre) == self.repeatFactor:
                continue #genre appears max = repeatFactor
            else:
                dailyMenu.append(item)
                dailyGenres.append(int(genre))
            
        return dailyMenu, dailyGenres
