#  coding: utf-8
import SocketServer, errno

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
        if len(splitedData) < 3:
            return
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
                                    'text/html',\
                                    '<p>405 Method not allow<p>', \
                                    '')
        return actChecker, response

    def pathVarify(self, path):
        pathCheckingList = []
        pathList = path.strip('/')
        pathList = pathList.split('/')

        for direction in pathList:
            if (direction == '..') and len(pathCheckingList)!=0:
                pathCheckingList.pop()
            elif (direction == '.'):
                pass
            elif (direction == '..') and len(pathCheckingList)==0:
                pathChecker = False
                response = self.genRspd('404 Page not found',\
                                        'text/html',\
                                        '<p>404 Page not found<p>', \
                                        '')
                return pathChecker, response
            else:
                pathCheckingList.append(direction)

        pathChecker = True
        response = None

        return pathChecker, response

    def pullFileContent(self,path):
        mimeType = 'text/'
        extraHeader = ''

        # the direction
        if (path[-1]=='/'):
            path = path  + 'index.html'

        # figure out the mime type
        mimeTypeChecker = path.split('.')
        mimeTypeChecker = mimeTypeChecker[-1]
        if (mimeTypeChecker == 'html'):
            mimeType = mimeType + 'html'
        elif (mimeTypeChecker == 'css'):
            mimeType = mimeType + 'css'
        else:
            mimeType = mimeType + 'html'

        # get the content from file
        try:
            File = open(path, 'r')
            contents = File.read()
            File.close()
        except IOError, e:

            # 404 not found
            if (e.errno == errno.ENOENT):
                HTTPStatus = '404 Page not found'
                contents = '<p>404 Page not found<p>'

            # 302 redirection
            elif (e.errno == errno.EISDIR):
                HTTPStatus = '302 Found'
                extraHeader = 'Location: http://127.0.0.1:8080' + path[3:] + '/'
                contents = '<p>302 Found<p>'

            else:
                raise
        else:
            HTTPStatus = '200 OK'

        # create HTTP
        response = self.genRspd(HTTPStatus, mimeType, contents, extraHeader)
        return response

    def genRspd(self, HTTPStatus, mimeType, contents, extraHeader):
        response = 'HTTP/1.1 ' + HTTPStatus + '\r\n' + \
                   'Content-Length:' + str(len(contents)) + '\r\n' + \
                   'Content-Type: ' + mimeType + '\r\n' + \
                   extraHeader + '\r\n\r\n' \
                   + contents
        return response

    def genHTTPErrorRspd(self, statusCode, extraHeader):
        if statusCode==302:
            pass
        elif statusCode==404:
            pass
        elif statusCode==405:
            pass
        else:
            pass

        return response

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
