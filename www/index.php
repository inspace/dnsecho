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
    <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.11.2/jquery.min.js"></script>
    <script>
        function doReq(){
            $.ajax({
                url: "http://www.ipgeoloc.com/dns.php?c=<?php echo $c ?>&i=<?php echo $guid ?>",
                type: 'POST',
                success: function(data) {
                    $('body').append('<div>' + data + '</div>');
                }
            });
        }

        document.onload = setTimeout(doReq, 2000);

    </script>
</head>

<body>

    <img src="<?php echo $imgUrl ?>">

    Searching for your DNS server...

</body>

</html>
