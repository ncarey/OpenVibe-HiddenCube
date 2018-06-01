from HiddenCube import HiddenCube


if __name__ =='__main__':
	
	cube = HiddenCube(project_directory = 'D:\Workspace\OpenVibe-HiddenCube\HiddenCubeDataset', dataset_name = 'testSet', n_dimensions = 5, dimension_size = 1500, randn_seed = 5, hypersphere_noise_multiplier = 4, parallelization = 2, notebook_plotting = False)

	cube.generateRandomRotations(rotations=10)
	cube.generateSimilarRotations(principal_angle_ID = 0.5510944884607982, 
                              	      rotations = 10, 
                              	      similarity_factor = .1)