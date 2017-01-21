#  coding: utf-8
import SocketServer

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(SocketServer.BaseRequestHandler):

    def handle(self):
        self.data = self.request.recv(1024).strip()
        print ("Got a request of: %s\n" % self.data)
        #self.request.sendall("OK")

        #self.dbgPrt("type(self.data)",repr(type(self.data)))

        splitedData = self.splitReqstComponent(self.data)
        #self.dbgPrt("splited data",repr(splitedData))

        # variables of request and checker
        action = splitedData[0]
        action_is_valid = False
        path = 'www' + splitedData[1]
        path_is_valid = False
        protocal = splitedData[2]

        # varify action
        action_is_valid, response = self.actVarify(action)

        # varify the path
        if action_is_valid:
            path_is_valid, response = self.pathVarify(path)

        # response
        if path_is_valid:
            response = self.pullFileContent(path)

        self.request.sendall(response)
        #print ("Sent a response of: %s\n" % response)

    def actVarify(self, action):
        if (action == 'GET'):
            actChecker = True
            response = None
        else:
            actChecker = False
            response = self.genRspd('405 Method not allow',\
                                    'Content-Type: text/html',\
                                    '<p>405 Method not allow<p>')
        return actChecker, response

    def pathVarify(self, path):
        pathCheckingList = []
        pathList = path.split('/')

        for direction in pathList:
            if (direction == '..') and len(pathCheckingList)!=0:
                pathCheckingList.pop()
            elif (direction == '.'):
                pass
            elif (direction == '..') and len(pathCheckingList)==0:
                pathChecker = False
                response = self.genRspd('404 Page not found',\
                                        'Content-Type: text/html',\
                                        '<p>404 Page not found<p>')
                return pathChecker, response
            else:
                pathCheckingList.append(direction)

        pathChecker = True
        response = None

        return pathChecker, response

    def pullFileContent(self,path):
        fileType = 'Content-Type: text/'

        # the direction
        if (path[-1]=='/'):
            path = path  + 'index.html'

        # figure out the file type
        fileTypeChecker = path.split('.')
        fileTypeChecker = fileTypeChecker[-1]
        if (fileTypeChecker == 'html'):
            fileType = fileType + 'html\r\n\r\n'
        elif (fileTypeChecker == 'css'):
            fileType = fileType + 'css\r\n\r\n'
        else:
            fileType = fileType + 'html\r\n\r\n'

        # get the content from file
        try:
            File = open(path, 'r')
            contents = File.read()
            File.close()
        except IOError:
            #self.handle404()
            statuCode = '404 Page not found'
            contents = '<p>404 Page not found<p>'
        else:
            statuCode = '200 OK'

        # create HTTP
        response = self.genRspd(statuCode, fileType, contents)
        return response

    def genRspd(self, statuCode, fileType, contents):
        # create HTTP
        response = 'HTTP/1.1 ' + statuCode + '\r\n' + \
                   'Content-Length:' + str(len(contents)) + '\r\n' + \
                   fileType + contents
        return response

    def handle404():
        return code

    def splitReqstComponent(self, requestLine):
        result = requestLine.split("\r\n")
        result = result[0].split()
        return result

    def dbgPrt(self, markerStr, contentStr):
        print ("%s: %s\n" % (markerStr, contentStr))

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    SocketServer.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = SocketServer.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
