# -*- coding: utf-8 -*-
"""
Guillaumot Charlene 
Code to perform ALPACA's predictions on terminal (better time rendering performance)
"""

# # Usage:
# Two options
# From the terminal : 
# Do
#"C:\Users\ch1371gu\AppData\Local\NA-MIC\Slicer 5.2.2\Slicer.exe" --no-splash --no-main-window --python-script "0_rigid_predictions_10lds.py"
# Note that according to the paths you indicate, you should be inside the Slicer folder and your "alpaca_on_terminal.py" file as well 

# Option 2 : 
# Put the "alpaca_on_terminal.py" file inside the Slicer directory ("C:\Users\ch1371gu\AppData\Local\NA-MIC\Slicer 5.2.2\Slicer.exe")
# and from the Slicer Python console do : 
#exec(open("0_rigid_predictions.py").read())


# Check the working directory
import os
import re 
import numpy as np
import vtk.util.numpy_support as vtk_np
import ALPACA
self = ALPACA.ALPACALogic()
 

data_folder = "C:/Users/ch1371gu/Desktop/POSTE BIOGEOSCIENCES/Projet Ecol+/MAPPING/PIPELINE_CODES/pipeline_codes_repris_Nico/data/cranes_souris/"
sourceModelDirectory = data_folder + "Skull_Surfaces_sources"  # Directory that contains the mesh models used to train the labels predictions 
targetModelDirectory = data_folder + "Skull_Surfaces"  # Directory that contains the mesh to be landmark-projected

def create_folder(folder):
    # Check if the folder already exists
    if not os.path.exists(folder):
        # Create the folder if does not exist 
        os.makedirs(folder)
        print(f"Folder '{folder}' successfully created")
    else:
        print(f"Folder '{folder}' already exists")
compt = 0 

for sourceFile in os.listdir(sourceModelDirectory):
    compt = compt + 1
    indi_source= re.sub(".ply", "", sourceFile)
    print("indi_source")
    print(indi_source)
    
    for targetFile in os.listdir(targetModelDirectory):
        indi_target= re.sub(".ply", "", targetFile)
        print("indi_target")
        print(indi_target)
        
        # Load paths and files 
        sourceFilePath = os.path.join(f"{sourceModelDirectory}/",indi_source +".ply") #folder containing the 3d mesh model associated to the manually positioned landmarks'file available
        sourceLandmarkFile = os.path.join(f"{data_folder}Skull_Landmarks/", indi_source + ".fcsv") #indicate the manually positioned landmarks' file available
        targetFilePath = os.path.join(f"{targetModelDirectory}/",indi_target + ".ply")#folder of 3d mesh models to be landmarked
        outputDirectory= f"{data_folder}/output_alpaca/"#folder that will receive the predicted landmarks files 
        outputDirectory_indi = outputDirectory + indi_target
        create_folder(outputDirectory_indi)
        
        # Default parameters dictionnary
        parameters = {
        'projectionFactor': 0.01,   
        'pointDensity': 1.0,   
        'normalSearchRadius': 2.0, 
        'FPFHSearchRadius': 5.0, 
        'FPFHNeighbors' : 100,
        'distanceThreshold': 3, 
        'maxRANSAC': 1000000, 
        'RANSACConfidence': 0.999, 
        'ICPDistanceThreshold': 1.5, 
        'alpha': 2.0, 
        'beta': 2.0, 
        'CPDIterations': 100, 
        'CPDTolerance': 0.001,
        'Acceleration': 0 
        }
        skipScaling= 0
        
        print("LOAD MODELS")
        targetModelNode = slicer.util.loadModel(targetFilePath)
        sourceModelNode = slicer.util.loadModel(sourceFilePath)
        
             
        print ("DOWNSAMPLING")
        sourcePoints, targetPoints, sourceFeatures, targetFeatures, voxelSize, scaling = self.runSubsample(sourceModelNode,targetModelNode, skipScaling, parameters, False)
        
        print ("RIGID REGISTRATION")
        SimilarityTransform, similarityFlag = self.estimateTransform(sourcePoints, targetPoints, sourceFeatures, targetFeatures, voxelSize, skipScaling, parameters)
        sourceLandmarks, sourceLMNode = self.loadAndScaleFiducials(sourceLandmarkFile, scaling)
        print(len(sourceLandmarks))
        print(sourceLandmarks)
        sourceLandmarks_rigid= self.transform_numpy_points(sourceLandmarks,SimilarityTransform)
        
        print ("PRINT ORIGINAL AND INITIAL RIGID ESTIMATES ON SLICER")
        inputPoints = self.exportPointCloud(sourceLandmarks, "Original Landmarks")
        outputPoints_rigid = self.exportPointCloud(sourceLandmarks_rigid, "Initial rigid estimates") # print les points à l'écran 
        inputPoints_vtk = self.getFiducialPoints(inputPoints)
        outputPoints_vtk = self.getFiducialPoints(outputPoints_rigid)
        
        print ("TPS")
        deformedModelNode = self.applyTPSTransform(inputPoints_vtk, outputPoints_vtk, sourceModelNode, 'Warped Source Mesh')
        deformedModelNode.GetDisplayNode().SetVisibility(False)
        
        print ("PROJECTION")
        maxProjection = (targetModelNode.GetPolyData().GetLength()) *  parameters["projectionFactor"]
        projectedPoints = self.projectPointsPolydata(deformedModelNode.GetPolyData(), targetModelNode.GetPolyData(), outputPoints_vtk, maxProjection)
        projectedLMNode= slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsFiducialNode',"Refined Predicted Landmarks")
        print(parameters)
        
        for i in range(projectedPoints.GetNumberOfPoints()):
            point = projectedPoints.GetPoint(i)
            projectedLMNode.AddControlPoint(point)
        self.propagateLandmarkTypes(sourceLMNode, projectedLMNode)
        projectedLMNode.SetLocked(True)
        projectedLMNode.SetFixedNumberOfControlPoints(True)
        outputFilePath = os.path.join(outputDirectory_indi, indi_target + "_rep_"+ str(compt)+  ".fcsv")
        slicer.util.saveNode(projectedLMNode, outputFilePath)
        
        print ("REMOVE ELEMENTS FROM SCENE")
        slicer.mrmlScene.RemoveNode(deformedModelNode)
        slicer.mrmlScene.RemoveNode(projectedLMNode)   
        slicer.mrmlScene.RemoveNode(sourceModelNode)
        slicer.mrmlScene.RemoveNode(outputPoints_rigid)
        slicer.mrmlScene.RemoveNode(targetModelNode)
        slicer.mrmlScene.RemoveNode(sourceLMNode)
          


    
    
    
    
    



    













 










