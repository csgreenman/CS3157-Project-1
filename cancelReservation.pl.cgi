#!/usr/bin/perl

#BEGIN { unshift @INC, "/home/csg2119/Perl_Modules/lib/perl/5.10.1" };

use CGI::Carp qw(fatalsToBrowser);
print "content-type: text/html\n\n";
use Digest::MD5 qw(md5 md5_hex md5_base64);
use DBI;
use DBD::SQLite;
use CGI 'param';

my $dbfile = "salon.db";
my $dbh = DBI->connect("DBI:SQLite:dbname=$dbfile","","") or die "Couldn't connect to database";

my @names = param;
my $namestring = join(",", @names);

my $user = param('user');
my $cancel = param('apt');

our @hairappointmenttypes = qw(Cut Color Perm Trim Blowout);
our %hairtypehash = map{$_ => 1} @hairappointmenttypes;
our @salonappointmenttypes = qw(Manicure Pedicure ManiPediCombo Spa Facial);
our %salontypehash = map{$_ => 1} @salonappointmenttypes;

# two cgi scripts redirect to cancelReservation:
# home.pl.cgi uses the GET method, and clienttest.pl.cgi uses POST

if ($cancel) { &cancel; }
&seeAppointments;


=out
if ($type eq "cancel"){
	print "<html><body><center>";
	print "<form name=\"MyForm\" method=POST action=\"clienttest.pl.cgi\">";
	print "<input type=\"hidden\" name=\"stuff\" value=\"$type\">";
	print "<input type=\"hidden\" value=\"$user\" name=\"user\"></form>";
	print "<script type=\"text/javascript\" language=\"JavaScript\"><!--
	document.MyForm.submit();
	//--></script>";
	print "</center></body></html>";
}
else
{	
    if ($inp[0] eq "showappointments"){
	&seeAppointments;
    }
    else{
	@t = split('\*',$c);
	$user = $t[1];
	
	my $string = $ENV{REMOTE_ADDR} . " cancelled a reservation as user \"" . $user . "\" at " . localtime;
	&log($string);
	
	print "<html><body><center>";
	print "Appointment cancelled!";	
	print "<form name=\"MyForm\" method=GET action=\"home.pl.cgi\">";
	print "<input type=\"hidden\" name=\"user\" value=\"$user\">";
	print "<input type=\"hidden\" name=\"user\" value=\"$user\">";
	print "<input type=\"submit\" value=\"Home\"></form>";
	print "</center></body></html>";
    }
}

=cut

sub seeAppointments{
    my $appointmentstring;
    my @appointments;
    my $i = 0;
    my $sth = $dbh->prepare("SELECT id FROM client WHERE username=?") or die "$!";
    $sth->execute("$user");
    my ($username) = $sth->fetchrow_array();
    $sth->finish;
    my $sth = $dbh->prepare("SELECT date, time, type, stylist FROM appointment WHERE client=?") or die "$!";
    $sth->execute($username);
    while (my @result = $sth->fetchrow_array()) {
	my $date = $result[0];
	my $time = $result[1];
	#$time = s/\%([A-Fa-f0-9]{2})/pack('C', hex($1))/seg;
	my $type = $result[2];
	my $stylistid = $result[3];
	#my $sth1 = $dbh->prepare("SELECT name FROM appttype WHERE id=?") or die "Line 90 $!";
	#$sth1->execute($typeid);
	#my ($result) = $sth1->fetchrow_array();
	#my $appttype = $result;
	my $sth2 = $dbh->prepare("SELECT name FROM stylist WHERE id=?") or die "$!";
	$sth2->execute("$stylistid");
	my ($result) = $sth2->fetchrow_array();
	my $stylistname = $result;
	$appointmentstring=$date." at ".$time." ".$type." with ".$stylistname."\n";
	$appointments[$i] = $appointmentstring;
	++$i;
    }

    print "<html><body><center>";
    print "Here are your current appointments<br><br>";
    print "<form action=\"cancelReservation.pl.cgi\" method=GET>";
    print "<action=\"cancelReservation.pl.cgi\" method=GET>";
    foreach (@appointments){
	print "<input type=\"radio\" name=\"apt\" value=\"$_\">$_<br/>";	
    }
    print "<input type=\"hidden\" value=\"$user\" name=\"user\">";
    print "<input type=\"submit\" value=\"Cancel\"></form>";
    print "</html></body></center>";
}



sub cancel {
    print "<html><body><center>";
    @init = split(/&/, $cancel);
    @cancel = split(/ /, $init[0]);
    $date = $cancel[0];
    $time = $cancel[2];
    $type = $cancel[3];
    $stylist = $cancel[5];
    print "Stylist: ", $stylist, "<br>";
    #$stylist =~ s/\%([A-Fa-f0-9]{2})/pack('C', hex($1))/seg;
    my $sth2 = $dbh->prepare("SELECT id FROM stylist WHERE name=?");
    $sth2->execute("$stylist");
    my ($stylistid) = $sth2->fetchrow_array();
    print "ID: ", $stylistid, "<br>";
    my $sth = $dbh->prepare("SELECT id FROM client WHERE username=?");
    $sth->execute("$user");
    my ($uid) = $sth->fetchrow_array();
    $sth->finish;
    my $sth1 = $dbh->prepare("DELETE FROM appointment WHERE client=? AND date=? AND time=?");
    $sth1->execute($uid, $date, $time);
    $sth1->finish;
    if (exists $hairtypehash{$type}) {
	my $sth3 = $dbh->prepare("INSERT INTO hair_availability VALUES(NULL, ?, ?, ?)");
	$sth3->execute($date, $time, $stylistid);
    }
    elsif (exists $salontypehash{$type}) {
	my $sth3 = $dbh->prepare("INSERT INTO salon_availability VALUES(NULL, ?, ?, ?)");
	$sth3->execute($date, $time, $stylistid);
    }
    print "Appointment successfully canceled! <br>";
    #$dbh->do("DELETE FROM appointment WHERE client=$uid AND startTime=\"$start\"");
    print "</html></body></center>";
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
