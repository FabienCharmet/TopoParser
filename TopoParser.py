# -*- coding: iso-8859-1 -*-
from pyparsing import *
from shutil import copyfile
import subprocess

keyword = ['Node','Link']
varname = alphanums + '-_'

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
Reads = Word('(', max=1) + Optional(Word('Not')("Not")) + Word('Reads')("type") + Word(varname)("user_name") + Word(',', max=1) + Word(varname)("data_name") + Word(',', max=1) + Word(varname)("before_time") + Word(',', max=1) + Word(varname)("after_time")  +  Word(')',max=1)

Element = Node | Link | Time | Before | Data | User | DataIsAuthorized | Reads

#print Node.parseString(anode)

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


def parse(filename):
    replace_char('\n','',filename)
    replace_char(')',')\n',filename)
    node_insert=""
    data_insert=""
    user_insert=""
    link_insert=""
    time_insert=""
    before_insert=""
    type_insert=""
    reads_insert=""
    dataisauthorized_insert=""
    reads_insert=""

    with open(filename) as f:
        for line in f:
           s = Element.parseString(line)
	   elt_type = s["type"]
	   if elt_type == "Node":
	       name = s["node_name"]
	       node_insert += "(declare-constant '" + name + " :sort 'node)\n"
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
	       link_insert += "(assert (setlink0 " + nbegin + " " + nend + " (make-interval " + tbegin + " " + tend + ")) :name " + nbegin + "-linked-to-" + nend + "-during-"+ tbegin + "-" + tend + ")\n" 
	   if elt_type == "Time":
      	       name = s["time_name"]
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
	   if elt_type == "Reads":
	       try:
		   nots = s["Not"]
	       except KeyError:
		   nots = ""
               tbegin = s["before_time"]
	       tend = s["after_time"]
	       name = s["user_name"]
	       data = s["data_name"]
	       temp = "'(reads " + name + " " + data + " (make-interval " + tbegin + " " +     tend + "))"
	       if(nots=="Not"):
	          temp = "(not " + temp + ")"
	       temp = "(assert " + temp + ")\n" 
	       reads_insert += temp
           #print line
#    with open(fname) as f:
#        content = f.readlines()
        # you may also want to remove whitespace characters like `\n` at the end of each line
 #       content = [x.strip() for x in content] 

    #declaration_str=";;;;;;;;;;;;;;;;;;;;;;;;;;;;;\n;;;     DECLARATIONS      ;;;\n;;;;;;;;;;;;;;;;;;;;;;;;;;;;;\n"
    constant_type = ["node", "data", "users"]
    for x in constant_type:
        type_insert+="(declare sort '" + x + ")\n"
    #declaration_str += "(declare-snark-option time-point-sort-name 'time-point 'time-point)\n"
    #declaration_str += "(declare-time-relations :intervals t :points t :dates t)\n\n"
    #declaration_str += "(declare-function '$$cons 2 :new-name 'cons)"
    #declaration_str += "(declare-function '$$list :any  :new-name 'list)\n"
    #declaration_str += "(declare-constant '$$nil :alias 'nil :sort 'list)\n"
    
    outfilename = "result.lisp"
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
       	        elif(x == ";;; INSERT READS HERE ;;;\n"):
		    outfile.write(x)
    		    outfile.write(reads_insert)
    	        elif(x == ";;; INSERT BEFORE HERE ;;;\n"):
		    outfile.write(x)
    		    outfile.write(before_insert)
    	        else:
    		    outfile.write(x)
    
    subprocess.call(["cp","result.lisp","/home/fabien/snark-20180808r022/result.lisp"])

    print link_insert + node_insert + time_insert + before_insert + dataisauthorized_insert + reads_insert



parse("topo.conf")
