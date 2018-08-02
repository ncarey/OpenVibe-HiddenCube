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


    def __init__(self, logpath, experiment_name, seed, similarity_factor, imagecount):
        self.logpath = logpath
        self.experiment_name = experiment_name
        self.seed = seed
        self.similarity_factor = similarity_factor
        self.imagecount = imagecount

        
