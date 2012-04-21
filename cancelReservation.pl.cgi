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
    my $sth = $dbh->prepare("SELECT startTime, type, stylist FROM appointment WHERE client=?") or die "$!";
    $sth->execute($username);
    while (my @result = $sth->fetchrow_array()) {
	my $typeid = $result[1];
	my $stylistid = $result[2];
	my $sth1 = $dbh->prepare("SELECT name FROM appttype WHERE id=?") or die "Line 90 $!";
	$sth1->execute($typeid);
	my ($result) = $sth1->fetchrow_array();
	my $appttype = $result;
	my $sth2 = $dbh->prepare("SELECT name FROM stylist WHERE id=?") or die "$!";
	$sth2->execute("$stylistid");
	my ($result) = $sth2->fetchrow_array();
	my $stylistname = $result;
	$appointmentstring=$result[0]." ".$appttype." ".$stylistname."\n";
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
    @cancel = split(/ /, $cancel);
    $start = $cancel[0]." ".$cancel[1];
    my $sth = $dbh->prepare("SELECT id FROM client WHERE username=?");
    $sth->execute("$user");
    my ($uid) = $sth->fetchrow_array();
    $sth->finish;
    my $sth1 = $dbh->prepare("DELETE FROM appointment WHERE client=? AND startTime=?");
    $sth1->execute($uid, "$start");
    $sth1->finish;
    
    print "Appointment successfully canceled! <br>";
    $dbh->do("DELETE FROM appointment WHERE client=$uid AND startTime=\"$start\"");
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
