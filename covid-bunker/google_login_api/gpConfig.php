<?php
session_start();

//Include Google client library 
include_once 'src/Google_Client.php';
include_once 'src/contrib/Google_Oauth2Service.php';

/*
 * Configuration and setup Google API
 */
$clientId = '128673522219-fqk2n96l2ul0u9s3fjqm04inkknr0dtd.apps.googleusercontent.com'; //Google client ID
$clientSecret = 'SnYjFBPDYCnaXduycZ1jLkBd'; //Google client secret
$redirectURL = 'WEBSITE URL'; //Callback URL

//Call Google API
$gClient = new Google_Client();
$gClient->setApplicationName('Login to Covid-Bunker.com');
$gClient->setClientId($clientId);
$gClient->setClientSecret($clientSecret);
$gClient->setRedirectUri($redirectURL);

$google_oauthV2 = new Google_Oauth2Service($gClient);
?>