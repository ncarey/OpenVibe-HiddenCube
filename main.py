from HiddenCubeDataset.scripts.HiddenCube import HiddenCube
from imageloader import ImageLoader
from ExperimentLog import ExperimentLog
import os
from os.path import join
import sys
import time
from optparse import OptionParser


if __name__=='__main__':

    usage='''look at -h option'''

    parser = OptionParser(usage=usage)

    parser.add_option("-n", "--name", type="string", dest="setname", default="testSet", help="Specify the name of the dataset. Data will be put in a $RSVP_DATA_HOME/datasets/<name>/ directory. Directory will be wiped prior to creating dataset.", metavar="#NAME")

    parser.add_option("-d", "--dimensions", type="int", dest="dims", default="5", help="Specify how many dimensions of data to produce. The first three dimensions will form coordinates for the cube, the remaining dimensions will be uniform random noise between -2 and 2", metavar="#DIMS")

    parser.add_option("-s", "--seed", type="int", dest="seed", default="-1", help="Specify a seed for the random num generator. -1 uses current time as seed", metavar="#SEED")

    parser.add_option("-m", "--dimensionsize", type="int", dest="N", default=1500, help="Specify how many data points total per dimension", metavar="#N")

    parser.add_option("-r", "--rotations", type="int", dest="rotations", default=40, help="Specify how many random rotations of the dataset to perform to start out with", metavar="#ROTS")

    parser.add_option("-p", "--parallelization", type="int", dest="para", default=2, help="Specify how many parallel processes to use when generating random rotations", metavar="#PARA")

    parser.add_option("-v", "--similarityfactor", type="float", dest="similarfac", default=0.1, help="Specify how similar the rotations should be (TODO: experiment with this)", metavar="#SIMI")

    parser.add_option("-x", "--hypersphereNoiseMultiplier", type="float", dest="hsphere", default=4.0, help="Specify the hypersphere noise multiplier (TODO: experiment with this)", metavar="#HNOI")

    parser.add_option("-i", "--imagecount", type="int", dest="imagecount", default=20, help="Specify the amount of images per iteration of RSVP", metavar="#IMAGEC")
    (options, args) = parser.parse_args()


    project_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
    #project_dir = "D:\Workspace\PUSLD\OpenVibe-HiddenCube\"


    cube = HiddenCube(project_directory = join(project_dir, "HiddenCubeDataset"),
        dataset_name = options.setname,
        n_dimensions = options.dims,
        dimension_size = options.N,
        randn_seed = options.seed,
        hypersphere_noise_multiplier = options.hsphere,
        parallelization = 2,
        notebook_plotting = False)

    cube.generateRandomRotations(options.rotations)

    logpath = join(join(project_dir, "ExperimentLogs"), options.setname + ".txt")
    log = ExperimentLog(logpath, options.setname, options.seed, options.similarfac, options.imagecount)

    imageloader = ImageLoader(cube, log, project_dir, options.imagecount, similarity_factor = options.similarfac, debug = 1)

    looping = True
    while looping:
        imageloader.process()
        time.sleep(5)
