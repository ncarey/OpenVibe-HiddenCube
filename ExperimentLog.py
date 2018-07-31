import os
from os.path import join
import xml.etree.ElementTree as ET

#This class is for writing an xml log for the experiment, recording
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


    def __init__(self):
