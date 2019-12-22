// set up ======================================================================
var express  = require('express');
var app      = express(); 										// 
var port  	 = process.env.PORT || 3000; 				// set the port
var sqlite3 = require('sqlite3').verbose();
var db = new sqlite3.Database('sophos.db');

//.................................................................................

var PythonShell = require('python-shell');
PythonShell.run('MasterScanDB.py', function(err,results) {
         console.log("DB Created && ========>>>>>>  ALL DONE");
 });

//.................................. PYTHON DB Above ...........................................

app.use(express.static(__dirname + '/public')); 				// set the static files location /public/img will be /img for users

var connectivityData = function(req, res){
  db.all("SELECT * FROM mstrScan where State='Connected'", [], (err, rows) => {
    if (err) {
      throw err;
    }
    res.send(rows);
  });

};


  
var radioScanningData = function(req, res){
  db.all("SELECT Signal, Channel FROM mstrScan where State!='Connected'", [], (err, rows) => {
    if (err) {
      throw err;
    }
    res.send(rows);
  });

};

app.get('/currentscan',connectivityData);
app.get('/radioscan', radioScanningData);

app.listen(port);
console.log("App listening on port " + port);


// function rescan() {

// PythonShell.run('hello.py', function(err,results) {

//         console.log("DB Created && ========>>>>>>  ALL DONE");
// });
// };
