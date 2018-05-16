from optparse import OptionParser
import os
from os.path import join
import numpy as np
import scipy as sp
from scipy import linalg
from scipy import cluster
import imageio
import pylab
import matplotlib


def L2(cmp, image_names, PATH_im):
    norms = np.empty(len(image_names), dtype=[('name','a256'), ('norm', 'i8')]) #image number (rotation angle), and norm value
    for x in range(len(image_names)):
        temp = imageio.imread(join(PATH_im, image_names[x]))
        temp = temp[:,:,0] #all the colors should be euqal since the image is greyscaled, so we are only using the redlayer
        norms[x] = (image_names[x].replace(".png", ""), linalg.norm(temp - cmp))
    norms.sort(order='norm')
    #np.save("images.sim", norms[:15])
    return norms

def call_algo(name, PATH_cpm, PATH_im):
    cmp , image_names = get_images(PATH_cpm, PATH_im)
    if name == "l2":
        return L2(cmp, image_names, PATH_im)
    # Add other algorithms if need be

def get_images(PATH_cpm, PATH_dir):
    cmp = imageio.imread(PATH_cmp)
    cmp = cmp[:, :, 0]
    image_names = os.listdir(PATH_im)
    return cmp, image_names

def get_args():
    usage='''look at -h option'''
    parser = OptionParser(usage=usage)

    parser.add_option("-s", "--source-location", type="string", dest="source",
			default="testSet", help="Folder where the images are stored from hiddencube home.", metavar="#NAME")
    parser.add_option("-c", "--image-to-compare", type="string", dest="image",
            default="dne", help="Includes the location of the image to compare from hiddencube home")
    parser.add_option("-l", "--number", type="int", dest="num",
            default=10, help="The number of similar images to return.")
    parser.add_option("-a", "--algorithm", type="string", dest="algo",
            default="l2", help="Algorithm to be used. (Only l2 at the moment)")
    parser.add_option("-d", "--destination-location", type="string", dest="dest",
            default="most_sim", help="Enter the file for the list of similar images to be saved in.")


    options, _ = parser.parse_args()

    # checks
    if options.image == "dne" :
        print "Please choose a real image"
    if options.num < 1 :
        print "Please choose a positive integer"
    return parser.parse_args()


if __name__=='__main__':
    # get the options 
    options, _ = get_args()

    # Paths
    middle_home = os.environ['OPENVIBE_MIDDLE']
    # PATH_im = join(middle_home, "HiddenCubeDataset", "datasets", options.source)
    # PATH_cmp = join(middle_home, "buffers", "CurrentImages", options.image)
    PATH_im = options.source
    PATH_cmp = options.image
    image_names = os.listdir(PATH_im)


    best = call_algo(options.algo, PATH_cmp, PATH_im)
    best = best[:options.num]
    np.save(options.dest, best)