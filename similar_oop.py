from optparse import OptionParser
import os
from os.path import join
import numpy as np
import scipy as sp
from scipy import linalg
from scipy import spatial
import imageio
import matplotlib
from sklearn.decomposition import PCA

def sift(cmp, image_names, PATH_im):
    # Probably the best algorithm for this program, also its varient SURF can be used (SURF is ~3 times faster)
    # works for images that contain objects 
    # works best when the objects are the same throughout the images
    # the opencv library seems to work

    # In the instance we are using the hiddencubedataset it may be useful to use the Harris corner detection algorithm
    return

def pca(cmp, image_names, PATH_im):
    pass 
    pca = PCA(30) # some number of components
    X = np.ndarray((len(image_names)+1, 512, 512), 'int8')
    X[0] = cmp
    for i in range(1, len(image_names)):
        X[i] = imageio.imread(join(PATH_im, image_names[x]))
    X_proj = pca.fit_transform(X+cmp) # not really sure how to handle images, as they are 

    # Now see which images are most similar to cmp using L2 norm (or any other norm)
    # how ???
    return 

def procrustes(cmp, image_names, PATH_im):
    norms = np.empty(len(image_names), dtype=[('name','a256'), ('norm', 'float')])
    for x in range(len(image_names)):
        temp = imageio.imread(join(PATH_im, image_names[x]))
        temp = temp[:,:,0]
        diff = 1e9
        try:
            _, _, diff = spatial.procrustes(temp, cmp)
        except:
            print "caught"
        norms[x] = (image_names[x], diff)
        
    norms.sort(order='norm')
    #np.save("images.sim", norms[:15])
    return norms

def L2(cmp, image_names, PATH_im):
    norms = np.empty(len(image_names), dtype=[('name','a256'), ('norm', 'i8')]) 
    for x in range(len(image_names)):
        temp = imageio.imread(join(PATH_im, image_names[x]))
        temp = temp[:,:,0] 
        norms[x] = (image_names[x], linalg.norm(temp - cmp))
        print norms[x]
    norms.sort(order='norm')
    #np.save("images.sim", norms[:15])
    return norms

def save_images(norms, num, name="most_sim"):
    best = norms[:num]
    print(best[:options.num])
    np.save(name, best)
    return 

def call_algo(name, PATH_cpm, PATH_im):
    cmp , image_names = get_images(PATH_cpm, PATH_im)
    if name == "l2":
        return L2(cmp, image_names, PATH_im)
    if name == "procrustes":
        return procrustes(cmp, image_names, PATH_im)
    if name == "sift":
        return pca(cmp, image_names, PATH_im)
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
    parser.add_option("-a", "--algorithm", type="stringd", dest="algo",
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

    norms = call_algo(options.algo, PATH_cmp, PATH_im)
    save_images(norms, options.num, name=options.dest)
    # best = best[:options.num]
    # print(best[:options.num])
    # np.save(options.dest, best)