#!/usr/bin/perl
use Fcntl; #The Module
use Digest::MD5 qw(md5 md5_hex md5_base64);

print "content-type: text/html \n\n";

# read whatever was passed through the POST method
read(STDIN, my $in, $ENV{CONTENT_LENGTH});

if ($ENV{CONTENT_LENGTH} == 0 && $ENV{QUERY_STRING} eq ""){
	&start;
}
else{
	my @in = split('&',$in);
	my @value = split('=',$in[0]);
	my $command = $value[0];

	if ($command eq "user"){
		our $user = $value[1];
		&changePassForm;	
	}
	elsif ($command eq "username"){
		&checkValidUser;
	}
	elsif ($command eq "useremail"){
		&emailTempPass($value[1]);
	}
	elsif ($command eq "oldPass"){
		&checkpass;
	}
	else{
		print "ERROR: $in";
	}
}

sub checkpass{
	my @in = split('&',$in);
	my @value = split('=', $in[0]);
	my $oldpass = $value[1];
	@value = split('=', $in[1]);
	my $newpass = $value[1];
	@value = split('=', $in[2]);
	my $checknewpass = $value[1];
	@value = split('=', $in[3]);
	my $user = $value[1];
	chomp($user);
	chomp($oldpass);
	my $string = $user . "=" . md5_hex($oldpass);	
	my $newstring = $user . "=" . md5_hex($newpass);	

	our $boolean = 0;
	open(FH, "password.txt");
	my @file = <FH>;
	chomp(@file);

	foreach (@file){
		if ($_ eq $string){
			$_ = $newstring;
			$boolean = 1;
			last;
		}
	}

	if (($boolean == 1) && ($newpass eq $checknewpass)){
		chomp(@file);

		open FILE, ">password.txt";
		foreach (@file){
			print FILE "$_\n";
		}
		close FILE;


		my $string = $ENV{REMOTE_ADDR} . " reset their password as user \"" . $user . "\" at " . localtime;
		&log($string);

		print "<html><body><center>Password changed!";
		print "<form action=\"login.pl.cgi\" method=POST>";
		print "<input type=\"submit\" value=\"Login\"></form>";
		print "</html></body></center>";
	}
	elsif ($boolean == 0){
		print "<html><body><center>Sorry, incorrect password!";
		print "<form action=\"resetPassword.pl.cgi\" method=POST>";
		print "<input type=\"hidden\" value=$user name=\"user\">";
		print "<input type=\"submit\" name=\"changepass\" value=\"Back\"></form>";
		print "</html></body></center>";
	}
	else{
		print "<html><body><center>Sorry, passwords did not match!";
		print "<form action=\"resetPassword.pl.cgi\" method=POST>";
		print "<input type=\"hidden\" value=$user name=\"user\">";
		print "<input type=\"submit\" name=\"changepass\" value=\"Back\"></form>";
		print "</html></body></center>";	
	}
}

sub start{
	print "<html><body><center>";
	print "<form action=\"resetPassword.pl.cgi\" method=POST>Username: ";
	print "<input type=\"text\" name=\"username\"><br><br>";
	print "<input type=\"hidden\" value=$user name=\"user\">";
	print "<input type=\"submit\" value=\"Submit\"></form>";
	print "</html></body></center>";
}

sub checkValidUser{
	my @in = split('&',$in);
	my @value = split('=',$in[0]);
	my $user = $value[1];
	@value = split('=',$in[1]);
	my $temppass = &randomString;
	open(FH, "password.txt");
	my @file = <FH>;
	chomp(@file);
	
	my $boolean = -1;
	foreach (@file){
		if ($_ =~ m/$user\=/){
			$boolean = 1;
			$_ = $user . "=" . md5_hex($temppass);	
			last;
		}
		else {
			$boolean = 0;
		}
	}
	close FILE;

	open FILE, ">password.txt";
	foreach (@file){
		print FILE "$_\n";
	}
	close FILE;

	if ($boolean == 1){
		my $s = $user . "=" . md5_hex($temppass);
		print "<html><body><center>";
		print "<form  name=\"MyForm\" method=POST action=\"clienttest.pl.cgi\">";
		print "<input type=\"hidden\" name=\"user\" value=\"$user\">";
		print "<input type=\"hidden\" value=\"$temppass\" name=\"user\"></form>";
		print "<script type=\"text/javascript\" language=\"JavaScript\"><!--
		document.MyForm.submit();
		//--></script>";
		print "</center></body></html>";
	}	
	else{
		print "<html><body><center>User not found!";
		print "<form name=\"MyForm\" method=GET action=\"home.pl.cgi\">";
		print "<input type=\"hidden\" name=\"user\" value=\"$user\">";
		print "<input type=\"hidden\" name=\"user\" value=\"$user\">";
		print "<input type=\"submit\" value=\"Home\"></form>";
		print "</html></body></center>";
	}
}

sub emailTempPass{
	my $e = shift;
	@e = split('\*',$e);
	my $email = $e[1];
	$email =~ s/%40/\@/;	
	@e = split('\%3D', $in);
	$temppass = $e[2];
	$e[1] =~ s/%26user//;	
	$user = $e[1];

	open ( MAIL, "| /usr/lib/sendmail -t" );
	print MAIL "From: $email\n";
	print MAIL "To: $email\n";
	print MAIL "Subject: Password Recovery\n\n";
	print MAIL "Your username is $user and your new password is $temppass\nLog back in here to change your password: http://web3157.cs.columbia.edu/~jm3542/cs3157/project1/login.pl.cgi";
	close ( MAIL );

	my $string = $ENV{REMOTE_ADDR} . " requested a password reset as user \"" . $user . "\" at " . localtime;
	&log($string);

	print "<html><body><center>New password sent to email!";
	print "<form action=\"login.pl.cgi\" method=POST>";
	print "<input type=\"submit\" value=\"Login\"></form>";
	print "</html></body></center>";
}


sub changePassForm{
	print "<html><body><center>";
	print "<form action=\"resetPassword.pl.cgi\" method=POST>Old Password: ";
	print "<input type=\"password\" name=\"oldPass\"><br><br>New Password: ";
	print "<input type=\"password\" name=\"newPass\"><br><br>Confirm New Password: ";
	print "<input type=\"password\" name=\"newPass1\"><br><br>";
	print "<input type=\"hidden\" value=$user name=\"user\">";
	print "<input type=\"submit\" value=\"Submit\"></form>";
	print "</html></body></center>";
}

sub randomString{
	my @c = qw(q w e r t y u i o p a s d f g h j k l z x c v b n m 1 2 3 4 5 6 7 8 9 0);
	my $s = "";
	for (my $count = 0; $count < 6; $count++) {
 		my $index = int(rand(36));
		$s .= $c[$index];
	}
	return $s;
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