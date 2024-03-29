#!/usr/bin/env python

from flask import Flask, redirect, url_for, request, send_file
import sys
import os
import hashlib
import socket
import urllib

UPLOAD_FOLDER = 'static'

app = Flask(__name__)
def checkResponse( back ):
	if back.startswith('OK') :
		tokens = back.split(' ')
	 	f = urllib.urlopen(tokens[2])	
	 	return send_file(f)
	else:
		return "404 URL Not Found"
		
@app.route('/')
def index():
	return redirect(url_for('static', filename='index.html'))

@app.route('/rd/<int:p>', methods=["GET"])
def rd_getrd(p):
	#1. Figure out the <object-name> from the request
	#2. Connect to the routing daemon on port p
	#3. Do GETRD <object-name> 
	#4. Parse the response from the routing daemon
	#4 a) If response is OK <URL>, the open the URL
	#4 b) If response is 404, then show that content is not available
    #### You may factor out things from here and rd_getrd() function and form a separate sub-routine
	
	obj =  request.args['object']
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect(('localhost', p))
	re = 'GETRD '+str(len(obj))+' '+str(obj)
	#print 'Connecting to localhost @ port '+ str(p)
	s.sendall(re)
	back = s.recv(4096)
	print 'Response from routing daemon: \n'+str(back)
	s.close()
 	return checkResponse(back)

@app.route('/rd/addfile/<int:p>', methods=["POST"])
def rd_addfile(p):
	#1. Figure out the object-name and the file details/content from the request
	#2. Find the sha256sum of the file content
	#3. Save the file in the static directory under the sha256sum name and compute the relative path
	#4. Connect to the routing daemon on port p
	#5. Do ADDFILE <object-name> <relative-path> 
	#6. Based on the response from the routing daemon display whether the object has been successfully uploaded/added or not 
	
	obj =  request.form['object']
	f = request.files['uploadFile']
	#print f.stream.read()
	
	m = hashlib.sha256()
	m.update( f.stream.read() )
	hashName = m.hexdigest()
	f.seek(0)	
	f.save(os.path.join(UPLOAD_FOLDER, hashName))
	f.close()
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
 	s.connect(('localhost', p))
	re = 'ADDFILE '+str(len(obj))+' '+str(obj)+' '+str(len(os.path.join(UPLOAD_FOLDER, hashName)))+' '+str(os.path.join(UPLOAD_FOLDER, hashName))
	
	print 'request: '+str(re)
	
	s.sendall(re)
	back = s.recv(4096)
	
	print 'response: '+ back
	
	if back.startswith('OK'):
		return 'File has been successfully uploaded'
	else:
		return 'File upload failed'

@app.route('/rd/<int:p>/<obj>', methods=["GET"])
def rd_getrdpeer(p, obj):
    #1. Connect to the routing daemon on port p
    #2. Do GETRD <object-name> 
    #3. Parse the response from the routing daemon
    #3 a) If response is OK <URL>, the open the URL
    #3 b) If response is 404, then show that content is  not available
    #### You may factor out things from here and rd_getrd() function and form a separate sub-routine
	
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
 	s.connect(('localhost', p))
	re = 'GETRD '+str(len(obj))+' '+str(obj)
	s.sendall(re)
	back = s.recv(4096)
	s.close()
	return checkResponse(back)

if __name__ == '__main__':
	if (len(sys.argv) > 1):
		servport = int(sys.argv[1])
		app.run(host='0.0.0.0', port=servport, threaded=True, processes=1)
	else:	
		print "Usage ./webserver <server-port> \n"
