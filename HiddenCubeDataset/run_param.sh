export HIDDENCUBE_HOME=/home/ncarey/gitrepos/HiddenCubeDataset
python $HIDDENCUBE_HOME/scripts/generateDataset.py --name testSet --dimensions 5 --timing 1 --seed 1 --dimensionsize 1500 --parallelization $1 --rotations $2

