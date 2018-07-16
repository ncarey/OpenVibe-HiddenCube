import os
from os import listdir
from os.path import isfile, join



from HiddenCubeDataset.scripts.HiddenCube import HiddenCube

#This class is for managing the filestructure in between iterations of
#RSVP during the feedback loop of the PULSD BCI system.
#This class is responsible to reading the output of the BCI, keeping
#track of data elements identified by the BCI, calling a specified
#similarity function to generate more data for the next iteration of
#RSVP and most importantly, staging the images/data for consumption
#by the BCI
class ImageLoader:

    def isCurImgDirPopulated(self):
	return '01.png' in listdir(self.cur_images_dir)

    def clearImageBufferDir(self):
	images = listdir(self.cur_images_dir)
	images.remove('isImageSetReady.txt')
	images.remove('votes.txt')
	for image in images:
		os.remove(join(image_dir,image))

    def isImageSetReadyCheck(self):
	try:
		isReady = open(self.isImageSetReady_file_path, 'r')
		ret = isReady.read()
		isReady.close()
		return ret is '1'
	except:
		#sleep and try again
		time.sleep(2)
		isReady = open(self.isImageSetReady_file_path, 'r')
		ret = isReady.read()
		isReady.close()
		return ret is '1'

    def setImageReadyBuffer(self):
	try:
		readyfile = open(self.isImageSetReady_file_path, 'w')
		readyfile.write('1')
		readyfile.close()
	except:
		time.sleep(2)
		readyfile = open(self.isImageSetReady_file_path, 'w')
		readyfile.write('1')
		readyfile.close()

    def readVotes(self):
	votefile = open(self.vote_file_path, 'r')
	content = votefile.read()
	votes = {}
	lines = content.split('\n')
	for line in lines:
		tmp = line.split()
		if(len(tmp) == 2): #hack
                        votes[tmp[0]] = int(tmp[1])

        if(self.debug == 1):
            print("Read Votes: {0}".format(votes))
            
	return votes

    def clearVotes(self):
	votefile = open(self.vote_file_path, 'w')
	votefile.close()
	
    def isVoteFileEmpty(self):
	return os.path.getsize(self.vote_file_path) == 0




    def __init__(self, project_dir, dataset, image_count, debug):

        self.debug = debug
        
        self.dataset = dataset
        self.image_count = image_count

        #root directory of project, not to be confused with HiddenCube project_dir, which is the dataset directory
        self.project_dir = project_dir
        self.cur_images_dir = join(self.project_dir, "buffers", "CurrentImages")
        self.data_images_dir = join(project_dir, "HiddenCubeDataset", "datasets", dataset.getDatasetName(), "images")
      	self.vote_file_path = join(cur_images_dir, "votes.txt")
	self.isImageSetReady_file_path = join(cur_images_dir, "isImageSetReady.txt")



	#decoder keeps track of metadata for the images in the RSVP 'current images' directory
	#these images are named 01.png 02.png ... NN.png, decoder tracks which images in the
	#hiddenCube dataset these are
        self.decoder = {}

        

        
