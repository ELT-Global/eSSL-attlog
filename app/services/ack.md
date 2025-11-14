13 Command Reply  
After Getting Command Issued by the Server, the client needs to reply corresponding command.  
A request message from the client:  
POST /iclock/devicecmd?SN=${SerialNumber} 
Host: ${ServerIP}: ${ServerPort} 
 Content-Length: ${XXX} 
…… 
 
${CmdRecord} 
 
Annotation:   
HTTP request method: GET method   
URI: /iclock/devicecmd   
HTTP protocol version: 1.1  
Client configuration information:       
SN: ${Required} Serial number of the client      
Host head field: ${Required}  
Content-Length header field: ${Required}  
Other header fields: ${Optional}  
Response entity: ${CmdRecord}, record of replied commands. The reply content all contains the ID\Retur
 n\CMD information, with the following meanings: 
ID: Number of the command issued by the client     
Return: Returned result after the client executes the command       
CMD: Description of the command issued by the server    
A small number of replies contain other information. For specific reply content format, see the descriptio
 n of each command.   
${LF} is used to connect multiple command reply records.  
 
A normal response message from the server: 
HTTP/1.1 200 OK 
Date: ${XXX} 
Content-Length: 2 
…… 
 
OK 
 
Annotation:   
HTTP status line: Defined with standard HTTP protocol   
HTTP response header field:       
Date header field: ${Required} This header field is used for synchronization with the server time, in GMT f
 ormat. For example, Date: Fri, 03 Jul 2015 06: 53: 01 GMT      
PUSH SDK                                                                                                                                                     Attendance PUSH Communication Protocol 
Page | 102  Copyright©2020 ZKTECO CO., LTD.  All rights reserved. 
Content-Length header field: Based on HTTP 1.1, this header field is usually used to specify the data leng
 th of the response entity. If the response entity size is uncertain, head fields of Transfer-Encoding: chunk
 ed, Content-Length and Transfer-Encoding are supported, all of which are standard definitions of HTTP a
 nd are not described in details here.  
 
Example:  
A request from the client:   
POST /iclock/devicecmd?SN=0316144680030 HTTP/1.1 
Host: 58.250.50.81: 8011 
User-Agent: iClock Proxy/1.09 
Connection: close 
Accept: */* 
Content-Length: 143 
 
ID=info8487&Return=0&CMD=DATA 
ID=info8488&Return=0&CMD=DATA 
ID=info8489&Return=0&CMD=DATA 
ID=info7464&Return=0&CMD=DATA 
ID=fp7464&Return=0&CMD=DATA 
 
A response from the server:   
HTTP/1.1 200 OK 
Server: nginx/1.6.0 
Date: Tue, 30 Jun 2015 01: 24: 48 GMT 
Content-Type: text/plain 
Content-Length: 2 
Connection: close 
Pragma: no-cache 
Cache-Control: no-store 
 
OK 