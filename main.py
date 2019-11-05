import numpy as np
import numpy.matlib
import sims, rec
         
# Simulated keyword matrix tunable parameters
numGenresOfItems = 7
numItemsInEachGenre = 7

guestList = np.load('guestList.npy')

guest = input('Enter Your Guest ID (range 100-109): ')
    
# Generate simulated keyword matrix
keywordMatrix = sims.SimKeywordMatrix(numGenresOfItems, numItemsInEachGenre).keywordMatrix()

# Find the medoids of each genre/cluster
medoidVectors = sims.Medoids(keywordMatrix, numGenresOfItems).medoidVector()

# Generate simulated transactional data
days = input('Enter number of days to consider: ')
sims.SimTransData.set_num_days(int(days))
transData = sims.SimTransData(guestList, keywordMatrix[:,2:]).generateTransData()

# Generate a daily menu from all items available 
dailyMenu, dailyGenres = \
sims.SimDailyMenu(numGenresOfItems, numItemsInEachGenre, keywordMatrix[:,1]).generateDailyMenu()

# Extract guest's transactional data
guestConsumptionData, itemSerialNum, guestName = \
rec.GuestData(guest, guestList, keywordMatrix[:,2:], transData).getGuestConsumptionData()
 
# Determine what genres/clusters rank in affinity
affinityVector = \
rec.Affinity(guestConsumptionData, numGenresOfItems, medoidVectors).getAffinityVector()
 
# Get top recommendations and list of recently consumed items from recommended genre
topRecs, recent = \
rec.Recommend(affinityVector, dailyGenres, dailyMenu, itemSerialNum).generateRecommendations()

# Display new recommendations based on today's menu
print('\nHello %s!\n' % (guestName,))
guiDisplay = 'Your recommendations for today:\n\n'
guiString1 = ''
for i in topRecs:
    guiString1 += ('Dish #%s\n' % (i))

numDaysOfData = len(guestConsumptionData)
      
# Display recent dishes consumed from today's menu
print('Your recommendations for today are:\n')
for i in topRecs:
    print('Item #%s' % (i))
      
#Display recent dishes consumed from today's menu
print('\nIn the last %s days, you also tried:\n' % (numDaysOfData,))

if len(recent) == 0:
        print('<no items to show>')
else:
    for k in recent:
        print('Item #%s' % (k))
print('\nfrom today\'s menu.\n')
