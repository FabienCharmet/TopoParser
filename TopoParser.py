# -*- coding: iso-8859-1 -*-
from pyparsing import *
from shutil import copyfile
import subprocess
import sys, getopt
import string
from copy import deepcopy

keyword = ['Node','Link']
varname = alphanums + '-_'
list_node = []
list_link = []
list_time = []

#####################
###     TYPES     ###
#####################
Node = Word('(', max=1) + Word('Node')("type") + Word(varname)("node_name") + Word(')',max=1)
Time = Word('(', max=1) + Word('Time')("type") + Word(varname)("time_name") + Word(')',max=1)
Data = Word('(', max=1) + Word('Data')("type") + Word(varname)("data_name") + Word(')',max=1)
User = Word('(', max=1) + Word('User')("type") + Word(varname)("user_name") + Word(')',max=1)

#####################
##  TIME FUNCTIONS ##
#####################
Before =  Word('(', max=1) + Word('Before')("type") + Word(',', max=1) + Word(varname)("before_time") + Word(',', max=1) + Word(varname)("after_time")  + Word(')',max=1)

#####################
###   FUNCTIONS   ###
#####################
Link = Word('(', max=1) + Word('Link')("type") + Word(varname)("src_link") + Word(',', max=1) + Word(varname)("dst_link") + Word(',', max=1) + Word(varname)("begin_time") + Word(',', max=1) + Word(varname)("end_time") + Word(')',max=1)
DataIsAuthorized = Word('(', max=1) + Optional(Word('Not')("Not")) + Word('Data-IsAuthorized')("type") + Word(varname)("user_name") + Word(',', max=1) + Word(varname)("data_name") + Word(',', max=1) + Word(varname)("before_time") + Word(',', max=1) + Word(varname)("after_time")  +  Word(')',max=1)
DataAtNode = Word('(', max=1) + Optional(Word('Not')("Not")) + Word('Data-At-Node')("type") + Word(varname)("data_name") + Word(',', max=1) + Word(varname)("node_name") + Word(',', max=1) + Word(varname)("before_time") + Word(',', max=1) + Word(varname)("after_time")  +  Word(')',max=1)
ReadsAtNode = Word('(', max=1) + Optional(Word('Not')("Not")) + Word('Reads-At-Node')("type") + Word(varname)("user_name") + Word(',', max=1) + Word(varname)("data_name") + Word(',', max=1) + Word(varname)("node_name") + Word(',', max=1) + Word(varname)("before_time") + Word(',', max=1) + Word(varname)("after_time")  +  Word(')',max=1)

Element = Node | Link | Time | Before | Data | User | DataIsAuthorized | ReadsAtNode | DataAtNode



def replace_char(src,target,filename):
    lines = []
    with open(filename) as infile:
        for line in infile:
            line = line.replace(src, target)
            if line.rstrip():
                lines.append(line) 
    with open(filename, 'w') as outfile:
        for line in lines:
            outfile.write(line)

def print_nodes(nodes):
    str_node=""
    for n in nodes:
	str_node+= "Node(" + str(n) + ") "
    print str_node

def print_links(links):
    str_links=""
    for l in links:
	str_links+="SetLinks(" + str(l[0]) + "," + str(l[1]) + "," + str(l[2]) + "," +str(l[3]) + ")\n" 
    print str_links


def move_migration_algo():
    new_time = []
    new_link = []
    temp_nodes = list_node[:]
    new_nodes = []
    for l in list_link:
	l[2]=time_token([0])
	l[3]=time_token([1])
    new_link = deepcopy(list_link)
    for n in temp_nodes:
	new_n = "new_" + n
	new_nodes.append(new_n)
        for l in new_link:
            if(l[0]==n):	
		l[0]=new_n
            if(l[1]==n):
		l[1]=new_n
	    l[2]="time-2"
	    l[3]="time-3"
    #print "new nodes " str(new_nodes)
    #print "new link " + str(temp_link)i
    new_time.append("time-0")
    new_time.append("time-1")
    new_time.append("time-2")
    new_time.append("time-3")
    print_nodes(new_nodes)
    print_links(new_link)
    return new_nodes,new_link,new_time

def time_token(time_vector):
    timeslot="time-"
    letter_tab=string.ascii_lowercase
    for t in time_vector:
	timeslot+=letter_tab[t]
    timeslot="time-" + str(time_vector[0])
    return timeslot


def iterative_migration_algo():
    migrated_nodes = []
    new_link = []
    new_nodes = []
    old_nodes = []
    all_link = []
    remaining_nodes = list_node[:]
    temp_link = list_link[:]
    new_time = []
    count = 1
    count_time = 1
    
    for l in temp_link:
	l[2]=time_token([0])
	l[3]=time_token([1])
    new_time.append(time_token([0]))

    while(len(remaining_nodes)>0):
	x = remaining_nodes[0]
	new_x = "new_" + x
	new_nodes.append(new_x)
	for l in temp_link:
	    if((x == l[0]) and (l[1] in remaining_nodes)):
   	        print "setlink " + new_x + " " + l[1]
		new_link.append([new_x,l[1],time_token([count_time]),time_token([count_time+1])])
		all_link.append([new_x,l[1],time_token([count_time]),time_token([count_time+1])])
	    if((x == l[1]) and (l[0] in remaining_nodes)):
   	        print "setlink " + new_x + " " + l[0]
		new_link.append([new_x,l[0],time_token([count_time]),time_token([count_time+1])])
		all_link.append([new_x,l[0],time_token([count_time]),time_token([count_time+1])])
	for l in new_link:
	    if((x == l[0]) and (l[1] in migrated_nodes)):
   	        print "setlink " + new_x + " " + l[1]
		new_link.append([new_x,l[1],time_token([count_time]),time_token([count_time+1])])
		all_link.append([new_x,l[1],time_token([count_time]),time_token([count_time+1])])
		print "Deleted link: " + str(l)
		new_link.remove(l)		
	    if((x == l[1]) and (l[0] in migrated_nodes)):
   	        print "setlink " + new_x + " " + l[0]
		new_link.append([new_x,l[0],time_token([count_time]),time_token([count_time+1])])
		all_link.append([new_x,l[0],time_token([count_time]),time_token([count_time+1])])
		print "Deleted link: " + str(l)
		new_link.remove(l)		
	
	new_time.append(time_token([count_time]))
	migrated_nodes.append(new_x)
	old_nodes.append(x)
	remaining_nodes.remove(x)
	count_time+=1
    new_time.append(time_token([count_time]))
    for l in new_link:
	l[3]=time_token([count_time])
    print_nodes(new_nodes)
    print_links(all_link)
    return new_nodes, all_link, new_time		
		


def parse(filename):
    replace_char('\n','',filename)
    replace_char(')',')\n',filename)
    data_insert=""
    user_insert=""
    time_insert=""
    before_insert=""
    dataisauthorized_insert=""
    readsatnode_insert=""
    dataatnode_insert=""

    with open(filename) as f:
        for line in f:
           s = Element.parseString(line)
	   elt_type = s["type"]
	   if elt_type == "Node":
	       name = s["node_name"]
	       list_node.append(name)
	   if elt_type == "Data":
	       name = s["data_name"]
	       data_insert += "(declare-constant '" + name + " :sort 'data)\n"
	   if elt_type == "User":
	       name = s["user_name"]
	       user_insert += "(declare-constant '" + name + " :sort 'user)\n"
	   if elt_type == "Link":
	       nbegin = s["src_link"]
	       nend = s["dst_link"]
               tbegin = s["begin_time"]
	       tend = s["end_time"]
	       list_link.append([nbegin,nend,tbegin,tend])
	   if elt_type == "Time":
      	       name = s["time_name"]
	       list_time.append(name)
	       time_insert += "(declare-constant '" + name + " :sort 'time-point :constructor t)\n"

	   if elt_type == "Before":
	       before_time = s["before_time"]
	       after_time = s["after_time"]
	       before_insert += "(before " + before_time + " " + after_time + ")\n"

	   if elt_type == "Data-IsAuthorized":
               tbegin = s["before_time"]
	       tend = s["after_time"]
	       name = s["user_name"]
	       data = s["data_name"]
	       temp = "'(data-isauthorized " + name + " " + data + " (make-interval " + tbegin + " " +     tend + "))"
	       try:
		   nots = s["Not"]
	       except KeyError:
		   nots = ""
	       if(nots=="Not"):
	          temp = "(not " + temp + ")"
	       temp = "(assert " + temp + ")\n" 
	       dataisauthorized_insert += temp

	   if elt_type == "Reads-At-Node":
	       try:
		   nots = s["Not"]
	       except KeyError:
		   nots = ""
               tbegin = s["before_time"]
	       tend = s["after_time"]
	       user = s["user_name"]
	       data = s["data_name"]
	       node = s["node_name"]
	       temp = "'(reads-at-node " + user + " " + data + " " + node + " (make-interval " + tbegin + " " +     tend + "))"
	       if(nots=="Not"):
	          temp = "(not " + temp + ")"
	       temp = "(assert " + temp + ")\n" 
	       readsatnode_insert += temp

	   if elt_type == "Data-At-Node":
	       try:
		   nots = s["Not"]
	       except KeyError:
		   nots = ""
               tbegin = s["before_time"]
	       tend = s["after_time"]
	       data = s["data_name"]
	       node = s["node_name"]
	       temp = "'(data-at-node " + data + " " + node + " (make-interval " + tbegin + " " +     tend + "))"
	       if(nots=="Not"):
	          temp = "(not " + temp + ")"
	       temp = "(assert " + temp + ")\n" 
	       dataatnode_insert += temp

    return time_insert,data_insert,user_insert,dataisauthorized_insert,readsatnode_insert,dataatnode_insert,before_insert


def insert_text(node_insert,time_insert,data_insert,user_insert,link_insert,dataisauthorized_insert,readsatnode_insert,dataatnode_insert,before_insert,outfilename):
    constant_type = ["node", "data", "user"]
    type_insert=""
    for x in constant_type:
        type_insert+="(declare-sort '" + x + ")\n"
    
    #outfilename = "result.lisp"
    with open(outfilename, 'w') as outfile:
        with open("toinsert.lisp", 'r') as readfile:
	    insertstring = readfile.readlines()
	    for x in insertstring:
                if(x == ";;; INSERT TYPES HERE ;;;\n"):
		    outfile.write(x)
 		    outfile.write(type_insert)
	        elif(x == ";;; INSERT NODES HERE ;;;\n"):
		    outfile.write(x)
		    outfile.write(node_insert)
	        elif(x == ";;; INSERT TIME POINTS HERE ;;;\n"):
		    outfile.write(x)
		    outfile.write(time_insert)
    	        elif(x == ";;; INSERT DATA HERE ;;;\n"):
		    outfile.write(x)
    		    outfile.write(data_insert)
    	        elif(x == ";;; INSERT USER HERE ;;;\n"):
		    outfile.write(x)
    		    outfile.write(user_insert)
    	        elif(x == ";;; INSERT SETLINK HERE ;;;\n"):
		    outfile.write(x)
    		    outfile.write(link_insert)
     	        elif(x == ";;; INSERT DATA-ISAUTHORIZED HERE ;;;\n"):
		    outfile.write(x)
    		    outfile.write(dataisauthorized_insert)
       	        elif(x == ";;; INSERT READS AT NODE HERE ;;;\n"):
		    outfile.write(x)
    		    outfile.write(readsatnode_insert)
       	        elif(x == ";;; INSERT DATA AT NODE HERE ;;;\n"):
		    outfile.write(x)
    		    outfile.write(dataatnode_insert)
    	        elif(x == ";;; INSERT BEFORE HERE ;;;\n"):
		    outfile.write(x)
    		    outfile.write(before_insert)
    	        else:
    		    outfile.write(x)
    
    #subprocess.call(["cp","result.lisp","/home/fabien/snark-20180808r022/result.lisp"])

    #print link_insert + node_insert + time_insert + before_insert + dataisauthorized_insert + readsatnode_insert

    #print list_node + list_link

    #move_migration_algo()    

try:
        opts, args = getopt.getopt(sys.argv[1:], "c:o:a:", ["conffile=", "outfile=", "algorithm="])
except getopt.GetoptError as err:
        # print help information and exit:
        print str(err)  # will print something like "option -a not recognized"
        sys.exit(2)

for opt, arg in opts:
    if opt in ('-c' , '--conffile'):
	conffile = arg
    if opt in ('-o' , '--outfile'):
	outfile = arg
    if opt in ('-a' , '--algorithm'):
	algo = arg
if (len(sys.argv)!=7):
    #print str(sys.argv) + " length: " + str(len(sys.argv))
    print "Wrong number of argument"
    print "Usage: python TopoParser.py -c <configuration file> -o <output file> -a <algorithm>"
    print "Algorithms: n = none, m = move, i = iteratice"
    exit()



time_insert,data_insert,user_insert,dataisauthorized_insert,readsatnode_insert,dataatnode_insert,before_insert = parse(conffile)

## Parsubg algorithm argument

if (algo == 'n'):
    nodes = []
    links = []
    times =['time-0','time-1']
if (algo == 'm'):
    nodes,links,times =  move_migration_algo()
if (algo == 'i'):
    nodes,links,times =  iterative_migration_algo()

node_insert=""
link_insert=""
before_insert=""
time_insert=""
nodes = list_node + nodes
links = list_link + links

for n in nodes:
    node_insert += "(declare-constant '" + n + " :sort 'node)\n"
for l in links:
    link_insert += "(assert (setlink0 " + l[0] + " " + l[1] + " (make-interval " + l[2] + " " + l[3] + ")) :name " + l[0] + "-linked-to-" + l[1] + "-during-"+ l[2] + "-" + l[3]  + ")\n" 
for t in times:
    time_insert += "(declare-constant '" + t + " :sort 'time-point :constructor t)\n"

my_iterator=0
while(my_iterator<len(times)-1):
     before_insert+="(before " + str(times[my_iterator]) + " " + str(times[my_iterator+1]) + ")\n" 
     my_iterator+=1

insert_text(node_insert,time_insert,data_insert,user_insert,link_insert,dataisauthorized_insert,readsatnode_insert,dataatnode_insert,before_insert,outfile)
