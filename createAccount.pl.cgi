#!/usr/bin/perl
BEGIN { unshift @INC, "/home/csg2119/Perl_Modules/lib/perl/5.10.1" };

use CGI::Carp qw(fatalsToBrowser);

use Fcntl; #The Module
use Digest::MD5 qw(md5 md5_hex md5_base64);
use DBI;
use DBD::SQLite;

my $dbfile="salon.db";
my $dbh = DBI->connect("DBI:SQLite:dbname=$dbfile", "", "") or die "Couldn't connect to database $!";

print "content-type: text/html \n\n";

# read whatever was passed through the POST method
read(STDIN, my $in, $ENV{CONTENT_LENGTH});

if ($ENV{CONTENT_LENGTH} == 0 && $ENV{QUERY_STRING} eq ""){
	&createNewAccount;
}

# POST used
elsif ($ENV{CONTENT_LENGTH} > 0){
	&create;
}
else{
	print "<html><body><center>";
	print "<font size=\"5\" face=\"trebuchet ms\" color=#9372ED>New account created!";
	print "<body style=\"background-attachment: fixed; background-position: bottom right; background-repeat: no-repeat;\" background=\"purpleflower.jpg\" bgcolor=\"black\">";
	print "<form action=\"login.pl.cgi\" method=POST>";
	print "<input type=\"submit\" value=\"Login\" class=\"button\"></form>";
	print "<style type=\"text/css\">";
	print ".button {border: 1px solid #000000;background: #000000; color:#9372ED; font: bold large 'trebuchet ms',helvetica,sans-serif;}";
	print ".button:hover {border: 1px solid #000000; background: #000000; color:#000000; font: bold large 'trebuchet ms',helvetica,sans-serif;}";
	print "</style></html></body></center>";
}

# create a page that takes in user and password information and submits it through the POST method
sub createNewAccount{
	print "<html><body><center>";
	print "<font size=\"5\" face=\"trebuchet ms\" color=#9372ED>";
	print "<body style=\"background-attachment: fixed; background-position: bottom right; background-repeat: no-repeat;\" background=\"purpleflower.jpg\" bgcolor=\"black\">";
	print "<form action=\"createAccount.pl.cgi\" method=POST>New Username: ";
	print "<input type=\"text\" name=\"t1\" class=\"input\"><br><br>New Password: ";
	print "<input type=\"password\" name=\"t2\" class=\"input\"><br><br> Confirm Password: ";
	print "<input type=\"password\" name=\"t3\" class=\"input\"><br><br> Email: ";
	print "<input type=\"text\" name=\"t4\" class=\"input\"><br><br>First name:";
	print "<input type=\"text\" name=\"t5\" class=\"input\"><br><br>Last name:";
	print "<input type=\"text\" name=\"t6\" class=\"input\"><br><br>";   
	print "<input type=\"submit\" value=\"Submit\" class=\"button\"></form>";
	print "<style type=\"text/css\">";
	print ".button {border: 1px solid #000000;background: #000000; color:#9372ED; font: bold large 'trebuchet ms',helvetica,sans-serif;}";
	print ".button:hover {border: 1px solid #000000; background: #000000; color:#000000; font: bold large 'trebuchet ms',helvetica,sans-serif;}";
	print ".input {border: 1px solid #9372ED; background: #9372ED;}";
	print "</style></html></body></center>";
}

# get the input submitted through the POST method and split it so that you get
# the corresponding user and password strings into respective variables and format
# it to match the format of the strings in password.txt
sub create{
	my @in = split('&',$in);
	my @value = split('=',$in[0]);
	my $user = $value[1];
	@value = split('=',$in[1]);
	my $password = $value[1];
	@value = split('=',$in[2]);
	my $checkpassword = $value[1];
	@value = split('=',$in[3]);
	my $email = $value[1];
	$email =~ s/\%40/\@/;
	@value = split('=',$in[4]);
	my $firstname = $value[1];
	@value = split('=',$in[5]);
	my $lastname = $value[1];

	our $boolean = 0;
	open(FH, "password.txt");
	my @file = <FH>;
	chomp(@file);
	foreach (@file){
		my @temp = split('=',$_);
		if ($temp[0] eq $user){
			$boolean = 1;
			last;
		}
	}
	
	if (($boolean == 0) && ($password eq $checkpassword)){
	    $dbh->do("INSERT INTO client VALUES(NULL, \"$user\", \"$firstname\", \"$lastname\", \"$email\")") or die("Couldn't add");
	    my $string = $user . "=" . md5_hex($password);		
	    open(FH, "password.txt");
	    my @file = <FH>;
	    push(@file,$string);
	    chomp(@file);
	    
	    # rewrite everything to the file
	    open FILE, ">password.txt";
	    foreach (@file){
		print FILE "$_\n";
	    }
	    close FILE;
	    
	    open ( MAIL, "| /usr/lib/sendmail -t" );
	    print MAIL "From: $email\n";
	    print MAIL "To: $email\n";
	    print MAIL "Subject: Welcome\n\n";
	    print MAIL "Welcome to the reservation service!";
	    close ( MAIL );
	    
	    $string = $ENV{REMOTE_ADDR} . " created a new account as user \"" . $user . "\" at " . localtime;
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
	    
	    $newuserdata = "newuser" . "\*" . $user . " " . $email . " " . $firstname . " " . $lastname;	
	    
	    print "<html><body><center>";
	    print "<font size=\"5\" face=\"trebuchet ms\" color=#9372ED>";
	    print "<body style=\"background-attachment: fixed; background-position: bottom right; background-repeat: no-repeat;\" background=\"purpleflower.jpg\" bgcolor=\"black\">";
	    print "Account successfully created!<br>";
	    print "<form action=\"login.pl.cgi\" method=POST>";
	    print "<input type=\"submit\" value=\"Login\" class=\"button\"></form>";
	    print "<style type=\"text/css\">";
	    print ".button {border: 1px solid #000000;background: #000000; color:#9372ED; font: bold large 'trebuchet ms',helvetica,sans-serif;}";
	    print ".button:hover {border: 1px solid #000000; background: #000000; color:#000000; font: bold large 'trebuchet ms',helvetica,sans-serif;}";
	    print ".input {border: 1px solid #9372ED; background: #9372ED;}";
	    print "</style></html></body></center>";
	    
	}
	elsif ($boolean == 1){
		print "<html><body><center>";
		print "<font size=\"5\" face=\"trebuchet ms\" color=#9372ED>";
		print "<body style=\"background-attachment: fixed; background-position: bottom right; background-repeat: no-repeat;\" background=\"purpleflower.jpg\" bgcolor=\"black\">";
		print "Sorry, that username is already taken!<br>";
		print "<form action=\"createAccount.pl.cgi\" method=POST>";
		print "<input type=\"submit\" value=\"New Account\" class=\"button\"></form>";
		print "<style type=\"text/css\">";
		print ".button {border: 1px solid #000000;background: #000000; color:#9372ED; font: bold large 'trebuchet ms',helvetica,sans-serif;}";
		print ".button:hover {border: 1px solid #000000; background: #000000; color:#000000; font: bold large 'trebuchet ms',helvetica,sans-serif;}";
		print "</style></html></body></center>";
	}
	else{
		print "<html><body><center>";
		print "<font size=\"5\" face=\"trebuchet ms\" color=#9372ED>";
		print "<body style=\"background-attachment: fixed; background-position: bottom right; background-repeat: no-repeat;\" background=\"purpleflower.jpg\" bgcolor=\"black\">";
		print "Sorry, the passwords didn't match!<br>";
		print "<form action=\"createAccount.pl.cgi\" method=POST>";
		print "<input type=\"submit\" value=\"New Account\" class=\"button\"></form>";
		print "<style type=\"text/css\">";
		print ".button {border: 1px solid #000000;background: #000000; color:#9372ED; font: bold large 'trebuchet ms',helvetica,sans-serif;}";
		print ".button:hover {border: 1px solid #000000; background: #000000; color:#000000; font: bold large 'trebuchet ms',helvetica,sans-serif;}";
		print "</style></html></body></center>";
	}
}