<?php

function gen_uuid() {
    //http://stackoverflow.com/questions/2040240/php-function-to-generate-v4-uuid
    return sprintf( '%04x%04x%04x%04x%04x%04x%04x%04x',
        mt_rand( 0, 0xffff ), mt_rand( 0, 0xffff ),
        mt_rand( 0, 0xffff ),
        mt_rand( 0, 0x0fff ) | 0x4000,
        mt_rand( 0, 0x3fff ) | 0x8000,
        mt_rand( 0, 0xffff ), mt_rand( 0, 0xffff ), mt_rand( 0, 0xffff )
    );
}

$guid = gen_uuid();

$salt = hash('sha1', strrev(substr($guid, 0, -4)));
$c = hash('md5', $salt . $guid);

$imgUrl = "http://" . $guid . ".test.ipgeoloc.com/t.gif";

?>

<html>

<head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <!-- The above 3 meta tags *must* come first in the head; any other head content must come *after* these tags -->
    <meta name="description" content="">
    <meta name="author" content="">
    <link rel="icon" href="../../favicon.ico">

    <title>Find your DNS Information</title>

    <!-- Bootstrap core CSS -->
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.4/css/bootstrap.min.css"

    <!-- Custom styles for this template -->
    <link href="jumbotron-narrow.css" rel="stylesheet">

    <style type="text/css">
      html, body, #map-canvas { height: 75%; margin: 0; padding: 0;}
    </style>

    <!-- Just for debugging purposes. Don't actually copy these 2 lines! -->
    <!--[if lt IE 9]><script src="../../assets/js/ie8-responsive-file-warning.js"></script><![endif]-->
    <!--<script src="../../assets/js/ie-emulation-modes-warning.js"></script> -->

    <!-- HTML5 shim and Respond.js for IE8 support of HTML5 elements and media queries -->
    <!--[if lt IE 9]>
      <script src="https://oss.maxcdn.com/html5shiv/3.7.2/html5shiv.min.js"></script>
      <script src="https://oss.maxcdn.com/respond/1.4.2/respond.min.js"></script>
    <![endif]-->

    <script type="text/javascript" src="https://maps.googleapis.com/maps/api/js?key=AIzaSyDRcS7X-Xmvi14Uuu2eH5asbn_AjoLDhFY"></script>

    <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.11.2/jquery.min.js"></script>
    <script>

        function addData(json){
            $('#status').remove();

            var ip = json.ip;
            var asn = json.asn;
            var isp = json.isp;
            
            var country = json.country;
            var region = json.region;
            if(!region){
                region = "-";
            }
            var city = json.city;
            if(!city){
                city = "-";
            }
            var lat = json.latitude;
            var lon = json.longitude;

            var nrow = "<tr><td>" + ip + "</td><td>" + asn + "</td><td>" + isp + "</td></tr>";
            $("#ntable tr:last").after(nrow);

            var lrow = "<tr><td>" + ip + "</td><td>" + country + "</td><td>" + region + "</td><td>" + city + "</td><td>" + lat + "</td><td>" + lon + "</td></tr>";
            $("#ltable tr:last").after(lrow);

            var point = new google.maps.LatLng(lat, lon);
            var marker = new google.maps.Marker({
                position: point,
                map: map,
                title: ip
            });
            map.setCenter(marker.getPosition());
            map.setZoom(6);
        }

        function doReq(){
            $.ajax({
                url: "dns.php?c=<?php echo $c ?>&i=<?php echo $guid ?>",
                type: 'POST',
                success: function(data) {
                    var dataLen = data.length;
                    for (var i = 0; i < dataLen; i++){
                        var ip = data[i];
                        $.getJSON("http://www.telize.com/geoip/" + ip + "?callback=?", addData);
                    }
                }
            });
        }

        document.onload = setTimeout(doReq, 2000);
    </script>

    <script type="text/javascript">
      function initialize() {
        var mapOptions = {
          center: { lat: 0.0, lng: 0.0},
          zoom: 1
        };
        map = new google.maps.Map(document.getElementById('map-canvas'), mapOptions);
      }
      google.maps.event.addDomListener(window, 'load', initialize);
    </script>

</head>

<body>

    <img src="<?php echo $imgUrl ?>">

   
    <div class="container">
      
      <div class="jumbotron">
        <h2>Find Your DNS Information</h2>
      </div>

      <p>
      This page will help you find the IP address, network, and geographic information about your DNS server.
      </p>

      
      <div id="status">
        <h3>Searching for your DNS Server...</h3>
      </div>

      <div class="row marketing">
        <div class="col-lg-6">
          
          <h3>DNS Network Info</h3>
          <table id="ntable" class="table table-bordered">
            <thead>
                <tr>
                    <th>IP Address</th>
                    <th>ASN</th>
                    <th>ISP Name</th>
                    <!-- <th>Hostname</th> -->
                </tr>
            </thead>
            <tbody>
            </tbody>
          </table>

          <h3>DNS Location</h3>
          <table id="ltable" class="table table-bordered">
             <thead>
                <tr>
                    <th>IP Address</th>
                    <th>Country</th>
                    <th>State/Region</th>
                    <th>City</th>
                    <th>Latitude</th>
                    <th>Longitude</th>
                </tr>
             </thead>
          </table> 
          
          <div id="map-canvas"></div>

        </div>

      <h3>Check on the command line</h3>
      <iframe width="420" height="315" src="https://www.youtube.com/embed/3L8uhuJSfMo" frameborder="0" allowfullscreen></iframe>

      <h3>What is DNS and how does it work?</h3>
      <p>
      DNS stands for Domain Name System. It provides a critical service to the Internet by converting hostnames, (e.g. www.google.com) into IP addresses, although it more than just this. Broadband customers typically have their DNS server automatically assigned to them by their ISP. Some users choose to use a public DNS service such as offered by <a href="https://developers.google.com/speed/public-dns/">Google</a> or <a href="https://www.opendns.com/home-internet-security/opendns-ip-addresses/">OpenDNS</a>. 
      </p>

      <p>
      There are really two "types" of DNS servers to be aware of. The first is called a recursive resolver. This is the DNS server that your computer directly asks questions to like "What is the IP Address of www.google.com?". The recursive resolver's job is to contact the DNS servers of specific domains on your behalf and ask it, "What is your IP Address?". The recursive resolver is the one typically assigned to you by your ISP and it is also known as your lDNS or local DNS server. The DNS servers of specific domains are called authoritative resolvers. They only answer questions about their domain.  
      </p>

      <p>
One reason you may be interested in what or where you DNS server is located is that it can have a large impact on your web-browsing performance. Lots of popular websites like Google, YouTube, and Facebook have content spread all over the globe so that nearby copies will improve user's browsing experience. These companies usually decide where you should download from based on your local DNS server. If you are far away from your local DNS server, you may get directed to download content from far away, degrading your browsing experience.  
      </p>

      </div>

      <footer class="footer">
        <p>&copy; InSpace 2015</p>
      </footer>

    </div> <!-- /container -->
    
</body>

</html>
