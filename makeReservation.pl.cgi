#!/usr/bin/perl -T

#BEGIN { unshift @INC, "/home/csg2119/Perl_Modules/lib/perl/5.8.8" };

use CGI::Carp qw(fatalsToBrowser);
use Fcntl; #The Module
use Digest::MD5 qw(md5 md5_hex md5_base64);
use CGI 'param';
use DBI;
use DBD::SQLite;

our @hairorsalon = qw(Hair Salon);
our @hairappointmenttypes = qw(Cut Color Perm Trim Blowout);
our %hairtypehash = map{$_ => 1} @hairappointmenttypes;
our @salonappointmenttypes = qw(Manicure Pedicure ManiPediCombo Spa Facial);
our %salontypehash = map{$_ => 1} @salonappointmenttypes;
our @weekday = qw(Sunday Monday Tuesday Wednesday Thursday Friday Saturday);
our @hairstylists = qw(Amy Beth Catherine Diana Evelyn);
our @salonworkers = qw(Fiona Gina Hannah Irene Jeanne);

my $dbfile = "salon.db";
my $dbh = DBI->connect("DBI:SQLite:dbname=$dbfile","","");
#my @days;
#my @apptdays;
#my @appttimes;

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
my $type = param('AppointmentType');
my $subtype = param('Type');
my $date = param('Day');
my $time = param('Time');
$time =~ s/\%([A-Fa-f0-9]{2})/pack('C', hex($1))/seg;
my $stylist = param('Person');

my @value = split('=',$in[0]);

if ($value[0] eq "user"){
    $user = $value[1];
    my @value = split('=',$in[1]);
    $command = $value[0];
    #$type = $value[1];
}
else{
    $command = $value[0];
    #$type = $value[1];
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
    &createAppointment;

    my $string = $ENV{REMOTE_ADDR} . " made a new reservation as user \"" . $user . "\" at " . localtime;
    &log($string);
    
    print "<html><body><center>";
    print "<font size=\"5\" face=\"trebuchet ms\" color=#9372ED>";
    print "<body style=\"background-attachment: fixed; background-position: bottom right; background-repeat: no-repeat;\" background=\"purpleflower.jpg\" bgcolor=\"black\">";
    print "Congrats, appointment has been made!";	
    print "<form name=\"MyForm\" method=POST action=\"home.pl.cgi\">";
    print "<input type=\"hidden\" name=\"user\" value=\"$user\">";
    print "<input type=\"hidden\" name=\"user\" value=\"$user\">";
    print "<input type=\"submit\" value=\"Home\" class=\"button\"></form>";
    print "<style type=\"text/css\">";
    print ".button {border: 1px solid #000000;background: #000000; color:#9372ED; font: bold large 'trebuchet ms',helvetica,sans-serif;}";
    print ".button:hover {border: 1px solid #000000; background: #000000; color:#000000; font: bold large 'trebuchet ms',helvetica,sans-serif;}";
    print "</style></html></body></center>";
}
else{
	print "ERROR, command is $command and type is $type\n";
	print "in is $in";
	print "c is $c";
}

sub startReservation{
	@inp = qw(Hair Salon);
	print "<html><body><center>";
	print "<font size=\"5\" face=\"trebuchet ms\" color=#9372ED>";
	print "<body style=\"background-attachment: fixed; background-position: bottom right; background-repeat: no-repeat;\" background=\"purpleflower.jpg\" bgcolor=\"black\">";
	print "What type of appointment would you like to make?";
	print "<form action=\"makeReservation.pl.cgi\" method=GET>";
	print "<select name=\"AppointmentType\" action=\"makeReservation.pl.cgi\" method=GET>";
	foreach(@inp) {
	    print "<option value=$_>$_";
	}
	print "</select>";
	print "<input type=\"hidden\" value=$user name=\"user\">";
	print "<input type=\"submit\" value=\"Submit\" class=\"button\"></form>";
	print "<style type=\"text/css\">";
	print ".button {border: 1px solid #000000;background: #000000; color:#9372ED; font: bold large 'trebuchet ms',helvetica,sans-serif;}";
	print ".button:hover {border: 1px solid #000000; background: #000000; color:#000000; font: bold large 'trebuchet ms',helvetica,sans-serif;}";
	print "</style></html></body></center>";
}

sub AppointmentType{
    #$type = param('AppointmentType');
    print "<html><body><center>";
    print "<font size=\"5\" face=\"trebuchet ms\" color=#9372ED>";
    print "<body style=\"background-attachment: fixed; background-position: bottom right; background-repeat: no-repeat;\" background=\"purpleflower.jpg\" bgcolor=\"black\">";
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
    print "<input type=\"submit\" value=\"Submit\" class=\"button\"></form>";
    print "<style type=\"text/css\">";
    print ".button {border: 1px solid #000000;background: #000000; color:#9372ED; font: bold large 'trebuchet ms',helvetica,sans-serif;}";
    print ".button:hover {border: 1px solid #000000; background: #000000; color:#000000; font: bold large 'trebuchet ms',helvetica,sans-serif;}";
    print "</style></html></body></center>";
}

sub pickDay{
    #$subtype = param('Type');
    if (exists $hairtypehash{$subtype}) {
	my $i = 0;
	my $sth = $dbh->prepare("SELECT date FROM hair_availability");
	$sth->execute();
	while(my @result = $sth->fetchrow_array()) {
	    $days[$i] = $result[0];	
	    ++$i;
	}
	my %hash = map{$_ => 1 } @days;
	@apptdays = keys %hash;
    }
    elsif (exists $salontypehash{$subtype}) {
	my $i = 0;
	my $sth = $dbh->prepare("SELECT date FROM salon_availability");
	$sth->execute();
	while(my @result = $sth->fetchrow_array()) {
	    $days[$i] = $result[0];
	    ++$i;
	}
	my %hash = map{$_ => 1 } @days;
	@apptdays = keys %hash;
    }
    print "<html><body><center>";
    print "<font size=\"5\" face=\"trebuchet ms\" color=#9372ED>";
    print "<body style=\"background-attachment: fixed; background-position: bottom right; background-repeat: no-repeat;\" background=\"purpleflower.jpg\" bgcolor=\"black\">";
    print "What day would you like to make your appointment?\n";
    print "<form action=\"makeReservation.pl.cgi\" method=GET>";
    print "<action=\"makeReservation.pl.cgi\" method=GET>";
    foreach (@apptdays){
	print "<input type=\"radio\" name=\"Day\" value=$_>$_<br/>";
    }
    print "<input type=\"hidden\" value=$user name=\"user\">";
    print "<input type=\"hidden\" value=$subtype name=\"Type\">";
    print "<input type=\"submit\" value=\"Submit\" class=\"button\"></form>";
    print "<style type=\"text/css\">";
    print ".button {border: 1px solid #000000;background: #000000; color:#9372ED; font: bold large 'trebuchet ms',helvetica,sans-serif;}";
    print ".button:hover {border: 1px solid #000000; background: #000000; color:#000000; font: bold large 'trebuchet ms',helvetica,sans-serif;}";
    print "</style></html></body></center>";
}

sub pickTime{
    my @times;
    my $j = 0;
    print "<html><body><center>";
    print "<font size=\"5\" face=\"trebuchet ms\" color=#9372ED>";
    print "<body style=\"background-attachment: fixed; background-position: bottom right; background-repeat: no-repeat;\" background=\"purpleflower.jpg\" bgcolor=\"black\">";
    print "What time would you like to make your appointment?\n";
    print "<form action=\"makeReservation.pl.cgi\" method=GET>";
    print "<action=\"makeReservation.pl.cgi\" method=GET>";
    if(exists $hairtypehash{$subtype}) {
	my $sth = $dbh->prepare("SELECT time FROM hair_availability WHERE date=?");
	$sth->execute($date);
	while(my @result = $sth->fetchrow_array()) {
	    $times[$j] = $result[0];
	    ++$j;
	}
    }
    elsif(exists $salontypehash{$subtype}) {
	my $sth = $dbh->prepare("SELECT time FROM salon_availability WHERE date=?");
	$sth->execute($date);
	while(my @result = $sth->fetchrow_array()) {
	    $times[$j] = $result[0];
	    ++$j;
	}
    }

    my %timehash = map{$_ => 1} @times;
    @appttimes = keys %timehash;
    foreach (@appttimes){
	print "<input type=\"radio\" name=\"Time\" value=$_>$_<br/>";	
    }
    print "<input type=\"hidden\" value=$user name=\"user\">";
    print "<input type = \"hidden\" value=$subtype name = \"Type\">";
    print "<input type = \"hidden\" value = $date name = \"Day\">";
    print "<input type=\"submit\" value=\"Submit\" class=\"button\"></form>";
    print "<style type=\"text/css\">";
    print ".button {border: 1px solid #000000;background: #000000; color:#9372ED; font: bold large 'trebuchet ms',helvetica,sans-serif;}";
    print ".button:hover {border: 1px solid #000000; background: #000000; color:#000000; font: bold large 'trebuchet ms',helvetica,sans-serif;}";
    print "</style></html></body></center>";
}

sub pickPerson{
    my @stylists;
    my $k=0;
    print "<html><body><center>";
    print "<font size=\"5\" face=\"trebuchet ms\" color=#9372ED>";
    print "<body style=\"background-attachment: fixed; background-position: bottom right; background-repeat: no-repeat;\" background=\"purpleflower.jpg\" bgcolor=\"black\">";
    print "Do you have a specific stylist that you would like?";
    print "<form action=\"makeReservation.pl.cgi\" method=GET>";
    print "<select name=\"Person\" action=\"makeReservation.pl.cgi\" method=GET>";
    if (exists $hairtypehash{$subtype}) {
	my $sth = $dbh->prepare("SELECT stylist FROM hair_availability WHERE date=? AND time=?");
	$sth->execute($date, $time);
	while(my @result = $sth->fetchrow_array()) {
	    $stylists[$k] = $result[0];
	    ++$k;
	}
    }
    elsif (exists $salontypehash{$subtype}) {
	my $sth = $dbh->prepare("SELECT stylist FROM salon_availability WHERE date=? AND time=?");
	$sth->execute($date, $time);
	while(my @result = $sth->fetchrow_array()) {
	    $stylists[$k] = $result[0];
	    ++$k;
	}
    }
    my %stylisthash = map{$_ => 1} @stylists;
    @stylists = keys %stylisthash;
    my $a = 0;
    my @stylistnames;


    foreach (@stylists) {
	my $sth1 = $dbh->prepare("SELECT name FROM stylist WHERE id=?");
	$sth1->execute($_);
	my ($name) = $sth1->fetchrow_array();
	$stylistnames[$a] = $name;
	++$a;
    }

    foreach (@stylistnames){
	print "<option value=$_>$_";
    }
    print "</select>";
    print "<input type=\"hidden\" value=$user name=\"user\">";
    print "<input type=\"hidden\" value=$subtype name=\"Type\">";
    print "<input type=\"hidden\" value=$date name=\"Day\">";
    print "<input type=\"hidden\" value=$time name=\"Time\">";
    print "<input type=\"submit\" value=\"Submit\" class=\"button\"></form>";
    print "<style type=\"text/css\">";
    print ".button {border: 1px solid #000000;background: #000000; color:#9372ED; font: bold large 'trebuchet ms',helvetica,sans-serif;}";
    print ".button:hover {border: 1px solid #000000; background: #000000; color:#000000; font: bold large 'trebuchet ms',helvetica,sans-serif;}";
    print "</style></html></body></center>";
}

sub createAppointment {
    my $sth = $dbh->prepare("SELECT id FROM client WHERE username=?");
    $sth->execute("$user");
    my ($id) = $sth->fetchrow_array();
    my $sth2 = $dbh->prepare("SELECT id FROM stylist WHERE name=?");
    $sth2->execute("$stylist");
    my ($stylistid) = $sth2->fetchrow_array();
    my $sth3 = $dbh->prepare("INSERT INTO appointment VALUES(NULL, ?, ?, ?, ?, ?)");
    $sth3->execute($id, $date, $time, "$subtype", $stylistid);
    if (exists $hairtypehash{$subtype}) {
	my $sth1 = $dbh->prepare("DELETE FROM hair_availability WHERE date=? AND time=? AND stylist=?");
	$sth1->execute($date, $time, $stylistid);
    }
    elsif (exists $salontypehash{$subtype}) {
	my $sth1 = $dbh->prepare("DELETE FROM salon_availability WHERE date=? AND time=? AND stylist=?");
	$sth1->execute($date, $time, $stylistid);
    }
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