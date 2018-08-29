import os
from os.path import join
#import xml.etree.ElementTree as ET

#This class is for writing a log for the experiment, recording
#images shown per batch of RSVP and which image data was triggered on
class ExperimentLog:


#<ExperimentName>
#   <MetaData>
#       <NumImagesPerIteration>
#       <SimilarityFactor>
#       <RandomSeed>
#       <SomethingAboutHowSubsequentImagesSelected>
#   <Data>
#       <RSVPIterationNumber>
#           <imagename>
#               <imageFilePath>
#               <votes>
#           <imagename>
#               <imageFilePath>
#               <votes>

    def recordImageVotes(self, votes, decoder):

        log_file = open(self.logpath, 'a')
        log_file.write("Iteration {0}\n".format(self.iteration))
        for cur_target_name in votes:
            vote_count = votes[cur_target_name]
            dataset_image_ID = decoder["{num:02d}".format(num=int(cur_target_name))].replace(".png","")
            log_file.write("\t{0}, {1}\n".format(dataset_image_ID, vote_count))

        log_file.close()
        self.iteration = self.iteration + 1

    def __init__(self, logpath, experiment_name, seed, similarity_factor, imagecount):
        self.logpath = logpath
        self.experiment_name = experiment_name
        self.seed = seed
        self.similarity_factor = similarity_factor
        self.imagecount = imagecount
        self.iteration = 0
        
        log_file = open(self.logpath, 'w')
        log_file.write("Name: {0}, rand seed: {1}, similarity_factor: {2}, imagecount: {3}".format(self.experiment_name,
                                                                                                  self.seed,
                                                                                                  self.similarity_factor,
                                                                                                  self.imagecount))
        log_file.close()
