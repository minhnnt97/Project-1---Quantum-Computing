#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 23 10:09:53 2019

@author: Minh Nguyen
"""

import numpy as np
from random import choices

def PrettyPrintBinary(state):
    i = 1
    for s in state:
        if i == len(state):
            print('{:g} |{:s}>'.format(s[0], s[1]))
        else:
            print('{:g} |{:s}>'.format(s[0], s[1]),end=' + ')
        i += 1

def PrettyPrintInteger(state):
    i = 1
    for s in state:
        num = int(s[1],2)   # Convert binary string to base-10 integer
        if i == len(state):
            print('{:g} |{:g}>'.format(s[0], num))
        else:
            print('{:g} |{:g}>'.format(s[0], num),end=' + ')
        i += 1
    
def StateToVec(state):  
    vector = np.zeros(2**len(state[0][1]))
    vector = [ float(v) for v in vector]
    for s in state:
        i = int(s[1],2)
        vector[i] = s[0]
    return vector

def VecToState(vector):
    state = []
    l = 0
    for i in range(len(vector)):
        v = vector[i]
        if v != 0.0:
            basis = "{0:b}".format(i)   # Convert base-10 integer to binary string
            state.append([v,basis])
            l = len(basis)
    for s in state:
        s[1] = s[1].zfill(l)
    state = [tuple(s) for s in state]
    return state
         
##############################

   
def tensorProd(matrix_list):
    product = matrix_list[0]
    i = 1
    while i < len(matrix_list):
        product = np.kron(matrix_list[i],product)
        i += 1
    return product




def HadamardArray(wire,total):     # Apply Hadamard matrix to wire i out of k wires
    Hadamard = 1/np.sqrt(2) * np.array([[1,1],
                                        [1,-1]])
    M_list = []
    for w in range(total):
        if w == total-wire-1:
            M_list.append(Hadamard)
            continue
        M_list.append(np.identity(2))
    
    matrix = tensorProd(M_list)
    return matrix




def PhaseArray(wire,total,phi):
    Phase = np.array([[1,           0],
                      [0,   np.exp(phi*1.j)]])
    M_list = []
    for w in range(total):
        if w == total-wire-1:
            M_list.append(Phase)
        else:
            M_list.append(np.identity(2))
    
    matrix = tensorProd(M_list)
    return matrix




# Currently only apply to target wires that is next to a control wire.
def CNOTArray(control,target,total):
    if total < 2:
        print('Not enough number of qubits to implement CNOT gate.')
    elif control == target:
        print('Invalid placement of CNOT gate (control wire and target wire must be different).')
    else:
        CNOTdown = np.array([[1,0,0,0],
                             [0,1,0,0],
                             [0,0,0,1],
                             [0,0,1,0]])    
    
        CNOTup = np.array([[1,0,0,0],
                           [0,0,0,1],
                           [0,0,1,0],
                           [0,1,0,0]])
        
        M_list = []
        w = 0
        while w < total:
            if target < control and w == total-1-control:
                M_list.append(CNOTup)
                w += 1
            elif target > control and w == total-1-target:
                M_list.append(CNOTdown)
                w += 1
            else:
                M_list.append(np.identity(2))
            w += 1
        matrix = tensorProd(M_list)
        return matrix




def UnitaryMatrix(num_wires,input_circuit):
    uni_matrix = np.identity(2**num_wires)
    for inp in input_circuit:
        if inp[0] == 'H':
            uni_matrix = HadamardArray(int(inp[1]),num_wires) @ uni_matrix
        elif inp[0] == 'P':
            uni_matrix = PhaseArray(int(inp[1]),num_wires,float(inp[2])) @ uni_matrix
        elif inp[0] == 'CNOT':
            uni_matrix = CNOTArray(int(inp[1]),int(inp[2]), num_wires) @ uni_matrix
    tol = 1E-10
    uni_matrix.real[np.abs(uni_matrix.real) < tol] = 0
    uni_matrix.imag[np.abs(uni_matrix.imag) < tol] = 0
    return uni_matrix
           


     
def ReadInput(fileName):
    myInput_lines = open(fileName).readlines()
    myInput = []
    numberOfWires = int(myInput_lines[0].strip())
    #myInput.append(numberOfWires)
    '''
    start = 1
    end = 0
    if myInput_lines[1].split()[0] == 'INITSTATE':
        start += 1
    if myInput_lines[-1].split()[0] == 'MEASURE':
        end -= 1
    '''
    for line in myInput_lines[1:]:
        myInput.append(line.split())
    return (numberOfWires,myInput)




def Measure(state):
    result = []
    probability = []
    for s in state:
        probability.append(np.abs(s[0])**2)
        result.append(s[1])
    total_probability = 0
    for p in probability: total_probability += p
    if np.abs(total_probability - 1) > 10**6:
        print('Total probability does not add up to 1.')
        return
    return choices(result,weights=probability)[0]
    



def GetInputState(numberOfWires,input_circuit):
    if input_circuit[0][0] == 'INITSTATE':
        if input_circuit[0][1] == 'FILE':
            vec = []
            with open('%s.dms' % input_circuit[0][2]) as f:
                for line in f:
                    l = line.strip().split()
                    v = '%s+%sj' % (l[0],l[1])
                    v = v.replace(' ','')   # Clear white spaces
                    v = v.replace('+-','-') # Change '+-' to just '-'
                    print(v)
                    vec.append(complex(v))
            return VecToState(vec)
        elif input_circuit[0][1] == 'BASIS':
            state = [(1,input_circuit[0][2].strip('|').strip('>'))]
            return state
    else:
        return [(1,'0'*numberOfWires)]



def runCircuit(stateFile):
    num_wires, input_circuit = ReadInput(stateFile)
    
    


#testState = [
#        (np.sqrt(0.1)*1.j, '101'),
#        (np.sqrt(0.5), '000') ,
#        (-np.sqrt(0.4), '010' )
#        ]
#testState2 = [
#        (np.sqrt(0.1)*3.j+2, '111'),
#        (np.sqrt(0.5)-0.1, '110') ,
#        (-np.sqrt(0.4)-2.j, '001' )
#        ]

#PrettyPrintBinary(testState2)
#PrettyPrintInteger(testState2)

#print(StateToVec(testState2))
#print(VecToState(StateToVec(testState2)))

#HadamardArray(1,2)
#PhaseArray(0,2,0.1)
'''
dim = 3
temp_sum = 0
for i in range(2**dim): temp_sum += i
testState = [(np.sqrt(i/temp_sum),'{0:b}'.format(i).zfill(dim)) for i in range(2**dim)]
print(Measure(testState))
'''
#wires_total, gates = ReadInput('input.circuit')
#print(wires_total)
#print(gates)
#print(UnitaryMatrix(wires_total,gates))

#final_state = GetInputState(wires_total,gates)
#print(final_state)

