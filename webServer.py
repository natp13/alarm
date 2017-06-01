#!/usr/bin/python

from wsgiref.simple_server import make_server, demo_app
from paste.request import parse_formvars
import socket
import sitev2

remotePage = """
<!DOCTYPE html> 
<html> 
<head> 
    <title>Nat's Alarm Clock</title> 
    <meta name="viewport" content="width=device-width, initial-scale=1"> 
    <link rel="stylesheet" href="http://code.jquery.com/mobile/1.2.1/jquery.mobile-1.2.1.min.css" />
    <script src="http://code.jquery.com/jquery-1.8.3.min.js"></script>
    <script src="http://code.jquery.com/mobile/1.2.1/jquery.mobile-1.2.1.min.js"></script>
    <script type="text/javascript">
        jQuery.support.cors = true;
        var serverUrl = "http://192.168.1.105:8000";
        
        function pausePlayClick() {
            //$.ajax({url: "/api/getWeather", data: { zipcode: 97201}});
            //$.ajax("http://192.168.1.116:8000/control?action=pause_play");
            $.ajax({
                type: "GET",
                //url: "http://192.168.1.116:8000/control",
                url: serverUrl + "/control",
                data: { action: "pause_play" },
                cache: false,
                crossDomain: true, // this line doesn't actually do anything? need the jQuery.support.cors
                dataType: "text",
                success: function(x) { alert(x); },
                error: function(x) { alert(x.responseText); }
            });
        }
        
        function setVolume(level)
        {
            $.ajax({
                type: "GET",
                // url: "http://192.168.1.116:8000/control",
                url: serverUrl + "/control",
                data: { action: "volume "+level.toString()+"%" },
                cache: false,
                crossDomain: true, // this line doesn't actually do anything? need the jQuery.support.cors
                dataType: "text",
                success: function(x) { alert(x); },
                error: function(x) { alert(x.responseText); }
            });
        }
        
        function getStations()
        {
            $.ajax({
                type: "GET",
                //url: "http://192.168.1.116:8000/control",
                url: serverUrl + "/control",
                data: { action: "stations" },
                cache: false,
                crossDomain: true, // this line doesn't actually do anything? need the jQuery.support.cors
                dataType: "text json",
                success: function(x) {
                    var stationsList = $("#stationsList");
                    stationsList.empty();
                    // loop through our values and add them to the list
                    for (value in x) {
                        stationsList.append("<li><a href=\\\"#\\\">"+value+":  "+x[value]+"</a></li>");        
                    }
                    stationsList.listview( "refresh" );
                },
                error: function(x,error) { alert(x.responseText); }
            });
        }
        
        function getStationHistory()
        {
            $.ajax({
                type: "GET",
                //url: "http://192.168.1.116:8000/control",
                url: serverUrl + "/control",
                data: { action: "station_history" },
                cache: false,
                crossDomain: true, // this line doesn't actually do anything? need the jQuery.support.cors
                dataType: "text json",
                success: function(x) {
                    var stationsList = $("#stationHistoryList");
                    stationsList.empty();
                    // loop through our values and add them to the list
                    for (value in x) {
                        stationsList.append("<li>"+value+") "+x[value][0]+":  "+x[value][1]+"</li>");        
                    }
                    stationsList.listview( "refresh" );
                },
                error: function(x,error) { alert(x.responseText); }
            });
        }
        
        function runCommand()
        {
            $.ajax({
                type: "GET",
                //url: "http://192.168.1.116:8000/control",
                url: serverUrl + "/control",
                data: { action: $("#commandBox-0").attr("value") },
                cache: false,
                crossDomain: true, // this line doesn't actually do anything? need the jQuery.support.cors
                dataType: "text",
                success: function(x) { alert(x); },
                error: function(x) { alert(x.responseText); }
            });
        }
    </script>
</head> 

<body>
<div data-role="page">

    <div data-role="header">
        <h1>Nat's Alarm Clock</h1>
    </div><!-- /header -->
    
    <div data-role="content">    
        <p>Yolo</p>        
    </div><!-- /content -->
    
    <a href="#" onClick="pausePlayClick()" data-role="button" data-theme="a">Pause/Play</a>
    
    <form id="volumeSlider">
        <label for="slider-0">Volume:</label>
        <input type="range" name="slider" id="slider-0" value="80" min="50" max="100"  />
    </form>

    <p></p>
    <form id="commandBox">
        <label for="commandBox-0">Enter command:</label>
        <input type="text" name="name" id="commandBox-0" value=""  />
    </form>
    <a href="#" onClick="runCommand()" data-role="button" data-theme="a">Run command</a>
    
    <script type="text/javascript">
        $("#volumeSlider").on( "slidestop", 
            function( event, ui ) {
                //alert($('#slider-0').attr('value'));
                setVolume($("#slider-0").attr("value"));
            });
        $("#volumeSlider").on( "slidecreate",
            function( event, ui ) {
                $.ajax({
                    type: "GET",
                    //url: "http://192.168.1.116:8000/control",
                    url: serverUrl + "/control",
                    data: { action: "get_volume"},
                    cache: false,
                    crossDomain: true, // this line doesn't actually do anything? need the jQuery.support.cors
                    dataType: "text",
                    success: function(x) { $("#slider-0").val(x).slider("refresh"); },
                    error: function(x) { alert(x.responseText); }
                });
                
            });
    </script>
    
    <div id="stationsHistory" data-role="collapsible">
        <h3>Station history</h3>
        <ul data-role="listview" id="stationHistoryList">
            <li>Items should go here</li>
        </ul>
    </div>
    
    <div id="stationsCollapsible" data-role="collapsible">
        <h3>List of stations</h3>
        <ul data-role="listview" id="stationsList">
            <li>Items should go here</li>
        </ul>
    </div>
    
    <script type="text/javascript">
        $("#stationsCollapsible").on("expand",
            function( event, ui ) {
                getStations();
            });
            
        $("#stationsHistory").on("expand",
            function (event,ui) {
                getStationHistory();
            });
    </script>

</div><!-- /page -->

</body>
</html>
"""

class ObjectPublisher(object):
    def __init__(self, root):
        self.root = root

    def __call__(self, environ, start_response):
        fields = parse_formvars(environ)
        obj = self.find_object(self.root, environ)
        response_body = obj(**fields.mixed())
        start_response("200 OK", [("content-type", "text/html")])
        return [response_body]

    def find_object(self, obj, environ):
        path_info = environ.get("PATH_INFO", "")
        if not path_info or path_info == "/":
            # We've arrived!
            return obj
            
        # PATH_INFO always starts with a /, so we'll get rid of it:
        path_info = path_info.lstrip("/")
        
        # Then split the path into the "next" chunk, and everything
        # after it ("rest"):
        parts = path_info.split("/", 1)
        next = parts[0]
        if len(parts) == 1:
            rest = ""
        else:
            rest = "/" + parts[1]
        # Hide private methods/attributes:
        assert not next.startswith("_")
        # Now we get the attribute; getattr(a, "b") is equivalent
        # to a.b...
        next_obj = getattr(obj, next)
        
        # Now fix up SCRIPT_NAME and PATH_INFO...
        environ["SCRIPT_NAME"] += "/" + next
        environ["PATH_INFO"] = rest
        
        # and now parse the remaining part of the URL...
        return self.find_object(next_obj, environ)


# def app(environ, start_response):
    # start_response("200 OK", [("Content-type", "text/html")])
    # return ["""
        # <html>
         # <head><title>Hello World!</title></head>
         # <body>
          # <h1>You"ve reached Nat's Raspberry Pi Alarm Clock</h1>
          # If you can't get in, then stay out.
         # </body>
        # </html>"""]
    #return ['<http><h1>Hello world!</h1></http>']
    
class Welcome(object):
    def __call__(self, name):
        return "Hello %s!" % name
        
    def nat(self, name):
        return "Nats page: %s!" % name
    
class Root(object):
    def __init__(self):
        self.welcome = Welcome()

    # The "index" method:
    def __call__(self):
        return '''
        <form action="control">
        Name: <input type="text" name="action">
        <input type="submit">
        </form>
        '''
        
    def remote(self, **kargs):
        return remotePage
        
    def remote2(self, **kargs):
        return sitev2.siteV2
        
    def control(self, action, **kargs):
        # TODO: do this async
        # or not. I think the javascript control should get the
        # response when the action is done, so that it can know what the result was
        # Yeah!
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("localhost", 8888))
        s.sendall(action + "\n")
        response = s.recv(1024)
        while response[-1] != "\n":
            response += s.recv(1024)
        s.close()
        #return "<h2>Done.</h2>" + action + "<p>" + response + "</p>" + "<p>" + repr(kargs) + "</p>"
        return response
        
app = ObjectPublisher(Root())

if __name__ == "__main__":
    # from paste import httpserver
    # httpserver.serve(app, port="8000")

    httpd = make_server("", 8000, app)
    print "Serving HTTP on port 8000..."
    # Respond to requests until process is killed
    httpd.serve_forever()
