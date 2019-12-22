
var app = angular.module('myApp', []);

app.controller("myCtrl", function($scope, $http) {
	
	//get data from server and store it in $scope.response
	$scope.getData = function(){

        $scope.status = {
            properties : [
               {
                    name: 'Application',
                    status: 'true',
                    detail: 'Synchronization',
                    message: 'Running',
                    suggestion: ''
                },
                {
                    name: 'L3 Connectivity',
                    status: 'false',
                    detail: 'DHCP= 1 DNS=1 Gateway=1 APInternet=1 RadiusServer=1 Cloud=1 Latency<30ms Jitter<5ms',
                    message: 'DHCP missing',
                    suggestion: 'Verify DHCP Connectivity'
                },
                {
                    name: 'L2 Connectivity',
                    status: 'warning',
                    detail: 'Valid SSID & BSSID 600mbps< Rx >700mbps 350mbps< Tx >450mbps',                   
                    message: 'Some packet drop',
                    suggestion: 'Unhide SSID'
                },
                {
                    name: 'Radio',
                    status: 'warning',
                    detail: '-65< RSSI >-50 Frequency~2.4/5.0GHz ChannelWidth~20/40/80MHz',
                    message: 'Low SNR value',
                    suggestion: 'Move towards AP'
                },
                {
                    name: 'Authentication',
                    status: 'false',
                    detail: 'Valid Credential',
                    message: 'wrong authentication type',
                    suggestion: 'Upgrade to higher encryption standard'
                },
                {
                    name: 'Association',
                    status: 'true',
                    detail: 'WPA/WPA2 TKIP/AES',
                    message: 'working fine',
                    suggestion: 'Update certificate'
                },
            ]
        };
        

        var successCallback = function(connectionData) {

            $scope.response = connectionData.data; //it store all the records from db in json format
            console.log($scope.response);
            $scope.response1 = $scope.response[0]; // store the response rocord to pass into the condition

        };

        var successCallback1 = function(connectionData1) {
            
            $scope.response2 = connectionData1.data; //it store all the records from db in json format
            console.log($scope.response2);
            $scope.response3 = $scope.response2; // store the response rocord to pass into the condition
            console.log($scope.response1);
        
            //////////////////////////////////////////meter gauge
            for (let i = 0; i < $scope.response3.length; i++) {

              $scope.response4 = $scope.response3[i];
              var meterRating =function () {
                if ($scope.response1.Signal >= -60 && $scope.response1.Signal <= -50 && $scope.response1.Channel !== $scope.response4.Channel) {
                   
                    $scope.level = 10;

                } else if ($scope.response1.Signal >= -60 && $scope.response1.Signal <= -50 && $scope.response1.Channel == $scope.response4.Channel) {
                   
                    $scope.level = 8;

                }
                
                else if ($scope.response1.Signal >= -65 && $scope.response1.Signal <= -61) {
                  
                  $scope.level = 8;

                } else if ($scope.response1.Signal >= -70 && $scope.response1.Signal <= -66) {
                 
                  $scope.level = 7;

                } else if ($scope.response1.Signal >= -75 && $scope.response1.Signal <= -71) {
                  
                  $scope.level = 4;

                } else if ($scope.response1.Signal >= -80 && $scope.response1.Signal <= -76) {
                   
                    $scope.level = 2;

                } else{
                   
                    $scope.level = 1;

                }
              };
             };
              meterRating();
             
            // Trig to calc meter point
            var degrees = 10 - $scope.level,
                radius = .5;
            var radians = degrees * Math.PI / 10;
            var x = radius * Math.cos(radians);
            var y = radius * Math.sin(radians);
            
            // Path: may have to change to create a better triangle
            var mainPath = 'M -.0 -0.025 L .0 0.025 L ',
                 pathX = String(x),
                 space = ' ',
                 pathY = String(y),
                 pathEnd = ' Z';
            var path = mainPath.concat(pathX,space,pathY,pathEnd);
            
            var data = [{ type: 'scatter',
                x: [0], y:[0],
                marker: {size: 28, color:'284099'},
                showlegend: false,
                name: 'Experience',
                text: $scope.level,
                hoverinfo: 'text+name'},
              { values: [50/6, 50/6, 50/6, 50/6, 50/6, 50/6,50],
              rotation: 90,
              textinfo: 'text',
              textposition:'inside',      
              marker: {colors:['rgba(14, 127, 0, .5)', 'rgba(110, 154, 22, .5)',
                                     'rgba(170, 202, 42, .5)', 'rgba(202, 209, 95, .5)',
                                     'rgba(255, 206, 0, .5)', 'rgba(232, 0, 0, .5)',
                                     'rgba(255, 255, 255, 0)']},
              labels: ['9-10', '7-8', '6-7', '4-5', '2-3', '0-1'],
              hoverinfo: 'label',
              hole: .5,
              type: 'pie',
              showlegend: false
            }];
            
            var layout = {
              shapes:[{
                  type: 'path',
                  path: path,
                  fillcolor: '284099',
                  line: {
                    color: '284099'
                  }
                }],
              title: '<b>User</b> <br>Experience',
              height: 450,
              width: 500,
              xaxis: {zeroline:false, showticklabels:false,
                         showgrid: false, range: [-1, 1]},
              yaxis: {zeroline:false, showticklabels:false,
                         showgrid: false, range: [-1, 1]}
            };
            
            Plotly.newPlot('myDiv', data, layout);
            
            //////////////////////////////////////////
            var l3ConnectivityCheck =function() {
            console.log($scope.response3);
    
            if ($scope.response1.DNS === '1' && $scope.response1.DHCP === '1' && $scope.response1.Gateway === '1' && $scope.response1.AP === '1'){

                $scope.status.properties[1].status = 'true';
                $scope.status.properties[1].message = 'Good connectivity';
                $scope.status.properties[1].suggestion = '';

            }else if ($scope.response1.DNS === '0' && $scope.response1.DHCP === '0' && $scope.response1.Gateway === '0' && $scope.response1.AP === '0') {
                
                $scope.status.properties[1].status = 'false';
                $scope.status.properties[1].message = 'DHCP is missing';
                $scope.status.properties[1].suggestion = 'Try to reconnect';
    
            }else if ($scope.response1.DHCP === '1' && $scope.response1.DNS === '0' && $scope.response1.Gateway === '1' && $scope.response1.AP === '1'){
        
                $scope.status.properties[1].status = 'false';
                $scope.status.properties[1].message = 'DNS is missing. No translation of IP address to domain names';
                $scope.level = 1;
                $scope.status.properties[1].suggestion = 'Try to connect after some time';
            
            }else if ($scope.response1.DHCP === '0' && $scope.response1.DNS === '1' && $scope.response1.Gateway === '1' && $scope.response1.AP === '1') {
        
                $scope.status.properties[1].status = 'false';
                $scope.status.properties[1].message = 'DHCP is missing, device can communicate only on LAN network';
                $scope.level = 1;
                $scope.status.properties[1].suggestion = 'Try to reconnect';
               
            }else if ($scope.response1.DHCP === '1' && $scope.response1.DNS === '1' && $scope.response1.Gateway === '0' && $scope.response1.AP === '1') {
        
                $scope.status.properties[1].status = 'false';
                $scope.status.properties[1].message = 'Gateway is missing, Unable to access internet';
                $scope.status.properties[1].suggestion = 'Check default Gateway Configuration';

            }else if ($scope.response1.DHCP === '1' && $scope.response1.DNS === '1' && $scope.response1.Gateway === '1' && $scope.response1.AP === '0') {
        
                $scope.status.properties[1].status = 'false';
                $scope.status.properties[1].message = 'APInternet is missing';
                $scope.status.properties[1].suggestion = 'Check APInternet Configuration';

            }else {
        
                $scope.status.properties[1].status = 'true';
                $scope.status.properties[1].message = 'Good Connectivity';
                $scope.status.properties[1].suggestion = '';

            }
    
            };
            l3ConnectivityCheck();
//l2Connectivity conditions
            var l2ConnectivityCheck =function() {
            if ($scope.response1.SSID.length >= 0 && $scope.response1.BSSID.length >= 0) {

                $scope.status.properties[2].status = 'true';
                $scope.status.properties[2].message = 'Successfully connected to AP';
                $scope.status.properties[2].suggestion = '';

            } else if ($scope.response1.SSID.length <= 0 ) {

                $scope.status.properties[2].status = 'false';
                $scope.status.properties[2].message = 'SSID missing';
                $scope.status.properties[2].suggestion = 'Connect with valid SSID';

            } else if($scope.response1.BSSID.length <= 0) {
        
                $scope.status.properties[2].status = 'false';
                $scope.status.properties[2].message = 'BSSID missing';
                $scope.status.properties[2].suggestion = 'Check valid credential';

            }
            };
            l2ConnectivityCheck();

// RadioCheck conditions
            var RadioCheck =function() {
            console.log($scope.response3);
            
            for (let i = 0; i < $scope.response3.length; i++) {
                $scope.response4 = $scope.response3[i];
            
                if ($scope.response1.Signal <= "-60" && $scope.response1.Signal >= "-50" && $scope.response1.Channel !== $scope.response4.Channel) {

                $scope.status.properties[3].status = 'true';
                $scope.status.properties[3].message = 'Strong Signal';
                $scope.status.properties[3].suggestion = '';
        
             } else if($scope.response1.Signal <= "-60" && $scope.response1.Signal >= "-50" && $scope.response1.Channel == $scope.response4.Channel){
                
                $scope.status.properties[3].status = 'warning';
                $scope.status.properties[3].message = 'Good Signal & Channels are Overlapping';
                $scope.status.properties[3].suggestion = 'Set Channel mode to Auto';

             } else if ($scope.response4.Signal <= "-70" && $scope.response4.Signal >= "-60" && $scope.response1.Channel !== $scope.response4.Channel) {
                
                 $scope.status.properties[3].status = 'warning';
                 $scope.status.properties[3].message = 'Average Signal';
                 $scope.status.properties[3].suggestion = 'Move towards AP';
             
                } else if ($scope.response4.Signal <= "-70" && $scope.response4.Signal >= "-60" && $scope.response1.Channel == $scope.response4.Channel) {
                    
                 $scope.status.properties[3].status = 'warning';
                 $scope.status.properties[3].message = 'Average Signal & Channels are overlapping';
                 $scope.status.properties[3].suggestion = 'Move towards AP & Set Channel mode to Auto';

                }
                else if ($scope.response1.Signal <= "-80" && $scope.response1.Signal >= "-70" && $scope.response1.Channel !== $scope.response4.Channel){
                   
                    $scope.status.properties[3].status = 'warning';
                    $scope.status.properties[3].message = 'Poor Signal';   
                    $scope.status.properties[3].suggestion = 'Move towards AP';
                    
                }else if ($scope.response1.Signal <= "-80" && $scope.response1.Signal >= "-70" && $scope.response1.Channel == $scope.response4.Channel){
                   
                    $scope.status.properties[3].status = 'warning';
                    $scope.status.properties[3].message = 'Poor Signal & Channels are overlapping';
                    $scope.status.properties[3].suggestion = 'Move towards AP & Set Channel mode to Auto';
                    
                }
                else { 

                $scope.status.properties[3].status = 'warning';
                $scope.status.properties[3].message = 'Extremely poor Signal & Channels are overlapping';
                $scope.status.properties[3].suggestion = 'Move towards AP & Set Channel mode to Auto';
            
            }
            };
         };
            RadioCheck();
// AuthenticationCheck conditions
            var AuthenticationCheck =function() {
            if ($scope.response1.PCipher == 'CCMP' && $scope.response1.GCipher == 'CCMP' || $scope.response1.PCipher == 'AES' && $scope.response1.GCipher == 'AES') {
        
                $scope.status.properties[4].status = 'true';
                $scope.status.properties[4].message = 'Successfully Authenticated';
                $scope.status.properties[4].suggestion = '';

            } else {
        
                $scope.status.properties[4].status = 'false';
                $scope.status.properties[4].message = 'Encryption Issue';
            
            }
            };
            AuthenticationCheck();
//AssociationCheck conditions
            var Association =function () {
            if ($scope.response1.MAC.length >= 0) {
        
                $scope.status.properties[5].status = 'true';
                $scope.status.properties[5].message = 'Getting Physical Address of your system';
                $scope.status.properties[5].suggestion = '';

            } else {
        
                $scope.status.properties[5].status = 'false';
                $scope.status.properties[5].message = 'Misconfiguration WPA/WPA2';
                $scope.status.properties[5].suggestion = '';

            }
            };
            Association();
            console.log($scope.response3);
    };

        var errorCallback = function(data) {
            console.log('Error: ' + data);
        };

        $http.get('/currentscan')
  		.then(successCallback,errorCallback);

        $http.get('/radioscan')
  		.then(successCallback1,errorCallback);
        
        };
    
	$scope.getData ();
});
                            