REM This still works, Images are in \HiddenCubeDataset\datasets\"directoryname"\images
SET HIDDENCUBE_HOME=C:\Users\Magna\Dropbox\Research\Tamas\OpenVibe-HiddenCube\HiddenCubeDataset
python scripts\test.py --name testSet --dimensions 5 --timing 1 --seed 1 --dimensionsize 1500 --parallelization 2 --rotations 10
