#  coding: utf-8
import SocketServer, errno

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# Copyright 2016 Chenrui Lei
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
    root_path = './www'
    host_name = 'http://127.0.0.1:8080'

    def handle(self):
        self.data = self.request.recv(1024).strip()
        print ("Got a request of: %s\n" % self.data)

        # decoding HTTP request
        splitedData = self.splitReqstComponent(self.data)
        if len(splitedData) < 3:
            return
        #print(splitedData)

        # variables of request and checker
        action = splitedData[0]
        action_is_valid = False
        path = splitedData[1]
        path_is_valid = False
        protocal = splitedData[2]

        # varify action
        action_is_valid, response = self.actVarify(action)

        # varify the path
        if action_is_valid:
            path_is_valid, response = self.pathVarify(path)

        # pull contents
        if path_is_valid:
            response = self.pullFileContent(path)

        # response
        self.request.sendall(response)
        #print ("Sent a response of: %s\n" % response)

    def actVarify(self, action):
        if (action == 'GET'):
            actChecker = True
            response = None

        # Invalid method found
        else:
            actChecker = False
            response = self.genHTTPErrorRspd(405,'')

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

            # Invalid path found
            elif (direction == '..') and len(pathCheckingList)==0:
                pathChecker = False
                response = self.genHTTPErrorRspd(404,'')
                return pathChecker, response

            else:
                pathCheckingList.append(direction)

        pathChecker = True
        response = None

        return pathChecker, response

    def pullFileContent(self,path):

        # if serve from a direction
        if (path[-1]=='/'):
            path = path  + 'index.html'

        # get the content from file
        try:
            File = open(self.root_path + path, 'r')
            contents = File.read()
            File.close()

        except IOError, e:

            # 404 not found
            if (e.errno == errno.ENOENT):
                response = self.genHTTPErrorRspd(404,'')

            # 302 redirection
            elif (e.errno == errno.EISDIR):
                extraHeader = 'Location: ' + self.host_name + path + '/'
                response = self.genHTTPErrorRspd(302,extraHeader)

            else:
                raise

        else:

            # 200 OK
            HTTPStatus = '200 OK'
            mimeType = self.findMimeType(self.root_path + path) # figure out the mime type
            response = self.genRspd(HTTPStatus, mimeType, contents, '')

        return response

    def findMimeType(self, fullPath):

        # variable
        mimeType = 'text/'

        # pre-processing
        mimeTypeChecker = fullPath.split('.')
        mimeTypeChecker = mimeTypeChecker[-1]

        # processing
        if (len(mimeTypeChecker)>1):
            if (mimeTypeChecker == 'html'):
                mimeType = mimeType + 'html'
            elif (mimeTypeChecker == 'css'):
                mimeType = mimeType + 'css'
            else:
                mimeType = mimeType + 'plain'
        else:
            mimeType = mimeType + 'plain'

        return mimeType

    def genRspd(self, HTTPStatus, mimeType, contents, extraHeader):
        response = 'HTTP/1.1 ' + HTTPStatus + '\r\n' + \
                   'Content-Length:' + str(len(contents)) + '\r\n' + \
                   'Content-Type: ' + mimeType + '\r\n' + \
                   extraHeader + '\r\n\r\n' \
                   + contents
        return response

    def genHTTPErrorRspd(self, statusCode, extraHeader):
        if statusCode==302:
            HTTPStatus = '302 Found'
            contents = '<p>302 Found<p>\n'
        elif statusCode==404:
            HTTPStatus = '404 Page not found'
            contents = '<p>404 Page not found<p>\n'
        elif statusCode==405:
            HTTPStatus = '405 Method not allow'
            contents = '<p>405 Method not allow<p>\n'

        return self.genRspd(HTTPStatus, 'text/html', contents, extraHeader)

    def splitReqstComponent(self, requestLine):
        result = requestLine.split("\r\n")
        result = result[0].split()
        return result


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    SocketServer.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = SocketServer.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
