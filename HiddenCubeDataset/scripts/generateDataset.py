import time
import random
from optparse import OptionParser
import subprocess
import os
from math import *
import multiprocessing
import numpy
import pylab
import matplotlib

#import matplotlib.pyplot


def generateHyperSphereNoise(N, dims, norm, unif):

  #generate points on surface of an N-ball according to Marsaglia method
  normal_deviates = norm(size=(dims, N))

  radius = numpy.sqrt((normal_deviates**2).sum(axis=0))
  points = normal_deviates/radius

  #points are now uniformly distributed along surface of unit n-ball.
  #since we want points distributed amoung interior of n-ball, multiply by uniformly random fraction
  uniform_deviates = unif(0,1,size=(1,N))
  point_radius = uniform_deviates**(1.0/dims)

  points = points * point_radius
  #points are now uniformly distributed inside unit n-ball
  #multiply by 4 because we want a large n-ball
  points = points * 4

  return points

#take an existing set of random n-ball points and add in a wire cube 
def generateCube(points, cube_noise_factor, cube_size, rand_int, unif, rand_matrix):

  cube_corners = {"x":[1,1,-1,-1,1,1,-1,-1], "y":[1,-1,-1,1,1,-1,-1,1], "z":[1,1,1,1,-1,-1,-1,-1]}

  for i in range(0, cube_size):
    #random int betwen 0(inclusive) and 3(exclusive)
    rand_xyz = rand_int(0,3)
    rand_corner = rand_int(0,8)
    rand_noise_x = unif(-1,1) * cube_noise_factor
    rand_noise_y = unif(-1,1) * cube_noise_factor
    rand_noise_z = unif(-1,1) * cube_noise_factor

    x = cube_corners["x"][rand_corner]
    y = cube_corners["y"][rand_corner]
    z = cube_corners["z"][rand_corner]

    if rand_xyz == 0:
      x = unif(-1,1)
    elif rand_xyz == 1:
      y = unif(-1,1)
    elif rand_xyz == 2:
      z = unif(-1,1)
    else:
      print "ERROR MR ERROR, this code should never be run!"

    x += rand_noise_x
    y += rand_noise_y
    z += rand_noise_z
    points[0][i] = x
    points[1][i] = y
    points[2][i] = z

  #now rotate just the 3D wire cube so that we dont encode the same boring cube every time.
  #this step is not essential, just adds some variety to datasets
  correct, rotation_matrix, seed_matrix = randomRotationMatrix(3, rand_matrix)
  while correct is False:
    correct, rotation_matrix, seed_matrix = randomRotationMatrix(3, rand_matrix)
      
  cube = points[0:3]
  cube = cube.T
  cube = numpy.dot(cube, rotation_matrix)
  cube = cube.T
  points[0:3] = cube

  return points

def generateSimulatedDataset(points, dimensions, rand_matrix):
  
  #apply N-dimensional random rotation to dataset to hide 3D wire cube
  correct, rotation_matrix, seed_matrix = randomRotationMatrix(dimensions, rand_matrix)
  while correct is False:
    correct, rotation_matrix, seed_matrix = randomRotationMatrix(dimensions, rand_matrix)
 
  points = numpy.dot(rotation_matrix, points)



  return points, rotation_matrix


def generateRandomRotations(points, sim_rotation_matrix, dimensions, rotations, parallelization, seed, data_dir_path):

  rots_per_process = int(rotations/parallelization)
  pool = multiprocessing.Pool(processes=parallelization)

  param_arr = []
  for i in range(0,parallelization):
    if seed != -1:
      param_arr.append((points, rots_per_process, dimensions, sim_rotation_matrix, seed+i, data_dir_path))
    else:
      param_arr.append((points, rots_per_process, dimensions, sim_rotation_matrix, seed, data_dir_path))
   

  pool.map(randRotationParallelWork, param_arr)
  pool.close() #POOL'S CLOSED!

  pool.join()

#def randRotationParallelWork(rotations, dimensions, sim_rotation_matrix, rand_matrix):
def randRotationParallelWork(params): 
  points = params[0]
  rotations = params[1]
  dimensions = params[2]
  sim_rotation_matrix = params[3]
  seed = params[4]
  data_dir_path = params[5]
  #initialize random number generators
  if seed != -1:
    #print "seed {0}".format(seed)
    numpy.random.seed(seed)
  else:
    numpy.random.seed()
  
  rand_matrix = numpy.random.randn
  fig = pylab.figure() #for plotting use

  for i in range(0, rotations):
    correct, rotation_matrix, seed_matrix = randomRotationMatrix(dimensions, rand_matrix)
    while correct is False:
      correct, rotation_matrix, seed_matrix = randomRotationMatrix(dimensions, rand_matrix)

    A = sim_rotation_matrix.T[0:3].T
    B = rotation_matrix[0:2].T
    cur_principal_angle = principal_angle(A, B)
 
    #print out rotation_matrix, seed_matrix, image w/prin angle 
    with open(data_dir_path + "/info/{0}_seed_matrix.txt".format(cur_principal_angle), 'w') as matrix_file:
      for i in range(0, len(seed_matrix)):
        line = "{0}".format(seed_matrix[i][0])
        for j in range(1, len(seed_matrix[i])):
          line = line + ",{0}".format(seed_matrix[i][j])
        matrix_file.write(line + "\n")



    with open(data_dir_path + "/info/{0}_rotation_matrix.txt".format(cur_principal_angle), 'w') as matrix_file:
      for i in range(0, len(rotation_matrix)):
        line = "{0}".format(rotation_matrix[i][0])
        for j in range(1, len(rotation_matrix[i])):
          line = line + ",{0}".format(rotation_matrix[i][j])
        matrix_file.write(line + "\n")

    rotation = numpy.dot(rotation_matrix[0:2], points)
    plot2DHist(rotation, data_dir_path + "/images/{0}".format(cur_principal_angle), 0, 1, fig)


def generateSimilarRotations(data_dir_path, similar_dir_path, sim_points, seed_matrix, simulated_rot_matrix, rotations, similarity_factor, parallelization, seed):
  
  dims = len(seed_matrix)

  rots_per_process = int(rotations/parallelization)
  pool = multiprocessing.Pool(processes=parallelization)
  
  param_arr = []
  for i in range(0, parallelization):
    if seed != -1:
      param_arr.append((sim_points, rots_per_process, dims, simulated_rot_matrix, seed_matrix, similarity_factor, seed+i, data_dir_path, similar_dir_path))
    else:
      param_arr.append((sim_points, rots_per_process, dims, simulated_rot_matrix, seed_matrix, similarity_factor, seed, data_dir_path, similar_dir_path))

  pool.map(similarRotationParallelWork, param_arr)
  pool.close() #POOL'S CLOSED!

  pool.join()

def similarRotationParallelWork(params):
  points = params[0]
  rotations = params[1]
  dims = params[2]
  sim_rotation_matrix = params[3]
  seed_matrix = params[4]
  similarity_factor = params[5]
  seed = params[6]
  data_dir_path = params[7]
  similar_dir_path = params[8]

  #initialize random number generators
  if seed != -1:
    numpy.random.seed(seed)
  else:
    numpy.random.seed()



  fig = pylab.figure() #for plotting

  for i in range(0, rotations):
    
    diff_matrix = numpy.random.uniform(low=-1 * (similarity_factor), high=similarity_factor, size=(dims,dims))
    new_seed_matrix = seed_matrix + diff_matrix

    correct, rotation_matrix = similarRotationMatrix(dims, new_seed_matrix)
    while correct is False:
      correct, rotation_matrix = similarRotationMatrix(dims, new_seed_matrix)

    #calc principal angle
    sim_rotation_matrix = numpy.array(sim_rotation_matrix)
    A = sim_rotation_matrix.T[0:3].T
    B = rotation_matrix[0:2].T
    cur_principal_angle = principal_angle(A, B)
 
    #print out rotation_matrix, seed_matrix, image w/prin angle 
    with open(data_dir_path + "/info/{0}_seed_matrix.txt".format(cur_principal_angle), 'w') as matrix_file:
      for i in range(0, len(seed_matrix)):
        line = "{0}".format(seed_matrix[i][0])
        for j in range(1, len(seed_matrix[i])):
          line = line + ",{0}".format(seed_matrix[i][j])
        matrix_file.write(line + "\n")



    with open(data_dir_path + "/info/{0}_rotation_matrix.txt".format(cur_principal_angle), 'w') as matrix_file:
      for i in range(0, len(rotation_matrix)):
        line = "{0}".format(rotation_matrix[i][0])
        for j in range(1, len(rotation_matrix[i])):
          line = line + ",{0}".format(rotation_matrix[i][j])
        matrix_file.write(line + "\n")

    rotation = numpy.dot(rotation_matrix[0:2], points)

    #save image twice, once in entire dataset folder, once in similar dataset folder
    filename = data_dir_path + "/images/{0}.png".format(cur_principal_angle)
    sim_filename = similar_dir_path + "/{0}.png".format(cur_principal_angle)

    plot2DHist(rotation, data_dir_path + "/images/{0}".format(cur_principal_angle), 0, 1, fig)
    cmd = "cp {0} {1}".format(filename, sim_filename)
    subprocess.call(cmd, shell=True)



def principal_angle(A, B):
  #"A and B must be column-orthogonal."
  svd = numpy.linalg.svd(numpy.dot(numpy.transpose(A), B))
  return numpy.arccos(min(svd[1].min(), 1.0))



def similarRotationMatrix(dims, seed_matrix):

  err = .000001 #error allowed for in imprecise computer math

  q, r = numpy.linalg.qr(seed_matrix)

  #verify Q is a rotation matrix
  det = numpy.linalg.det(q)
  #if det is not 1
  if det > 1.0 + err or det < 1.0 - err:
    #fix for a proper rotation: if det is -1, improper rotation. try to fix.
    q[0] = q[0] * -1
    # check again    
    det = numpy.linalg.det(q)
    if det > 1.0 + err or det < 1.0 - err:
      #could not fix
      return False, q
  

  inv = numpy.linalg.inv(q)
  for i in range(dims):
    for j in range(dims):
      if q.T[i][j] - inv[i][j] > err or q.T[i][j] - inv[i][j] < -err:
        #inverse does not equal transpose, not a rotation matrix
        return False, q
  #q is a valid rotation matrix, seed_matrix is random matrix used in QR decomp to produce Q
  return True, q


def randomRotationMatrix(dims, rand_matrix):

  err = .000001 #error allowed for in imprecise computer math

  #seed_matrix will be important later when attempting similar rotations
  seed_matrix = rand_matrix(dims, dims)
  q, r = numpy.linalg.qr(seed_matrix)

  #verify Q is a rotation matrix
  det = numpy.linalg.det(q)
  #if det is not 1
  if det > 1.0 + err or det < 1.0 - err:
    #fix for a proper rotation: if det is -1, improper rotation. try to fix.
    q[0] = q[0] * -1
    # check again    
    det = numpy.linalg.det(q)
    if det > 1.0 + err or det < 1.0 - err:
      #could not fix
      return False, q, seed_matrix
  

  inv = numpy.linalg.inv(q)
  for i in range(dims):
    for j in range(dims):
      if q.T[i][j] - inv[i][j] > err or q.T[i][j] - inv[i][j] < -err:
        #inverse does not equal transpose, not a rotation matrix
        return False, q, seed_matrix
  #q is a valid rotation matrix, seed_matrix is random matrix used in QR decomp to produce Q
  return True, q, seed_matrix

def plot2DHist(points, name, x_dimension, y_dimension, fig):
  
  #add points to data at each corner, truncate data past corners.

  x = points[x_dimension]
  y = points[y_dimension]

  #truncate any data outside off -2,-2 2,2 borders
  index = []
  for i in range(0, len(x)):
    if x[i] > 2 or x[i] < -2:
      index = numpy.append(index, i)
    if y[i] > 2 or y[i] < -2:
      index = numpy.append(index, i)
  x = numpy.delete(x, index)
  y = numpy.delete(y, index)

  #fix borders of histogram with edge points
  x = numpy.append(x, -2)
  y = numpy.append(y, -2)
  x = numpy.append(x, -2)
  y = numpy.append(y, 2)
  x = numpy.append(x, 2)
  y = numpy.append(y, -2)
  x = numpy.append(x, 2)
  y = numpy.append(y, 2)

  #pylab.axis("off")
  
  #fig = pylab.figure()
  dpi = fig.get_dpi()
  inches = 512.0 / dpi
  fig.set_size_inches(inches,inches)
  
  ax = pylab.Axes(fig, [0., 0., 1., 1.])
  ax.set_axis_off()
  fig.add_axes(ax)
  pylab.hist2d(x, y, bins=100)
  pylab.set_cmap('gray')
  pylab.savefig(name + '.png')
  pylab.clf()

if __name__=='__main__':

  usage='''look at -h option'''

  parser = OptionParser(usage=usage)

  parser.add_option("-n", "--name", type="string", dest="setname",
			default="test", help="Specify the name of the dataset. Data will be put in a $RSVP_DATA_HOME/datasets/<name>/ directory. Directory will be wiped prior to creating dataset.", metavar="#NAME")

  parser.add_option("-d", "--dimensions", type="int", dest="dims",
                     default="5", help="Specify how many dimensions of data to produce. The first three dimensions will form coordinates for the cube, the remaining dimensions will be uniform random noise between -2 and 2",
                     metavar="#DIMS")

  parser.add_option("-t", "--timing", type="int", dest="timing",
                     default="0", help="Specify 1 to display timing information, 0 otherwise", metavar="#TIME")

  parser.add_option("-s", "--seed", type="int", dest="seed",
                     default="-1", help="Specify a seed for the random num generator. -1 uses current time as seed",
                     metavar="#SEED")

  parser.add_option("-m", "--dimensionsize", type="int", dest="N",
                     default=1500, help="Specify how many data points total per dimension", metavar="#N")

  parser.add_option("-r", "--rotations", type="int", dest="rotations",
                     default=100, help="Specify how many random rotations of the dataset to perform", metavar="#ROTS")

  parser.add_option("-p", "--parallelization", type="int", dest="para",
                     default=2, help="Specify how many parallel processes to use when generating random rotations", 
			metavar="#PARA")

  parser.add_option("-f", "--similar", type="float", dest="similar",
                     default=-1.0, help="Specify principal angle of rotation to generate similar rotations", 
			metavar="#SIMI")
  parser.add_option("-v", "--similarityfactor", type="float", dest="similarfac",
                     default=0.1, help="Specify how similar the rotations should be (TODO: experiment with this)", 
			metavar="#SIMI")

  (options, args) = parser.parse_args()

  #check for project home environment variable 
  try:
    FNULL = open(os.devnull, 'w')
    hiddencube_home = os.environ['HIDDENCUBE_HOME']
    data_dir_path = hiddencube_home + "/datasets/" + options.setname
    
    #initialize random number generators
    if options.seed != -1:
      numpy.random.seed(options.seed)
    else:
      numpy.random.seed()
    
    norm = numpy.random.normal
    unif = numpy.random.uniform
    rand_int = numpy.random.randint
    norm_matrix = numpy.random.randn
 
    if options.similar is not -1.0:
      #generate similar rotations mode

      #set up directory structure
      similar_dir_path = data_dir_path + "/" + str(options.similar) + "_similar_rotations"
      cmd = 'mkdir -p {0}/'.format(similar_dir_path)
      subprocess.call(cmd, shell=True, stdout=FNULL, stderr=FNULL)

      #read in simulated dataset
      sim_data_path = data_dir_path + "/info/simulatedDataset.txt"   
      sim_points = []
      text = ""
      with open(sim_data_path, 'r') as sim_file:
        text = sim_file.read()
      text = text.split("\n")
      text.remove(text[-1]) #last element is blank
      for line in text:
        elems = line.split(",")
        tmp = [] 
        for elem in elems:
          tmp = numpy.append(tmp, float(elem))
        sim_points.append(tmp)

      #read in seed_matrix
      seed_matrix_path = data_dir_path + "/info/" + str(options.similar) + "_seed_matrix.txt"    
      seed_matrix = []
      text = ""
      with open(seed_matrix_path, 'r') as seed_file:
        text = seed_file.read()   
      text = text.split("\n")
      text.remove(text[-1]) #last element blank
      for line in text:
        elems = line.split(",")
        tmp = []
        for elem in elems:
          tmp = numpy.append(tmp, float(elem))
        seed_matrix.append(tmp)

      #read simulated rotation matrix
      sim_rot_matrix = []
      text = ""
      with open(data_dir_path + "/info/simulated_rotation_matrix.txt", 'r') as sim_rot_file:
        text = sim_rot_file.read()   
      text = text.split("\n")
      text.remove(text[-1]) #last element blank
      for line in text:
        elems = line.split(",")
        tmp = []
        for elem in elems:
          tmp = numpy.append(tmp, float(elem))
        sim_rot_matrix.append(tmp)


      generateSimilarRotations(data_dir_path, similar_dir_path, sim_points, seed_matrix, sim_rot_matrix, options.rotations, options.similarfac, options.para, options.seed)


    else:
      #generate new dataset mode
      start = 0
      if options.timing == 1:
        start = time.time()

      points = generateHyperSphereNoise(options.N, options.dims, norm, unif)
      points = generateCube(points, 0, options.N, rand_int, unif, norm_matrix)
    
      #plot2DHist(points, 'startCube', 0, 1)

      points, sim_rotation_matrix = generateSimulatedDataset(points, options.dims, norm_matrix)

      #plot2DHist(points, 'sim', 0, 1)
 
      #create dataset directory structure
      cmd = 'rm -rf {0}'.format(data_dir_path)
      subprocess.call(cmd, shell=True, stdout=FNULL, stderr=FNULL)
      cmd = 'mkdir -p {0}/info'.format(data_dir_path)
      subprocess.call(cmd, shell=True, stdout=FNULL, stderr=FNULL)
      cmd = 'mkdir -p {0}/images'.format(data_dir_path)
      subprocess.call(cmd, shell=True, stdout=FNULL, stderr=FNULL)

      #save simulated dataset to file
      with open(data_dir_path + "/info/simulatedDataset.txt", "w") as sim_file:
        for i in range(0, len(points)):
          line = "{0}".format(points[i][0])
          for j in range(1, len(points[i])):
            line = line + ",{0}".format(points[i][j])
          sim_file.write(line + "\n")
     

      #save simulated rotation matrix to file
      with open(data_dir_path + "/info/simulated_rotation_matrix.txt", "w") as sim_rot_file:
        for i in range(0, len(sim_rotation_matrix)):
          line = "{0}".format(sim_rotation_matrix[i][0])
          for j in range(1, len(sim_rotation_matrix[i])):
            line = line + ",{0}".format(sim_rotation_matrix[i][j])
          sim_rot_file.write(line + "\n")


      generateRandomRotations(points, sim_rotation_matrix, options.dims, options.rotations, options.para, options.seed, data_dir_path)
    

      #print "Done"

      if options.timing == 1:
        print (time.time() - start)

  except KeyError:
    print "\t ERROR: You need to set the HIDDENCUBE_HOME environment variable to the path to the home directory of this project.  Execute a command similar to 'export HIDDENCUBE_HOME=/home/ncarey/gitrepos/HiddenCubeDataset'"



