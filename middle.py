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


if __name__=='__main__':

    #same options as in test
    usage='''look at -h option'''

    parser = OptionParser(usage=usage)

    parser.add_option("-n", "--name", type="string", dest="setname",
			default="testSet", help="Specify the name of the dataset. Data will be put in a $RSVP_DATA_HOME/datasets/<name>/ directory. Directory will be wiped prior to creating dataset.", metavar="#NAME")

    parser.add_option("-d", "--dimensions", type="int", dest="dims",
            default="5", help="Specify how many dimensions of data to produce. The first three dimensions will form coordinates for the cube, the remaining dimensions will be uniform random noise between -2 and 2",
            metavar="#DIMS")

    parser.add_option("-t", "--timing", type="int", dest="timing",
            default="0", help="Specify 1 to display timing information, 0 otherwise", metavar="#TIME")

    parser.add_option("-s", "--seed", type="int", dest="seed",
            default="1", help="Specify a seed for the random num generator. -1 uses current time as seed", metavar="#SEED")

    parser.add_option("-m", "--dimensionsize", type="int", dest="N",
            default=1500, help="Specify how many data points total per dimension", metavar="#N")

    parser.add_option("-r", "--rotations", type="int", dest="rotations",
             default=10, help="Specify how many random rotations of the dataset to perform", metavar="#ROTS")

    parser.add_option("-p", "--parallelization", type="int", dest="para",
            default=2, help="Specify how many parallel processes to use when generating random rotations", metavar="#PARA")

    parser.add_option("-f", "--similar", type="float", dest="similar",
                     default=-1.0, help="Specify principal angle of rotation to generate similar rotations", metavar="#SIMI")

    parser.add_option("-v", "--similarityfactor", type="float", dest="similarfac",
                     default=0.1, help="Specify how similar the rotations should be (TODO: experiment with this)", metavar="#SIMI")
    (options, args) = parser.parse_args()





    middle = os.environ["OPENVIBE_MIDDLE"] # or some other path variable
    curr_images_path = join(middle, "buffers", "CurrentImages");
    data_images_path = join(middle, "HiddenCubeDataset", "datasets", options.setname, "images")
    vote_path = join(curr_images_path, "votes.txt")


    file_names = listdir(curr_images_path)
    if os.path.getsize(vote_path) == 0 and len(file_names) == 1:
        print "here"
        #call HiddenCube and make some CurrentImages
        os.system("python HiddenCubeDataset\scripts\test.py --name {0} --dimensions {1} --timing 1 --seed {2} --dimensionsize {3} --parallelization {4} --rotations {5}".format(options.setname, options.dims, options.seed, options.N, options.para, options.rotations))
        file_names = listdir(data_images_path)
        votes = open(join(curr_images_path, "decoder.txt"), "w")
        for x in range(len(file_names)):
            votes.write("{num:02d}.png {file}\n".format(num=(x+1), file=file_names[x]))
            shutil.copy2(join(data_images_path, file_names[x]), join(curr_images_path, "{num:02d}.png".format(num=(x+1))))
        votes.close()



#    while True:
#        if os.path.getsize(vote_path) == 0:
#            sleep(5)
#        else:
#            votes = open(vote_path, 'r')
#            for lines in votes:
#                arr = lines.split() # Assuming the format is as such: "filename" "#votes"
#                images[arr[0]] = int(arr[1])
#
#            open(vote_path, 'w').close() # to clear the files
