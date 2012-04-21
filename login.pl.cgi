#!/usr/bin/perl
use Fcntl; #The Module
use Digest::MD5 qw(md5 md5_hex md5_base64);
use CGI 'param';

print "content-type: text/html \n\n";

# read whatever was passed through the POST method
read(STDIN, my $in, $ENV{CONTENT_LENGTH});

if ($ENV{CONTENT_LENGTH} == 0 && $ENV{QUERY_STRING} eq ""){
    &generateLoginHTML;
}

# if there was something passed through the POST method only, then check the 
# username/password combination that was passed with the checkPassword subroutine
elsif ($ENV{CONTENT_LENGTH} > 0){
    &checkPassword;
}

# create a page that takes in user and password information and submits it through the POST method
sub generateLoginHTML{
    print "<html><body><center>";
    print "<form action=\"login.pl.cgi\" method=POST>User: ";
    print "<input type=\"text\" name=\"t1\"><br><br>Password: ";
    print "<input type=\"password\" name=\"t2\"><br><br>";
    print "<input type=\"submit\" value=\"Submit\"></form>";
    print "</form></html></body></center>";
}

# get the input submitted through the POST method and split it so that you get
# the corresponding user and password strings into respective variables and format
# it to match the format of the strings in password.txt
sub checkPassword{
    #$user = param('t1');
    #$password = param('t2');
    #print("User: ",$user," ", "Password: ",$password,"<br");
    my @in = split('&',$in);
    my @value = split('=',$in[0]);
    our $user = $value[1];
    @value = split('=',$in[1]);
    my $password = $value[1];
    my $string = $user . "=" . md5_hex($password);	

	# $boolean keeps track of whether or not there is a match
	our $boolean = -1;
	open(FH, "password.txt");
	my @file = <FH>;
	chomp(@file);

	# for each line in the file, check to see if there is a match;
	# if there is, break out of the loop
	foreach (@file){
		if ($_ eq $string){
			$boolean = 1;
			last;
		}
		else {
			$boolean = 0;
		}
	}

	# if there is no match, let the user know there was an error
	if ($boolean == 0){
		$string = $ENV{REMOTE_ADDR} . " attempt login fail as user \"" . $user . "\" at " . localtime;
		&log($string);
		print "<html><body><center>Invalid username/password combination";
		print "<form action=\"login.pl.cgi\" method=POST>";
		print "<input type=\"submit\" value=\"Login\"></form>";
		print "</html></body></center>";	
	}
	# if there is a match, direct them to the submitting URL form
	elsif ($boolean == 1){
		if ($user eq "admin"){
			$string = $ENV{REMOTE_ADDR} . " logged in as \"admin\" at " . localtime;
			&log($string);

		}
		else{
			$string = $ENV{REMOTE_ADDR} . " login success as user \"" . $user . "\" at " . localtime;
			&log($string);
		}


		print "<html><body><center>";
		print "<form name=\"MyForm\" method=POST action=\"home.pl.cgi\">";
		print "<input type=\"hidden\" name=\"user\" value=\"$user\">";
		print "<input type=\"hidden\" name=\"user\" value=\"$user\"></form>";
		print "<script type=\"text/javascript\" language=\"JavaScript\"><!--
		document.MyForm.submit();
		//--></script>";
		print "</center></body></html>";
	}

	# otherwise, something weird happened
	else{
	print "Something weird happened, perhaps password.txt does not exist?<BR>";
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
