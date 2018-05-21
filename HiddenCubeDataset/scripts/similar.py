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

parser.add_option("-n", "--name", type="string", dest="place",
			default="testSet", help="Folder where the images are stored from hiddencube home.", metavar="#NAME")
parser.add_option("-c", "--image-to-compare", type="string", dest="image",
      help="Includes the location of the image to compare from hiddencube home")

(options, args) = parser.parse_args() #important




if __name__=='__main__':
  
  hiddencube_home = os.environ['HIDDENCUBE_HOME']
  PATH_im = join(hiddencube_home, "datasets", options.place, "images")
  PATH_cmp = join(hiddencube_home, "scripts", options.image)
  image_names = os.listdir(PATH_im)

  cmp = imageio.imread(PATH_cmp)
  cmp = cmp[:, :, 0]
  norms = np.zeros((len(image_names), 2)) #image number (rotation angle), and norm value
  for x in range(len(image_names)):
    temp = imageio.imread(join(PATH_im, image_names[x]))
    temp = temp[:,:,0] #all the colors should be euqal since the image is greyscaled, so we are only using the redlayer
    norms[x, 0] = float(image_names[x].replace(".png", ""))
    norms[x, 1] = linalg.norm(temp - cmp) 
  norms[norms[:,1].argsort()]

  print(norms[:5,:])

  os.mkdir(join(hiddencube_home, "sim"))

  # for i in range(images.shape[0]):
  #   for j in range(i+1, images.shape[0]):
  #     val = linalg.norm(images[i] - images[j]) #linalg.orthogonal_procrustes(images[i], images[j]) takes too long
  #     norms[i, j] = val
  #     norms[j, i] = val
  
  # (centroids, val) = cluster.vq.kmeans(norms, 5)
  # print centroids[0]
  # np.savetxt("clusters.txt", centroids)