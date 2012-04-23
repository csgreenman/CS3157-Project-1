#!/usr/bin/perl -T
use Fcntl; #The Module
use Digest::MD5 qw(md5 md5_hex md5_base64);
use CGI 'param';
use strict;

print "content-type: text/html \n\n";

# read whatever was passed through the POST method
read(STDIN, my $in, $ENV{'CONTENT_LENGTH'});

#$in = $ENV{QUERY_STRING};
my @inp = split(/&/,$in);
my @value = split(/=/,$inp[0]);
our $user = $value[1];
@value = split(/=/,$inp[1]);
my $command = $value[0];

if ($command eq "user"){
	if ($value[1] eq "admin"){
		&admin;
	}
	else{
		&loggedIn;
	}
}
elsif ($command eq "act"){
	&seeActivity;
}
elsif ($command eq "adminact"){
	&printActivity;
}
else{
	print "ERROR: $in";
}


sub seeActivity{
	my @in = split('&',$in);
	@value = split('=',$in[0]);
	my $user = $value[1];	

	open(FH, "activity.txt");
	my @file = <FH>;
	my @actions;
	chomp(@file);
	foreach (@file){
		if ($_ =~ m/ /) {
			if ($` eq $ENV{REMOTE_ADDR}){
				push(@actions,$_);
			}
		}
	}
	chomp(@actions);

	my $string = $ENV{REMOTE_ADDR} . " viewed past activity as user \"" . $user . "\" at " . localtime;
	&log($string);

	print "<html><body><center>";
	print "<font size=\"5\" face=\"trebuchet ms\" color=#9372ED>";
	print "<body style=\"background-attachment: fixed; background-position: bottom right; background-repeat: no-repeat;\" background=\"purpleflower.jpg\" bgcolor=\"black\">";
	print "At this IP address, the following actions have occurred:<br><br>";
	print "<font size=\"4\">";
	foreach(@actions){
		print "$_<br>";
	}
	print "<br><form name=\"MyForm\" method=POST action=\"home.pl.cgi\">";
	print "<input type=\"hidden\" name=\"user\" value=\"$user\">";
	print "<input type=\"hidden\" name=\"user\" value=\"$user\">";
	print "<input type=\"submit\" value=\"Home\" class=\"button\"></form>";
	print "<style type=\"text/css\">";
	print ".button {border: 1px solid #000000;background: #000000; color:#9372ED; font: bold large 'trebuchet ms',helvetica,sans-serif;}";
	print ".button:hover {border: 1px solid #000000; background: #000000; color:#000000; font: bold large 'trebuchet ms',helvetica,sans-serif;}";
	print "</style></html></body></center>";

}

# create a page that allows the user to submit URLs to the file url_sub.txt. This contains the 
# button labeled "See current files in url_sub.txt" which tells the code to write no new lines to
# the file but simply print out what is already in the file
sub loggedIn{

	print "<html><body><font size=\"5\" face=\"trebuchet ms\" color=#9372ED>";
	print "<body style=\"background-attachment: fixed; background-position: bottom right; background-repeat: no-repeat;\" background=\"purpleflower.jpg\" bgcolor=\"black\">";
	print "<center><form action=\"makeReservation.pl.cgi\" method=GET>";
	print "<input type=\"hidden\" value=$user name=\"user\">";
	print "<input type=\"submit\" name=\"res\" value=\"Make Reservation\" class=\"button\"></form>";
	print "<form action=\"cancelReservation.pl.cgi\" method=GET>";
	print "<input type=\"hidden\" value=$user name=\"user\">";
	print "<input type=\"submit\" name=\"cancel\" value=\"See/Cancel Reservation\" class=\"button\"></form>";
	print "<form action=\"home.pl.cgi\" method=POST>";
	print "<input type=\"hidden\" value=$user name=\"user\">";
	print "<input type=\"submit\" name=\"act\" value=\"See Activity\" class=\"button\"></form>";
	print "<form action=\"resetPassword.pl.cgi\" method=POST>";
	print "<input type=\"hidden\" value=$user name=\"user\">";
	print "<input type=\"submit\" name=\"changepass\" value=\"Change Password\" class=\"button\"></form>";
	print "<form action=\"test.html\">";
	print "<input type=\"submit\" name=\"logout\" value=\"Logout\" class=\"button\"></form>";
	print "<style type=\"text/css\">";
	print ".button {border: 1px solid #000000;background: #000000; color:#9372ED; font: bold large 'trebuchet ms',helvetica,sans-serif;}";
	print ".button:hover {border: 1px solid #000000; background: #000000; color:#000000; font: bold large 'trebuchet ms',helvetica,sans-serif;}";
	print "</style></html></body></center>";
}

sub admin{
	print "<html><body><center>";
	print "<font size=\"5\" face=\"trebuchet ms\" color=#9372ED>";
	print "<body style=\"background-attachment: fixed; background-position: bottom right; background-repeat: no-repeat;\" background=\"purpleflower.jpg\" bgcolor=\"black\">";
	print "WELCOME ADMIN<br><br><form action=\"home.pl.cgi\" method=POST>";
	print "<input type=\"hidden\" value=$user name=\"user\">";
	print "<input type=\"submit\" name=\"adminact\" value=\"See Activity\" class=\"button\"></form>";
	print "<form action=\"resetPassword.pl.cgi\" method=POST>";
	print "<input type=\"hidden\" value=$user name=\"user\">";
	print "<input type=\"submit\" name=\"changepass\" value=\"Change Password\" class=\"button\"></form>";
	print "<form action=\"test.html\">";
	print "<input type=\"submit\" name=\"logout\" value=\"Logout\" class=\"button\"></form>";
	print "<style type=\"text/css\">";
	print ".button {border: 1px solid #000000;background: #000000; color:#9372ED; font: bold large 'trebuchet ms',helvetica,sans-serif;}";
	print ".button:hover {border: 1px solid #000000; background: #000000; color:#000000; font: bold large 'trebuchet ms',helvetica,sans-serif;}";
	print "</style></html></body></center>";
}

sub log{
	my $string = shift;
	open(FH, "activity.txt");
	my @file = <FH>;
	push(@file,$string);
	chomp(@file);
		
	# rewrite everything to the file
	open FILE, ">activity.txt";
	foreach (@file){
		print FILE "$_\n";
	}
	close FILE;
}

sub printActivity{
	my $string = $ENV{REMOTE_ADDR} . " viewed all activity as \"admin\" at " . localtime;
	&log($string);
	
	open(FH, "activity.txt");
	my @file = <FH>;
	chomp(@file);
		
	print "<html><body><center>";
	print "<font size=\"5\" face=\"trebuchet ms\" color=#9372ED>";
	print "<b>Here is a log of everything that has happened on the site:</b><br><br>";
	print "<font size=\"3\" color=#000000>";
	foreach(@file){
		print "$_<br>";
	}


	print "<br><form name=\"MyForm\" method=POST action=\"home.pl.cgi\">";
	print "<input type=\"hidden\" name=\"user\" value=\"$user\">";
	print "<input type=\"hidden\" name=\"user\" value=\"$user\">";
	print "<input type=\"submit\" value=\"Home\" class=\"button\"></form>";
	print "<style type=\"text/css\">";
	print ".button {border: 1px solid #FFFFFF;background: #FFFFFF; color:#9372ED; font: bold large 'trebuchet ms',helvetica,sans-serif;}";
	print ".button:hover {border: 1px solid #FFFFFF; background: #FFFFFF; color:#FFFFFF; font: bold large 'trebuchet ms',helvetica,sans-serif;}";
	print "</style></html></body></center>";
}