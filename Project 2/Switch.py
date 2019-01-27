# Project 2 for OMS6250
#
# This defines a Switch that can can send and receive spanning tree 
# messages to converge on a final loop free forwarding topology.  This
# class is a child class (specialization) of the StpSwitch class.  To 
# remain within the spirit of the project, the only inherited members
# functions the student is permitted to use are:
#
# self.switchID                   (the ID number of this switch object)
# self.links                      (the list of swtich IDs connected to this switch object)
# self.send_message(Message msg)  (Sends a Message object to another switch)
#
# Student code MUST use the send_message function to implement the algorithm - 
# a non-distributed algorithm will not receive credit.
#
# Student code should NOT access the following members, otherwise they may violate
# the spirit of the project:
#
# topolink (parameter passed to initialization function)
# self.topology (link to the greater topology structure used for message passing)
#
# Copyright 2016 Michael Brown, updated by Kelly Parks
#           Based on prior work by Sean Donovan, 2015
			    												

from Message import *
from StpSwitch import *
from bisect import bisect_left

class Switch(StpSwitch):

    def __init__(self, idNum, topolink, neighbors):    
        # Invoke the super class constructor, which makes available to this object the following members:
        # -self.switchID                   (the ID number of this switch object)
        # -self.links                      (the list of swtich IDs connected to this switch object)
        super(Switch, self).__init__(idNum, topolink, neighbors)
        #TODO: Define a data structure to keep track of which links are part of / not part of the spanning tree.

#	print (self.switchID)
#	print ('******************')
#	print (self.links)
	# INITIAL PARAMETERS SETUP
#####################
	# DISTANCE FIELD IS SET TO 0 -> DISTANCE FROM NODE TO ITSELF IS ALWAYS ZERO	
	self.distance = 0        

	# ROOT IS GOING TO BE INITIALIZED TO EACH ROOT OF SPANNING TREE
	self.root = self.switchID

	# NODE WITH WHICH WE CAN COMPARE SWITH ID VALUES - INITIALIZED TO SWITCH ID
	self.node = self.switchID

	# SPANTREE LINKS EMPTY STACK WHERE ALL TRUE LINKS OF MINIMUM SPANNING TREE ARE ADDED
	self.spantree_links = []
	
	# NUMBER OF TOTAL LINKS IN GIVEN TOPO
	self.num_total_links = len(self.links)



    def send_initial_messages(self):
        #TODO: This function needs to create and send the initial messages from this switch.
        #      Messages are sent via the superclass method send_message(Message msg) - see Message.py.
	#      Use self.send_message(msg) to send this.  DO NOT use self.topology.send_message(msg)
	
	# GIVEN THAT
	# msg = Message(claimedRoot, distanceToRoot, originID, destinationID, pathThrough) 

	# ROOT AND ORIGIN WILL BE SAME SWITCH ID
	# DISTANCE = 0
	# DESTINATION IDS ARE IN THE LINKS LIST 

	for i in range(self.num_total_links):
		msg = Message(self.switchID,0,self.switchID,self.links[i],False)
		self.send_message(msg)

	return msg
        
    def process_message(self, message):
        #TODO: This function needs to accept an incoming message and process it accordingly.
        #      This function is called every time the switch receives a new message.

#	if msg = Message(self.switchID,0,self.switchID,self.links[i],True)
	
	# TEST TO SEE IF PATH THROUGH IS FALSE
	if message.pathThrough == False:
		# IF ORIGIN ID OF GIVEN MESSAGE IS IN TRUE LINK AND CHECK THAT ORIGIN ID IS NOT THE SAME AS INITIALIZED VALUES
		if message.origin in self.spantree_links:
			if message.origin != self.node:	
				self.spantree_links.remove(message.origin)

	# MESSAGE PATH THROUGH IS TRUE	
	# ORIGIN ID IS A TRUE SPANNING TREE LINK
	# ADD TO OUR EXISTING TRUE LINKS
	else:
		# IN CASE OF LARGE LISTS, EFFICIENT TO USE BISECT METHOD
#		self.spantree_links.sort()
#		if not bisect_left(self.spantree_links, message.origin):
		if message.origin not in self.spantree_links:
			self.spantree_links.append(message.origin)

	# NOW MODIFICATION OF THE ACTUAL SPANNING TREE LINKS HAS BEEN VALIDATED
	# ELECTING THE ROOTS OF THE TREE
	
	if message.root < self.root: # LOWER SWITCHID FOUND
		# INITIALIZING THE NEW ROOT, DISTANCE, AND UPDATING NDOE
		self.root = message.root
		self.distance = message.distance + 1
		self.node = message.origin
		
		# HAVE TO ADD ORIGIN ID TO SPANNING TREE
		if self.node not in self.spantree_links:
			self.spantree_links.append(self.node)

		# CHANGING MESSAGE VALUES
		for i in range(self.num_total_links):
			message = Message(self.root, self.distance, self.switchID, self.links[i], self.node == self.links[i])
			self.send_message(message)
	
	if message.root == self.root:
		# OLD MESSAGE NEEDS TO CHANGE INCLUDING THE SAME ROOT AND NEW NODE
		# HAS SHORTER DISTANCE WITH SAME ROOT
		if message.distance + 1 < self.distance:
			
			# CHANGING THE DISTANCE FOR SPAN TREE

			self.distance = message.distance + 1

			# INCLUDING NEIGHBOR AS THE ORIGIN ID
			# NEIGHBOR TO ROOT 
			
			neighbor = message.origin
			
			# MODIFYING THE NEW MESSAGE TO INCLUDE NEIGHBOR AND NEW DISTANCE
			
			for i in range(self.num_total_links):
				message = Message(self.root, self.distance, self.switchID, self.links[i], neighbor == self.links[i])
				self.send_message(message)
			
			# REMOVING OLD NODE AND ADDING NEIGHBOR
			self.spantree_links.remove(self.node)
			self.node = neighbor
			
			if neighbor not in self.spantree_links:
				self.spantree_links += neighbor


	# EDGE CASE WHERE ROOT AND DISTANCE IS SAME 
	# CURRENT PATH HAS LOWER SWITCHID
	
	if message.root == self.root:
		if message.distance + 1 == self.distance:
			if self.node > message.origin:
				neighbor = message.origin

				for i in range(self.num_total_links):
					message = Message(self.root, self.distance, self.switchID, self.links[i], neighbor == self.links[i])
					self.send_message(message)
				
				self.spantree_links.remove(self.node)
				self.node = neighbor
				
				if neighbor not in self.spantree_links:
					self.spantree_links.append(neighbor)

        return
        
    def generate_logstring(self):
        #TODO: This function needs to return a logstring for this particular switch.  The
        #      string represents the active forwarding links for this switch and is invoked 
        #      only after the simulaton is complete.  Output the links included in the 
        #      spanning tree by increasing destination switch ID on a single line. 
        #      Print links as '(source switch id) - (destination switch id)', separating links 
        #      with a comma - ','.  
        #
        #      For example, given a spanning tree (1 ----- 2 ----- 3), a correct output string 
        #      for switch 2 would have the following text:
        #      2 - 1, 2 - 3
        #      A full example of a valid output file is included (sample_output.txt) with the project #skeleton.
	
	
	self.spantree_links.sort()
	result = []
	for final_id in self.spantree_links:
		result.append(str(self.switchID) + ' - ' + str(final_id))
	
#	print (result)
#$	print (result, sep = " , ")
#	return (result, sep = " , ")

	result = ", ".join(result)
	return result
#        return "switch logstring"
