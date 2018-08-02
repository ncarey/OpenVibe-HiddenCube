import os
from os import listdir
from os.path import isfile, join
import shutil
import filecmp
import time
import random

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
            os.remove(join(self.cur_images_dir,image))

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


    def loadBufferWithRandomImages(self, cur_img_index):
        
        random_rotation_files = listdir(self.data_images_dir)
        #randomly select num_cur_images of those to use in RSVP
        sampled_indexes = random.sample(range(1, len(random_rotation_files)), (self.image_count - cur_img_index) + 1)
        
        for index in sampled_indexes:
            cur_img = random_rotation_files[index]
            self.decoder["{num:02d}".format(num=cur_img_index)] = cur_img
            shutil.copy2(join(self.data_images_dir, cur_img), join(self.cur_images_dir, "{num:02d}.png".format(num=cur_img_index)))
            cur_img_index += 1

        return cur_img_index
        

    def process(self):

        if self.isImageSetReadyCheck():
            if(self.debug == 1):
                print("Image Set indicated as ready, ImageLoader sleeping")
        elif self.isVoteFileEmpty():
            if(self.debug == 1):
                print("Image Set indicated as consumed, but no classifier votes output yet. ImageLoader sleeping")
        else:
            #main. isImageSetReady.txt = 0, votes.txt has content
	    # wait a cpl sec just in case p300 accumuator still writing down votes
            # read in votes
            # take top x votes, generate y similar rotations for each
            #   if any top votes are 0, generate y random rotations
            # generate num_images - x*y random rotations 
            #  actually, for now if everything has a vote, we wont do randoms. this shouldnt really happen tho
            # clear curr_images and populate with new set
            # clear votes.txt
            # set isImageSetReady.txt to 1

            print("reading classifier votes and generating new image set for RSVP")
            time.sleep(3)
            votes = self.readVotes()
            self.clearImageBufferDir()
            cur_image_count = 1
            while cur_image_count <= self.image_count:
                #get largest vote, if any
                cur_target_name = max(votes, key=lambda k: votes[k])
                if votes[cur_target_name] != 0:
                    #generate similar rotations
                    #shall we use number of votes to influence num sim rots? probably shouldnt...	
                    dataset_image_ID = self.decoder["{num:02d}".format(num=int(cur_target_name))].replace(".png","")
                    dataset_image_path = join(self.project_dir, "HiddenCubeDataset", "datasets", self.dataset.getDatasetName(), "{0}_similar_rotations".format(dataset_image_ID))
                    #similar rotations...need to fix some magic numbers here, specifically num of rotations generated. One element with lots of votes could dominate next iteration...
                    self.dataset.generateSimilarRotations(principal_angle_ID = dataset_image_ID, rotations = int(votes[cur_target_name]) * 2, similarity_factor = self.similarity_factor)

                    new_images = listdir(dataset_image_path)
                    for new_image in new_images:
                        shutil.copy2(join(dataset_image_path, new_image), join(self.cur_images_dir, "{num:02d}.png".format(num=cur_image_count)))
                        self.decoder["{num:02d}".format(num=cur_image_count)] = new_image
                        cur_image_count += 1;
                        if cur_image_count > image_count:
                            break;
                    votes[cur_target_name] = 0 # so we dont double select

                else:
                    #no votes left, randomize remainder
                    cur_image_count = self.loadBufferWithRandomImages(cur_image_count)

            self.clearVotes()
            self.setImageReadyBuffer()
            
        

    def __init__(self,
                 dataset,
                 log,
                 project_dir = "D:\Workspace\PULSD\OpenVibe-HiddenCube",
                 image_count = 20,
                 seed = -1,
                 similarity_factor = .1,
                 debug = 1):

        self.debug = debug
        
        self.dataset = dataset
        self.log = log
        
        self.image_count = image_count
        self.similarity_factor = similarity_factor
        
        #root directory of project, not to be confused with HiddenCube project_dir, which is the dataset directory
        self.project_dir = project_dir
        self.cur_images_dir = join(self.project_dir, "buffers", "CurrentImages")
        self.data_images_dir = join(self.project_dir, "HiddenCubeDataset", "datasets", self.dataset.getDatasetName(), "images")
        self.vote_file_path = join(self.cur_images_dir, "votes.txt")
        self.isImageSetReady_file_path = join(self.cur_images_dir, "isImageSetReady.txt")

        self.seed = seed
        if self.seed != -1:
            random.seed(self.seed)
        else:
            random.seed()

	#decoder keeps track of metadata for the images in the RSVP 'current images' directory
	#these images are named 01.png 02.png ... NN.png, decoder tracks which images in the
	#hiddenCube dataset these are
        self.decoder = {}


        #setup buffer structure
        self.clearImageBufferDir()
        self.clearVotes()
        #Change this if you want to start with specific image sets
        self.loadBufferWithRandomImages(cur_img_index = 1)
        self.setImageReadyBuffer()


        

        
