File structure for the HiddenCube EEG-Search experiment.

'HiddenCubeDataset' contains the python scripts and file structure for generating
initial HiddenCube datasets and subsequent 'similar rotations'

'buffers' contains scripts and buffer folders that handle the communications
between the OpenVibe Scenario and the HiddenCube python scripts.  The OpenVibe
scenario will request images/similar rotations which the buffer scripts will then
fetch from the HiddenCubeDataset scripts and subsequently place into the buffer folders,
renaming and copying the image files appropriately for OpenVibe consumption while preserving image metadata
Furthermore, 'buffers' will contain timing buffer files that coordinate when a scenario
is ready for more images or when images are ready for a scenario's consumption.


'OpenVibeScenario' contains the OpenVibe-specific scenario .xml files