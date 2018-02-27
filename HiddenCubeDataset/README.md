HiddenCubeDataset
=================

Ubuntu Requirements:
Python 2.7
sudo apt-get install python-numpy
sudo apt-get install python-scipy
sudo apt-get install python-matplotlib

- IMPORTANT:
  - set a HIDDENCUBE_HOME environment variable to the path to the directory containing this README
    - export HIDDENCUBE_HOME=/path/to/this/directory  (note no slash on the end)

- How to run the scripts
  - The scripts/generateDataset.py script can be run in two modes: generate dataset and generate similar rotations
  - Running in 'generate dataset' mode
    - This mode creates a simulated dataset along with a number of random rotations of the simulated dataset
    - A new directory will be created in the $HIDDENCUBE_HOME/datasets/ folder that will contain the new dataset
    - Remember to create a new dataset before attempting to generate similar rotations

    - export HIDDENCUBE_HOME=/path/to/HiddenCubeDataset
    - python scripts/generateDataset.py --name testSet --dimensions 5 --timing 0 --seed -1 --dimensionsize 1500 --parallelization 2 --rotations 500

    - execute "python scripts/generateDataset.py" with the following options.  Leave an option blank if the default value is acceptable.
      - -n/--name [dataset name string]
        - This is the user-specified name of the dataset to be created.
        - Also the name of the directory the dataset will be placed in. ($HIDDENCUBE_HOME/datasets/[dataset_name])
        - Default is "test"
      - -d/--dimensions [int]
        - This option allows you to specify how many dimensions the dataset will have.
        - The first three dimensions contain the wire-frame cube, the rest contain random noise uniformly distributed within a hyper-sphere
        - Default is 5 dimensions
      - -t/--timing [0 or 1]
        - Specify 1 to display execution time of creating a dataset. Used for benchmarking
        - Default is 0
      - -s/--seed [int]
        - Specify a number to seed the random number generator with for reproducible results
        - Specify -1 to use the current system time as the seed
        - Default is -1
      - -m/--dimensionsize [int]
        - Specify how many elements each dimension will hold.  This number is the amount of coordinates in a dataset.
        - This number is also the amount of datapoints visualized in the images
        - Default is 1500.  There should be little need to change this
      - -r/--rotations [int]
        - Specifty how many random rotations to perform on the simulated dataset.
        - This is the amount of images created.
        - Performing rotations and creating visualization is the parallized portion of the program.
        - Default is 100, which should take much less than 10 seconds to execute
      - -p/--parallelization [int]
        - Specify how many parallel processes should generate random rotations at the same time.
        - Set this to the amount of available processor cores in your system. 
        - Parallelization is done with a python multiprocess pool.
        - No, hyperthreading doesn't help performance nearly as much as another physical core
        - Default is 2
      - NOTE: if generating a new dataset, leave the -f/--similar and -v/--similarityfactor parameters UNSPECIFIED

  - Running in 'similar rotations' mode:
    - First, create a dataset
    - Pick an image that you would like to generate similar rotations to
      - Note the name of the image. This is the principal angle, or "score". A lower score should show more structure

    - export HIDDENCUBE_HOME=/home/ncarey/gitrepos/HiddenCubeDataset
    - python scripts/generateDataset.py --name testSet --seed -1 --parallelization 2 --rotations 200 --similar 0.137439186156 --similarityfactor 0.2

    - Note that the produced similar rotations will be in BOTH of the following directories:
      - $HIDDENCUBE_HOME/datasets/[dataset_name]/X.XXXXXXXXXXXX_similar_rotations/ 
        - X.XXXXXXXXXXXX is the filename of the base rotation that we generate similar rotations to
      - $HIDDENCUBE_HOME/datasets/[dataset_name]/images/
    - Explanation of parameters:
      - -n/--name [dataset name]
        - This must be the name of the dataset that contains the image you want to generate similar rotations as
        - This is also the name of the directory that the image will be located in.
        - Default is 'test'
      - -r/--rotations [int]
        - Specify how many similar rotations you'd like.  These rotations are randomly similar to the specified rotation. 
        - Default is 100
      - -f/--similar [X.XXXXXXXXXXXX]
        - X.XXXXXXXXXXXX is the name of the image/rotation to generate similar rotations to.
        - Do not include the '.png' filename extension
        - Default is -1.0, which means the program will run in generate dataset mode.
      - -v/--similarityfactor [float]
        - This parameter is tricky.  It determines how similar the generated rotations will be to the the provided image.
        - Smaller values will lead to less varied rotations, larger values will lead to more variance
        - This parameter will need some experimentation, behavior is not yet fully understood/documented
        - Default is 0.1
 


- Explanation of directory file structure:

 - $HIDDENCUBE_HOME/ 
   - Base directory. Contains bash shell scripts that show how to run the main python scripts

 - $HIDDENCUBE_HOME/datasets/
   - directory that holds each different dataset directory

 - $HIDDENCUBE_HOME/datasets/[dataset name]/
   - [dataset name] is the unique user-specified name of a particular dataset
     - matches the -n/--name option for the main generateDataset.py script
   - all dataset-specific information will be inside this directory

 - $HIDDENCUBE_HOME/datasets/[dataset_name]/images/
   - this directory contains all visualizations of rotations performed on the simulated dataset
   - images generated in the initial dataset creation AND later similar rotation explorations are stored here
   - images in this folder are named after their "score"
     - The score is the principal angle between the specific rotation performed on the simulated dataset and the transpose of the rotation used to create the simulated dataset.

  - $HIDDENCUBE_HOME/datasets/[dataset_name]/info/
    - this directory is used to contain text information about rotations performed on the simulated dataset
    - simulatedDataset.txt contains the matrix representing the simulated dataset.
    - simulated_rotation_matrix.txt contains the rotation matrix applied to the wireframe cube that created the simulated dataset.
    - X.XXXXXXXXXXXX_rotation_matrix.txt contains the rotation matrix applied to the simulated dataset used to create the X.XXXXXXXXXXXX.png image
    - X.XXXXXXXXXXXX_seed_matrix.txt contains the normally random seed matrix used to generate a random rotation matrix.  This file is used when generating similar rotation matricies.

  - $HIDDENCUBE_HOME/datasets/[dataset name]/X.XXXXXXXXXXXX_similar_rotations/
    - This directory contains images of rotations created using the similar rotation function.  
    - X.XXXXXXXXXXXX is the principal angle of the rotation that we generate similar rotations to
    - NOTE: images in this folder are also located in the $HIDDENCUBE_HOME/datasets/[dataset name]/images/ directory

  - $HIDDENCUBE_HOME/benchmark
    - contains a benchmarking script and a graph depicting parallel performance

  - $HIDDENCUBE_HOME/scripts
    - contains scripts essential to generating simulated datasets and similar rotations




How to run:
  - Look at the ./run.sh script
  - make sure to set the HIDDENCUBE_HOME environment variable as this directory.
    - look at the run.sh script
  - To play a movie similar to what RSVP will show the subject:
    - mplayer mf://*.png  -loop 0 -fps 4
  - To print a movie similar to above but to a file:
    - mencoder mf://*.png -mf type=png:w=512:h=512:fps=4 -ovc x264 -x264encopts preset=slow:tune=film:threads=auto:crf
=18 -o 5Dhist.mov

