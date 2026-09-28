#!/usr/bin/env python3
import pybullet as p
import pybullet_data
import time
import sys

if len(sys.argv) < 2:
    print("Usage: ./simulate.py <urdf_file>")
    sys.exit(1)

urdf_path = sys.argv[1]

p.connect(p.GUI)
p.setAdditionalSearchPath(pybullet_data.getDataPath())
p.setGravity(0, 0, -9.81)
planeId = p.loadURDF("plane.urdf")

# Load Robot
startPos = [0, 0, 0]
startOrn = p.getQuaternionFromEuler([0, 0, 0])
robotId = p.loadURDF(urdf_path, startPos, startOrn, useFixedBase=1)

# Number of Joints
numJoints = p.getNumJoints(robotId)
print("NumJoints: " + str(numJoints))

# Sliders (User Debug Parameters)
jointIds = []
paramIds = []

for j in range(numJoints):
    info = p.getJointInfo(robotId, j)
    jointName = info[1].decode("utf-8")
    jointType = info[2]
    
    if jointType == p.JOINT_REVOLUTE or jointType == p.JOINT_PRISMATIC:
        jointIds.append(j)

        # Slider for position control
        pId = p.addUserDebugParameter(jointName, -3.14, 3.14, 0)
        paramIds.append(pId)

# Simulation Loop
while True:
    
    # Read sliders and apply to joints
    for i in range(len(jointIds)):
        targetPos = p.readUserDebugParameter(paramIds[i])
        p.setJointMotorControl2(robotId, jointIds[i], p.POSITION_CONTROL, targetPosition=targetPos, force=500)
    
    p.stepSimulation()
    time.sleep(1./240.)
