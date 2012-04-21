#!/usr/bin/perl

#BEGIN { unshift @INC, "/home/csg2119/Perl_Modules/lib/perl/5.8.8" };

use CGI::Carp qw(fatalsToBrowser);
use Fcntl; #The Module
use Digest::MD5 qw(md5 md5_hex md5_base64);
use CGI 'param';
use DBI;
use DBD::SQLite;

our @hairorsalon = qw(Hair Salon);
our @hairappointmenttypes = qw(Cut Color Perm Trim Blowout);
our @salonappointmenttypes = qw(Manicure Pedicure ManiPediCombo Spa Facial);
our @weekday = qw(Sunday Monday Tuesday Wednesday Thursday Friday Saturday);
our @hairstylists = qw(Amy Beth Catherine Diana Evelyn);
our @salonworkers = qw(Fiona Gina Hannah Irene Jeanne);

my $dbfile = "salon.db";
my $dbh = DBI->connect("DBI:SQLite:dbname=$dbfile","","");
my @days;

print "content-type: text/html \n\n";

# read whatever was passed through the GET method

if ($ENV{'REQUEST_METHOD'} eq "POST") { 
    read(STDIN, $in, $ENV{CONTENT_LENGTH});
}
    
elsif ($ENV{'REQUEST_METHOD'} eq "GET") {
    $in = $ENV{QUERY_STRING};
}

my @temp = split('=',$in);
our @inp = split('\*', $temp[1]);
my @in = split('&',$in);

our $user = "";
my $command = "";
my $type = "";

my @value = split('=',$in[0]);

if ($value[0] eq "user"){
    $user = $value[1];
    my @value = split('=',$in[1]);
    $command = $value[0];
    $type = $value[1];
}
else{
    $command = $value[0];
    $type = $value[1];
    @value = split('=',$in[1]);
    $user = $value[1];
}

if ($command eq "res"){
	&startReservation;
}
elsif ($command eq "AppointmentType"){	
	&AppointmentType;
}
elsif ($command eq "Type"){	
	&pickDay;
}
elsif ($command eq "Day"){	
	&pickTime;
}
elsif ($command eq "Time"){
	&pickPerson;
}
elsif ($command eq "Person"){

	my $string = $ENV{REMOTE_ADDR} . " made a new reservation as user \"" . $user . "\" at " . localtime;
	&log($string);

	print "<html><body><center>";
	print "Congrats, appointment has been made!";	
	print "<form name=\"MyForm\" method=GET action=\"home.pl.cgi\">";
	print "<input type=\"hidden\" name=\"user\" value=\"$user\">";
	print "<input type=\"submit\" value=\"Home\"></form>";
	print "</center></body></html>";
}
else{
	print "ERROR, command is $command and type is $type\n";
	print "in is $in";
	print "c is $c";
}

sub startReservation{
	@inp = qw(Hair Salon);
	print "<html><body><center>";
	print "What type of appointment would you like to make?";
	print "<form action=\"makeReservation.pl.cgi\" method=GET>";
	print "<select name=\"AppointmentType\" action=\"makeReservation.pl.cgi\" method=GET>";
	foreach(@inp) {
	    print "<option value=$_>$_";
	}
	print "</select>";
	print "<input type=\"hidden\" value=$user name=\"user\">";
	print "<input type=\"submit\" value=\"Submit\"></form>";
	print "</html></body></center>";
}

sub AppointmentType{
	print "<html><body><center>";
	print "What specific type of appointment would you like to make?";
	print "<form action=\"makeReservation.pl.cgi\" method=GET>";
	print "<select name=\"Type\" action=\"makeReservation.pl.cgi\" method=GET>";
	if($type eq "Hair") {
	    foreach(@hairappointmenttypes) {
		print "<option value=$_>$_";
	    }
	}
	elsif($type eq "Salon") {
	    foreach(@salonappointmenttypes) {
		print "<option value=$_>$_";
	    }
	}
	print "</select>";
	print "<input type=\"hidden\" value=$user name=\"user\">";
	print "<input type=\"submit\" value=\"Submit\"></form>";
	print "</html></body></center>";
}

sub pickDay{
    my $i = 0;
    my $sth = $dbh->prepare("SELECT date FROM available_appt");
    $sth->execute();
    while(my @result = $sth->fetchrow_array()) {
	$days[$i] = $result[0];	
	++$i;
    }

    $size = @days;
    for($j = 0; $j < $size-1; $j++) {
	for($k = $j+1; $k < $size; $k++) {
	    if($days[$j] eq $days[$k]) {	
		splice @days, $j, 1;
	    }
	}
    }

   for($j = 0; $j < $size-1; $j++) {
	for($k = $j+1; $k < $size; $k++) {
 	    if($days[$j] eq $days[$k]) {
		splice @days, $j, 1;
	    }
	}
    }
    
    print "<html><body><center>";
    print "What day would you like to make your appointment?\n";
    print "<form action=\"makeReservation.pl.cgi\" method=GET>";
    print "<action=\"makeReservation.pl.cgi\" method=GET>";
    foreach (@days){
	print "<input type=\"radio\" name=\"Day\" value=$_>$_<br/>";
    }
    print "<input type=\"hidden\" value=$user name=\"user\">";
    print "<input type=\"submit\" value=\"Submit\"></form>";
    print "</html></body></center>";
}

sub pickTime{
	print "<html><body><center>";
	print "What time would you like to make your appointment?\n";
	print "<form action=\"makeReservation.pl.cgi\" method=GET>";
	print "<action=\"makeReservation.pl.cgi\" method=GET>";
	foreach (@inp){
		if ($_ ne "done" && $_ ne "&user" && $_ ne "reservation"){

			$_ =~ s/\%3A/:/;
			print "<input type=\"radio\" name=\"Time\" value=$_>$_<br/>";
		}	
	}
	print "<input type=\"hidden\" value=$user name=\"user\">";
	print "<input type=\"submit\" value=\"Submit\"></form>";
	print "</html></body></center>";
}

sub pickPerson{
	print "<html><body><center>";
	print "Do you have a specific stylist that you would like?";
	print "<form action=\"makeReservation.pl.cgi\" method=POST>";
	print "<select name=\"Person\" action=\"clienttest.pl.cgi\" method=POST>";
	foreach (@inp){
		if ($_ ne "done" && $_ ne "&user" && $_ ne "reservation"){
			print "<option value=$_>$_";
		}
	}
	print "</select>";
	print "<input type=\"hidden\" value=$user name=\"user\">";
	print "<input type=\"submit\" value=\"Submit\"></form>";
	print "</html></body></center>";
}

sub createAppointment {
    #$dbh->do("INSERT INTO appointment VALUES(
}

sub log{
	my $string = shift;
	open(FH, "activity.txt");
	@file = <FH>;
	push(@file,$string);
	chomp(@file);
		
	# rewrite everything to the file
	open FILE, ">activity.txt";
	foreach (@file){
		print FILE "$_\n";
	}
	close FILE;
}
