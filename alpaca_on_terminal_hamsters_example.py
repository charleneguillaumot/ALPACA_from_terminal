# -*- coding: utf-8 -*-
"""
Guillaumot Charlene 
Code to perform ALPACA's predictions on terminal (better time rendering performance)
"""

# # Usage:
# Two options
# From the terminal : 
# Do
#"C:\Users\ch1371gu\AppData\Local\NA-MIC\Slicer 5.2.2\Slicer.exe" --no-splash --no-main-window --python-script "alpaca_on_terminal_hamsters.py"
# Note that according to the paths you indicate, you should be inside the Slicer folder and your "alpaca_on_terminal.py" file as well 

# Option 2 : 
# Put the "alpaca_on_terminal.py" file inside the Slicer directory ("C:\Users\ch1371gu\AppData\Local\NA-MIC\Slicer 5.2.2\Slicer.exe")
# and from the Slicer Python console do : 
#exec(open("alpaca_on_terminal_hamsters.py").read())


# Check the working directory
import os
import re 
import numpy as np
import vtk.util.numpy_support as vtk_np
import ALPACA
self = ALPACA.ALPACALogic()
 

data_folder = "C:/Users/ch1371gu/Desktop/POSTE BIOGEOSCIENCES/Projet Ecol+/MAPPING/TRIALS_MESH_SUBSET/INDIVIDUS/cranes_Morgane/"
sourceModelDirectory = data_folder + "Skull_Surfaces"  # Directory that contains the mesh models used to train the labels predictions 

def create_folder(folder):
    # Check if the folder already exists
    if not os.path.exists(folder):
        # Create the folder if does not exist 
        os.makedirs(folder)
        print(f"Folder '{folder}' successfully created")
    else:
        print(f"Folder '{folder}' already exists")


for sourceFileName in os.listdir(sourceModelDirectory):
     targetFileName = re.sub(".ply", "", sourceFileName)

     indi=  targetFileName

     sourceFilePath = os.path.join(f"{data_folder}Skull_Surfaces/", indi + ".ply""") #folder containing the 3d mesh model associated to the manually positioned landmarks'file available
     sourceLandmarkFile = os.path.join(f"{data_folder}Skull_Landmarks/H-C3FH-1_Skull.fcsv") #indicate the manually positioned landmarks' file available
     targetFilePath = os.path.join(f"{data_folder}Skull_Surfaces/",indi + ".ply")#folder of 3d mesh models to be landmarked
     outputDirectory= f"{data_folder}/output_alpaca/"#folder that will receive the predicted landmarks files 
     outputDirectory_indi = outputDirectory + indi
     create_folder(outputDirectory_indi)

     skipScaling= 0

     # Change alpha and beta parameters 
     # here, 4 files will be produced per individual: alpha1-beta4; alpha1-beta6; alpha10-beta4; alpha10-beta6
     alpha = [1,10] 
     beta = [4,6]

     # Default parameters dictionnary
     parameters = {
     'projectionFactor': 0.01,   
     'pointDensity': 1.0,   
     'normalSearchRadius': 2.0, 
     'FPFHSearchRadius': 5.0, 
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
     
     #-----------------------
     # MESH 3D MODELS LOADING 
     #-----------------------
     print("LOAD MODELS")
     targetModelNode = slicer.util.loadModel(targetFilePath)
     sourceModelNode = slicer.util.loadModel(sourceFilePath)
     
     #----------------------------------------
     #  Downsampling and global registration 
     #----------------------------------------  
     print ("DOWNSAMPLING AND GLOBAL REGISTRATION")
     sourcePoints, targetPoints, sourceFeatures, targetFeatures, voxelSize, scaling = self.runSubsample(sourceModelNode,targetModelNode, skipScaling, parameters)
     # Point cloud sampling, rigid transform definition and associated properties (voxel size, scaling...), according to the chosen parameters (skipscling, pointdensity)
     # these properties are changed 
     
     #--------------------
     # Local registration
     #--------------------
     # After the global registration alignment, we get an imperfect rigid transform. The local registration aims at adjusting/improving the aligment
     # To each source point, will be assigned each nearest target point : point to plane approache (ICP algorithm)
     # The ICPDistanceThreshold is a parameter that could be modulated to influence this part
     print ("LOCAL REGISTRATION")
     ICPTransform = self.estimateTransform(sourcePoints, targetPoints, sourceFeatures, targetFeatures, voxelSize, skipScaling, parameters)
     sourceLandmarks, sourceLMNode = self.loadAndScaleFiducials(sourceLandmarkFile, scaling)
     sourceLandmarks.transform(ICPTransform)
     sourcePoints.transform(ICPTransform)
     # local registration output : improved rigid transform 
     
     for param_alpha in alpha: 
         parameters["alpha"] = param_alpha
         print("alpha parameter loop = ", param_alpha)
         
         for param_beta in beta: 
             parameters["beta"] = param_beta
             print("beta parameter loop = ", param_beta)
             
             #-------------------------
             # Deformable registration  
             #-------------------------
             # The rigid source transform set of points is deformed to match the target point cloud
             # Use of the Coherent Point Drift algorithm (CPD)
             # The source point cloud is assimilated to a mixted gaussian model (GMM), methods which implies two main parameters : alpha and beta
             # the CPDIterations and CPDTolerence parameters also belong to this part of the code 
             # Final step : the predicted points are projected on the target surface mesh
             
             print ("DEFORMABLE REGISTRATION")
             registeredSourceLM = self.runCPDRegistration(sourceLandmarks.points, sourcePoints.points, targetPoints.points, parameters)
             print("CREATE PREDICTED LANDMARKS")
             outputPoints = self.exportPointCloud(registeredSourceLM, "Init.Pred.LM")    
             
             # projectionFactor parameter: used for this final part -> the landmark points are projected on the target mesh, the projectionFactor parameter sets a tolerance threshold in point movments while projecting them  
             if  parameters["projectionFactor"] == 0:
                 print("you chose projectionFactor = 0, so....XXX ")
                 self.propagateLandmarkTypes(sourceLMNode, outputPoints)
                 outputFilePath = os.path.join(outputDirectory, indi + "_alpha_"+ str(param_alpha) +"_beta_" + str(param_beta) + "_projFactor_" + str(param_proj) + "_predALPACA.fcsv")
                 slicer.util.saveNode(outputPoints, outputFilePath)
                 slicer.mrmlScene.RemoveNode(outputPoints)
                 slicer.mrmlScene.RemoveNode(sourceModelNode)
                 slicer.mrmlScene.RemoveNode(targetModelNode)
                 slicer.mrmlScene.RemoveNode(sourceLMNode)
             else:
                 print("you chose projectionFactor different from 0, so landmarks are projected on target mesh")
                 inputPoints = self.exportPointCloud(sourceLandmarks.points, "Original Landmarks")
                 inputPoints_vtk = self.getFiducialPoints(inputPoints)
                 outputPoints_vtk = self.getFiducialPoints(outputPoints)

                 ICPTransformNode = self.convertMatrixToTransformNode(ICPTransform, 'Rigid Transformation Matrix')
                 sourceModelNode.SetAndObserveTransformNodeID(ICPTransformNode.GetID())
                 deformedModelNode = self.applyTPSTransform(inputPoints_vtk, outputPoints_vtk, sourceModelNode, 'Warped Source Mesh')
                 deformedModelNode.GetDisplayNode().SetVisibility(False)

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
                 outputFilePath = os.path.join(outputDirectory_indi, indi + "_alpha_"+ str(param_alpha) +"_beta" + str(param_beta) + "_.fcsv")
                 slicer.util.saveNode(projectedLMNode, outputFilePath)
                 slicer.mrmlScene.RemoveNode(deformedModelNode)
                 slicer.mrmlScene.RemoveNode(projectedLMNode)         
       
     slicer.mrmlScene.RemoveNode(sourceModelNode)
     slicer.mrmlScene.RemoveNode(outputPoints)
     slicer.mrmlScene.RemoveNode(targetModelNode)
     slicer.mrmlScene.RemoveNode(sourceLMNode)







        













     










