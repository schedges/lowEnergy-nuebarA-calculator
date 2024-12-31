import ROOT
import sys
from array import array

#####################################
#Check user supplied input file name#
#####################################
if len(sys.argv) < 2:
  print("\nERROR: Incorrect call!")
  print("Correct usage is python polimiParser.py <dumn1 filename> <optional: ptrac file for source particle locations>\n")
  sys.exit()

############################
#Open data files, load data#
############################
dumnFilename=sys.argv[1]
dumnFile=open(dumnFilename, "r")
dumnText=dumnFile.read()
dumnFile.close()
dumnLines=dumnText.split('\n')

##################
#Open output file#
##################
outFile=ROOT.TFile(dumnFilename+".root","RECREATE") #output file

###########################
##OPTIONAL PTRAC HANDLING##
###########################
hasPtrac=0
ptracHasEnergy=0
if len(sys.argv)==3:
  hasPtrac=1
  ptracFile=open(sys.argv[2],"r")
  ptracText=ptracFile.read()
  ptracFile.close()

  sourceTree=ROOT.TTree("sourceTree","Source location/history #")

  ptracLines=ptracText.split('\n')
  histNum=array('i',[0])
  sourceX=array('d',[0.])
  sourceY=array('d',[0.])
  sourceZ=array('d',[0.])
  sourceE=array('d',[0.])
  sourceTree.Branch('histNum',histNum,'histNum/I')
  sourceTree.Branch('sourceX',sourceX,'sourceX/D')
  sourceTree.Branch('sourceY',sourceY,'sourceY/D')
  sourceTree.Branch('sourceZ',sourceZ,'sourceZ/D')
  sourceTree.Branch('sourceE',sourceE,'sourceE/D')
  sourceXs=[]
  sourceYs=[]
  sourceZs=[]
  sourceEs=[]

  firstLineFound=0
  for iline,line in enumerate(ptracLines):
    if iline%100000==0:
      print("On ptrac line {0} of {1}".format(iline,len(ptracLines)))
      
    if firstLineFound==0:
      lineParts=line.split()
      if len(lineParts)==2:
        if lineParts[0]=="1" and lineParts[1]=="1000":
          firstLine=iline
          firstLineFound=1
 
    if firstLineFound==0:
      continue
          
    if iline>=firstLine:
      if not line=="":
        if (iline-firstLine)%3==0:
          lineParts=line.split()
          histNum[0]=int(lineParts[0])
        elif (iline-firstLine-1)%3==0:
          continue
        elif (iline-firstLine-2)%3==0:
          lineParts=line.split()
          sourceX[0]=float(lineParts[0])
          sourceY[0]=float(lineParts[1])
          sourceZ[0]=float(lineParts[2])
          sourceXs.append(sourceX[0])
          sourceYs.append(sourceY[0])
          sourceZs.append(sourceZ[0])
          if len(lineParts)==9:
            ptracHasEnergy=1
            sourceE[0]=float(lineParts[6])
            sourceEs.append(sourceE[0])
          else:
            sourceE[0]=0
          sourceTree.Fill()
  outFile.cd()
  sourceTree.Write("sourceTree",ROOT.TObject.kOverwrite)

###############
#Create TTrees#
###############
polimiTree=ROOT.TTree("polimiTree","Minimally modified polimi output")

historyNum=array('d',[0.])
particleNum=array('d',[0.])
projectileType=array('d',[0.])
interactionType=array('d',[0.])
targetNucleus=array('d',[0.])
cellNum=array('d',[0.])
energy=array('d',[0.])
time=array('d',[0.])
xLoc=array('d',[0.])
yLoc=array('d',[0.])
zLoc=array('d',[0.])
particleWeight=array('d',[0.])
generationNum=array('d',[0.])
numScatterings=array('d',[0.])
code=array('d',[0.])
energyPreScatter=array('d',[0.])

polimiTree.Branch('historyNum',historyNum,'historyNum/D')
polimiTree.Branch('particleNum',particleNum,'particleNum/D')
polimiTree.Branch('projectileType',projectileType,'projectileType/D')
polimiTree.Branch('interactionType',interactionType,'interactionType/D')
polimiTree.Branch('targetNucleus',targetNucleus,'targetNucleus/D')
polimiTree.Branch('cellNum',cellNum,'cellNum/D')
polimiTree.Branch('energy',energy,'energy/D')
polimiTree.Branch('time',time,'time/D')
polimiTree.Branch('xLoc',xLoc,'xLoc/D')
polimiTree.Branch('yLoc',yLoc,'yLoc/D')
polimiTree.Branch('zLoc',zLoc,'zLoc/D')
if hasPtrac==1:
  polimiTree.Branch('sourceX',sourceX,'sourceX/D')
  polimiTree.Branch('sourceY',sourceY,'sourceY/D')
  polimiTree.Branch('sourceZ',sourceZ,'sourceZ/D')
  if ptracHasEnergy==1:
    polimiTree.Branch('sourceE',sourceE,'sourceE/D')
polimiTree.Branch('particleWeight',particleWeight,'particleWeight/D')
polimiTree.Branch('generationNum',generationNum,'hisgenerationNumtoryNum/D')
polimiTree.Branch('numScatterings',numScatterings,'numScatterings/D')
polimiTree.Branch('code',code,'code/D')
polimiTree.Branch('energyPreScatter',energyPreScatter,'energyPreScatter/D')

#Pre-loop prep
prevHistoryNum=0. #Used to tell when we're onto a new throw
depositionList=[] #Stores depositions from a throw. These are not time-sorted, so we sort before filling our tree

#Step through data file
for index,line in enumerate(dumnLines):
  
  if index%100000==0:
    print("On dumn1 line {0} of {1}".format(index,len(dumnLines)))
  
  #Blank line at end of file, skip
  if line=="":
    continue
    
  #split line by white space
  args = line.split()
  
  #Get history number
  currentHistoryNumber=float(args[0])
  
  #If it's a new historyNum (and not the first event), sort the data by time
  if not currentHistoryNumber==prevHistoryNum and not prevHistoryNum==0.:
    depositionList=sorted(depositionList, key=lambda x: x[7], reverse=False)
    for deposition in depositionList:
      historyNum[0]=deposition[0]
      particleNum[0]=deposition[1]
      projectileType[0]=deposition[2]
      interactionType[0]=deposition[3]
      targetNucleus[0]=deposition[4]
      cellNum[0]=deposition[5]
      energy[0]=deposition[6]
      time[0]=deposition[7]*10.
      xLoc[0]=deposition[8]
      yLoc[0]=deposition[9]
      zLoc[0]=deposition[10]
      if hasPtrac==1:
        sourceX[0]=sourceXs[int(historyNum[0])-1]
        sourceY[0]=sourceYs[int(historyNum[0])-1]
        sourceZ[0]=sourceZs[int(historyNum[0])-1]
        if ptracHasEnergy==1:
          sourceE[0]=sourceEs[int(historyNum[0])-1]
      particleWeight[0]=deposition[11]
      generationNum[0]=deposition[12]
      numScatterings[0]=deposition[13]
      code[0]=deposition[14]
      energyPreScatter[0]=deposition[15]
      
      #fill
      polimiTree.Fill()
    
    #Empty list of depositions
    depositionList=[]
    
  #Otherwise, add deposition to list
  depositionList.append([float(i) for i in args])
    
  #Update prevHistory Number
  prevHistoryNum=currentHistoryNumber
  
#Need to manually fill last event num

depositionList=sorted(depositionList, key=lambda x: x[7], reverse=True)
for deposition in depositionList:
  historyNum[0]=deposition[0]
  particleNum[0]=deposition[1]
  projectileType[0]=deposition[2]
  interactionType[0]=deposition[3]
  targetNucleus[0]=deposition[4]
  cellNum[0]=deposition[5]
  energy[0]=deposition[6]
  time[0]=deposition[7]*10.
  xLoc[0]=deposition[8]
  yLoc[0]=deposition[9]
  zLoc[0]=deposition[10]
  if hasPtrac==1:
    sourceX[0]=sourceXs[int(historyNum[0])-1]
    sourceY[0]=sourceYs[int(historyNum[0])-1]
    sourceZ[0]=sourceZs[int(historyNum[0])-1]
    if ptracHasEnergy==1:
      sourceE[0]=sourceEs[int(historyNum[0])-1]
  particleWeight[0]=deposition[11]
  generationNum[0]=deposition[12]
  numScatterings[0]=deposition[13]
  code[0]=deposition[14]
  energyPreScatter[0]=deposition[15]
  
  #fill
  polimiTree.Fill()

#write ttree
polimiTree.Write("polimiTree",ROOT.TObject.kOverwrite)

#close output file
outFile.Close()
