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


usage='''look at -h option'''

parser = OptionParser(usage=usage)

parser.add_option("-n", "--name", type="string", dest="name",
			default="testSet", help="Folder where the images are stored from hiddencube home.", metavar="#NAME")
parser.add_option("-c", "--image-to-compare", type="string", dest="image",
      help="Includes the location of the image to compare from hiddencube home")

(options, args) = parser.parse_args() #important




if __name__=='__main__':
  
  middle_home = os.environ['OPENVIBE_MIDDLE']
  PATH_im = join(middle_home, "HiddenCubeDataset", "datasets", options.name, "images")
  PATH_cmp = join(middle_home, "buffers", "CurrentImages", options.image)
  image_names = os.listdir(PATH_im)

  cmp = imageio.imread(PATH_cmp)
  cmp = cmp[:, :, 0]
  norms = np.empty(len(image_names), dtype=[('name','a256'), ('norm', 'i8')]) #image number (rotation angle), and norm value
  for x in range(len(image_names)):
    temp = imageio.imread(join(PATH_im, image_names[x]))
    temp = temp[:,:,0] #all the colors should be euqal since the image is greyscaled, so we are only using the redlayer
    hold = (image_names[x].replace(".png", ""), linalg.norm(temp - cmp))
    # norms[x, 0] = image_names[x].replace(".png", "")
    # norms[x, 1] = linalg.norm(temp - cmp) 
    norms[x] = hold
  norms.sort(order='norm')
  np.save("images.sim", norms[:15])
  