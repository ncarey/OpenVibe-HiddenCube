import time
import random
from optparse import OptionParser
import subprocess
import os
from os import listdir
from os.path import isfile, join
from math import *
import multiprocessing
import numpy as np
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

    parser.add_option("-sn", "--similaritytype", type="int", dest="sim_num", 
            default="0", help="Picks the similarity function being used\n 0 -> normal\n 1 -> L2\n 2 -> clustering(?)")




    middle = os.environ["OPENVIBE_MIDDLE"] # or some other path variable
    curr_images_path = join(middle, "buffers", "CurrentImages")
    scripts_path = join(middle, "HiddenCubeDataset", "scripts") #need this shit
    data_images_path = join(middle, "HiddenCubeDataset", "datasets", options.setname, "images")
    vote_path = join(curr_images_path, "votes.txt")


    file_names = listdir(curr_images_path)
    decoder = {}    #Would it be prefereable to use a bufferfile?
    if os.path.getsize(vote_path) == 0:
        print "here"
        #call HiddenCube and make some CurrentImages
        os.system("python HiddenCubeDataset\scripts\\test.py --name {0} --dimensions {1} --timing 1 --seed {2} --dimensionsize {3} --parallelization {4} --rotations {5}".format(options.setname, options.dims, options.seed, options.N, options.para, options.rotations))
        file_names = listdir(data_images_path)
        mapfile = open(os.path.join(curr_images_path, "decode.txt"), 'w')
        for x in range(len(file_names)):
            decoder["{num:02d}".format(num=(x+1))] = file_names[x]
            print(decoder["{num:02d}".format(num=(x+1))])
            shutil.copy2(join(data_images_path, file_names[x]), join(curr_images_path, "{num:02d}.png".format(num=(x+1))))
            mapfile.write("{num:02d} {0}\n".format(file_names[x], num=(x+1)))
        mapfile.close()
        ready = open(join(curr_images_path,"isImageSetReady.txt"), 'w')
        ready.write("1\n")
        ready.close()
    #End of side case


    #test to see if program can write similar images to
    votes = open(vote_path, 'w')
    votes.write("01 7")
    votes.close()

    looping = False
    while looping:
        if os.path.getsize(vote_path) == 0:
            print "About to Stop"
            time.sleep(5)
            looping = False
        else:
            #in the case the program had to be killed
            if len(decoder) == 0:
                mapfile = open(join(curr_images_path, "decode.txt"), 'r')
                for lines in mapfile:
                    arr = lines.split()
                    decoder[arr[0]] = arr[1]
                mapfile.close()
                mapfile = open(join(curr_images_path, "decode.txt"), 'w')
                mapfile.close()

            count = 1
            threshold = 5 #some random number of votes
            votes = open(vote_path, 'r')
            mapfile = open(join(curr_images_path, "decode.txt"), 'a')
            for lines in votes:
                arr = lines.split()  # Assuming the format is as such: "filename" "#votes"
                if int(arr[1]) > threshold: #creating new similar images if threshold is passed
                    print(arr[0], arr[1])
                    simi = decoder[arr[0]].replace(".png","")
                    simi_path = join(middle, "HiddenCubeDataset", "datasets", options.setname, "{0}_similar_rotations".format(simi))
                    new_files = []
                    os.system("python HiddenCubeDataset\scripts\\test.py --name {0} --dimensions {1} --timing 1 --seed {2} --dimensionsize {3} --parallelization {4} --rotations {5} --similar {6}".format(options.setname, options.dims, options.seed, options.N, options.para, int(arr[1]), simi))
                    if options.sim_num == 0:
                        new_files = listdir(simi_path)
                    if options.sim_num == 1:
                        os.system("python similar.pn --name {0} --image-to-compare {1}".format(options.setname, join(curr_images_path, arr[0])))
                        new_files = np.load("images.sim")


                    for x in range(len(new_files)):
                        shutil.copy2( join(simi_path,"{0}.png".format(new_files[x])), join(curr_images_path, "{num:02d}.png".format(num=count)))
                        mapfile.write("{num:02d} {file}".format(num=count, file=new_files[x]))
                        count += 1
                    print "Generated {0} similar rotations for {1}".format(int(arr[1]), arr[0])
            votes.close()
            #votes = open(vote_path, 'w')
            #votes.close()