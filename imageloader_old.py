import time
import random
from optparse import OptionParser
import subprocess
import os
from os import listdir
from os.path import isfile, join
from math import *
import multiprocessing
import numpy
import filecmp
import shutil

from HiddenCubeDataset.scripts.HiddenCube import HiddenCube

def clearCurrentImages(image_dir):
	images = listdir(image_dir)
	images.remove('isImageSetReady.txt')
	images.remove('votes.txt')
	for image in images:
		os.remove(join(image_dir,image))


def setIsImageSetReady(readyfilename):
	try:
		readyfile = open(readyfilename, 'w')
		readyfile.write('1')
		readyfile.close()
	except:
		time.sleep(2)
		readyfile = open(readyfilename, 'w')
		readyfile.write('1')
		readyfile.close()

def readVotes(votefilename):
	votefile = open(votefilename, 'r')
	content = votefile.read()
	votes = {}
	lines = content.split('\n')
	for line in lines:
		tmp = line.split()
		if(len(tmp) == 2): #hack
                        votes[tmp[0]] = int(tmp[1])
	print("Read Votes: {0}".format(votes))
	return votes

def clearVotes(votefilename):
	votefile = open(votefilename, 'w')
	votefile.close()

def isCurImgDirPopulated(imgdirpath):
	return '01.png' in listdir(imgdirpath)

def isVoteFileEmpty(votefilename):
	return os.path.getsize(votefilename) == 0

def isImageSetReadyCheck(readyfilename):
	try:
		isReady = open(readyfilename, 'r')
		ret = isReady.read()
		isReady.close()
		return ret is '1'
	except:
		#sleep and try again
		time.sleep(2)
		isReady = open(readyfilename, 'r')
		ret = isReady.read()
		isReady.close()
		return ret is '1'
	
if __name__=='__main__':
	
	usage='''look at -h option'''

	parser = OptionParser(usage=usage)

	parser.add_option("-n", "--name", type="string", dest="setname", default="testSet", help="Specify the name of the dataset. Data will be put in a $RSVP_DATA_HOME/datasets/<name>/ directory. Directory will be wiped prior to creating dataset.", metavar="#NAME")

	parser.add_option("-d", "--dimensions", type="int", dest="dims", default="5", help="Specify how many dimensions of data to produce. The first three dimensions will form coordinates for the cube, the remaining dimensions will be uniform random noise between -2 and 2", metavar="#DIMS")

	parser.add_option("-s", "--seed", type="int", dest="seed", default="-1", help="Specify a seed for the random num generator. -1 uses current time as seed", metavar="#SEED")

	parser.add_option("-m", "--dimensionsize", type="int", dest="N", default=1500, help="Specify how many data points total per dimension", metavar="#N")

	parser.add_option("-r", "--rotations", type="int", dest="rotations", default=400, help="Specify how many random rotations of the dataset to perform", metavar="#ROTS")

	parser.add_option("-p", "--parallelization", type="int", dest="para", default=2, help="Specify how many parallel processes to use when generating random rotations", metavar="#PARA")

	parser.add_option("-v", "--similarityfactor", type="float", dest="similarfac", default=0.1, help="Specify how similar the rotations should be (TODO: experiment with this)", metavar="#SIMI")

	(options, args) = parser.parse_args()

        	
	#temporary
	num_cur_images = 20
	project_dir = "D:\Workspace\PULSD\OpenVibe-HiddenCube"
	#middle = os.environ["OPENVIBE_MIDDLE"] # or some other path variable
	cur_images_dir = join(project_dir, "buffers", "CurrentImages")
	data_images_dir = join(project_dir, "HiddenCubeDataset", "datasets", options.setname, "images")
	vote_file_path = join(cur_images_dir, "votes.txt")
	isImageSetReady_file_path = join(cur_images_dir, "isImageSetReady.txt")

	#decoder keeps track of metadata for the images in the RSVP 'current images' directory
	#these images are named 01.png 02.png ... NN.png, decoder tracks which images in the
	#hiddenCube dataset these are
	decoder = {}


	#create HiddenCubeDataset object

	cube = HiddenCube(project_directory = join(project_dir, "HiddenCubeDataset"),
                          dataset_name = options.setname, n_dimensions = options.dims,
                          dimension_size = options.N,
                          randn_seed = options.seed,
                          hypersphere_noise_multiplier = 4,
                          parallelization = 2,
                          notebook_plotting = False)

	
	looping = True
	while looping:
		#case 0: isImageSetReady.txt contains 1. 
		# goto sleep, everything is set and openvibe about to start RSVP
		if isImageSetReadyCheck(isImageSetReady_file_path):
			print("Image Set indicated as ready, sleeping")
			time.sleep(5)

		#case 0.5: isImageSetReady.txt contains 0, but votes.txt is empty and there are images in cur_images_dir. 
		# goto sleep, openvibe currently in RSVP
		elif isVoteFileEmpty(vote_file_path) and isCurImgDirPopulated(cur_images_dir):
			print("Image Set indicated as consumed, but no votes yet, sleeping")
			time.sleep(5)


		#case 1: inital setup.  isImageSetReady.txt = 0, cur_images_dir is empty, votes.txt empty
		# need to create new HiddenCube set (if necessary)
		# need to populate curr_images_dir with some random rotations
		# need to clear votes file
		# need to set isImageSetReady.txt to 1
		elif isVoteFileEmpty(vote_file_path): 

			print("creating new HiddenCubeSet")
			#os.system("python HiddenCubeDataset\scripts\\test.py --name {0} --dimensions {1} --timing 1 --seed {2} --dimensionsize {3} --parallelization {4} --rotations {5}".format(options.setname, options.dims, options.seed, options.N, options.para, options.rotations))
			#should we be generating 400 rotations off the bat?
			cube.generateRandomRotations(options.rotations)
                        
			random_rotation_files = listdir(data_images_dir)
			#randomly select num_cur_images of those to use in RSVP
			sampled_indexes = random.sample(range(1, len(random_rotation_files)), num_cur_images)
			cur_img_index = 1
			for index in sampled_indexes:
				cur_img = random_rotation_files[index]
				decoder["{num:02d}".format(num=cur_img_index)] = cur_img
				shutil.copy2(join(data_images_dir, cur_img), join(cur_images_dir, "{num:02d}.png".format(num=cur_img_index)))
				cur_img_index += 1

			clearVotes(vote_file_path)
			setIsImageSetReady(isImageSetReady_file_path)

		#case 2: main. isImageSetReady.txt = 0, votes.txt has content
		# wait a cpl sec just in case p300 accumuator still writing down votes
		# read in votes
		# take top x votes, generate y similar rotations for each
		#   if any top votes are 0, generate y random rotations
		# generate num_images - x*y random rotations 
		#  actually, for now if everything has a vote, we wont do randoms. this shouldnt really happen tho
		# clear curr_images and populate with new set
		# clear votes.txt
		# set isImageSetReady.txt to 1
		else:
                        print("reading classifier votes and generating new image set for RSVP")
                        time.sleep(3)
                        votes = readVotes(vote_file_path)
                        clearCurrentImages(cur_images_dir)
                        cur_image_count = 1
                        while cur_image_count <= num_cur_images:
                                #get largest vote, if any
                                cur_target_name = max(votes, key=lambda k: votes[k])
                                if votes[cur_target_name] != 0:
                                        #generate similar rotations
                                        #shall we use number of votes to influence num sim rots?	
                                        dataset_image_ID = decoder["{num:02d}".format(num=int(cur_target_name))].replace(".png","")
                                        dataset_image_path = join(project_dir, "HiddenCubeDataset", "datasets", options.setname, "{0}_similar_rotations".format(dataset_image_ID))
                                        #os.system("python HiddenCubeDataset\scripts\\test.py --name {0} --dimensions {1} --seed {2} --dimensionsize {3} --parallelization {4} --rotations {5} --similar {6}".format(options.setname, options.dims, options.seed, options.N, options.para, int(votes[cur_target_name]) * 2, dataset_image_ID))
                                        #similar rotations...need to fix some magic numbers here
                                        cube.generateSimilarRotations(principal_angle_ID = dataset_image_ID, rotations = int(votes[cur_target_name]) * 2, similarity_factor = options.similarfac)

                                        new_images = listdir(dataset_image_path)
                                        for new_image in new_images:
                                                shutil.copy2(join(dataset_image_path, new_image), join(cur_images_dir, "{num:02d}.png".format(num=cur_image_count)))
                                                decoder["{num:02d}".format(num=cur_image_count)] = new_image
                                                cur_image_count += 1;
                                        votes[cur_target_name] = 0 # so we dont double select

                                else:
					#no votes, randomize
                                        random_rotation_files = listdir(data_images_dir)
					#randomly select num_cur_images of those to use in RSVP
                                        sampled_indexes = random.sample(range(1, len(random_rotation_files)), (num_cur_images - cur_image_count) + 1)
                                        for index in sampled_indexes:
                                                cur_img = random_rotation_files[index]
                                                decoder["{num:02d}".format(num=cur_image_count)] = cur_img
                                                shutil.copy2(join(data_images_dir, cur_img), join(cur_images_dir, "{num:02d}.png".format(num=cur_image_count)))
                                                cur_image_count += 1

                        clearVotes(vote_file_path)
                        setIsImageSetReady(isImageSetReady_file_path)


