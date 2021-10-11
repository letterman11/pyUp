//appending "PY" to some cookies to differentiate from perl webMarks
// may cause some irregularities between share platform  of perl and python webMarks
var search_submission = 6;	
var stateOfBlur = 0;

var startDate = parent.top.document.getElementById("searchDateStart")
var endDate = parent.top.document.getElementById("searchDateEnd")

function init()
{
  var startDate = parent.top.document.getElementById("searchDateStart")
  var endDate = parent.top.document.getElementById("searchDateEnd")

}


function blurDates()
{
	var startDate = parent.top.document.getElementById("searchDateStart")
	var endDate = parent.top.document.getElementById("searchDateEnd")
	if(!stateOfBlur) {
	startDate.value = "";
	endDate.value = "";
	stateOfBlur=1;

	}
}


function setCookie(name,value,days)
{
        if (days) {
                var date = new Date();
                date.setTime(date.getTime()+(days*24*60*60*1000));
                var expires = "; expires="+date.toGMTString();
        }
        else var expires = "";
        //document.cookie = name+"="+value+expires+"; path=/";
        document.cookie = name+"="+encodeURIComponent(value)+expires+"; path=/";
}

function getCookie(name,path)
{
        var start = document.cookie.indexOf( name + "=" );
        var len = start + name.length + 1;

        if ( ( !start ) && ( name != document.cookie.substring( 0, name.length ) ) ) {
                return null;
        }

        if ( start == -1 ) return null;
                var end = document.cookie.indexOf( ";", len );
        if ( end == -1 ) end = document.cookie.length;
				//return unescape( document.cookie.substring( len, end ) );
                return decodeURIComponent(document.cookie.substring( len, end ) );

}


function eraseCookie(name)
{
        setCookie(name,"",-1);
}

function cgi_out(tab_parm)
{
	var sort_asc = 0;
	var sort_desc = 1;
	var sort_date_asc = 2;
	var sort_date_desc = 3;
	var sort_date_indicator = 11;	
	var sortCrit; 
	var counter;
	var prevTab;
	var date_flag;
	var currTab;

	prevTab = parseInt(getCookie('tab'));	
	counter = parseInt(getCookie('Counter'));	
	date_flag = parseInt(getCookie('date_flag'));

	currTab = tab_parm.substr(4,2);

	if(currTab == sort_date_indicator && date_flag == 1) {
	//	alert("A")
		sortCrit = sort_date_desc
		eraseCookie("date_flag")
		tab_parm = "tab=" + prevTab
		
	} 
	else if(currTab == sort_date_indicator) {
	//	alert("B")
		sortCrit = sort_date_asc	
		setCookie('date_flag',1)
		tab_parm = "tab=" + prevTab

	} else if(currTab != prevTab) {
	//	alert("C")
		sortCrit = sort_asc;
		setCookie('tab', currTab);
   		setCookie('Counter',1); 
	}
	else if (currTab == prevTab) {
	//	alert("D")
		sortCrit = (counter++ % 2) ? sort_desc : sort_asc;
		setCookie('Counter',counter)
	}


	//top.location = "/tabView?" + tab_parm + "&sortCrit=" + sortCrit;
	// deploy url##
	top.location = "/pyWebMarks/tabView?" + tab_parm + "&sortCrit=" + sortCrit;
	//	
}

function setSearchTerms()
{      
       var searchTerms = parent.top.document.getElementById('searchBxTitle');
       parent.top.document.getElementById('searchTerms').innerHTML = searchTerms.value;
       setCookie('searchTerms', searchTerms.value);
       setCookie('search_submission', search_submission);

	var startDate = parent.top.document.getElementById("searchDateStart")
	var endDate = parent.top.document.getElementById("searchDateEnd")

	if(stateOfBlur == 0) 
	{
		startDate.value="";
		endDate.value="";
	}
}

function validateFields(sDate,eDate)
{
	re_1 =	'/([0-9]{1,2})[-/]([0-9]{1,2})[-/]([0-9]{4})/';
	re_2 =	'/([0-9]{4})[-/]([0-9]{1,2})[-/]([0-9]{1,2})/';
/*
	if((re_1.test(sDate.value) || (re_2.test(sDate.value))
		return true;	

	if((re_1.test(eDate.value) || (re_2.test(eDate.value) || (eDate.value == "")))
		return true;	
*/
}


function getSearchTerms()
{      
       var searchTerms = getCookie('searchTerms');
       parent.top.document.getElementById('searchTerms').innerHTML = searchTerms;

}

function topOpToSearch(topOp)
{      
   var searchBox = parent.top.document.getElementById('searchBxTitle');
   searchBox.value = topOp; 
}



function logOut()
{
	//appending "PY" to some cookie parameters to differentiate from regular webMarks perl
	eraseCookie("PYwmSessionID");
	eraseCookie("PYwmUserName");
	eraseCookie("PYwmUserID");
	eraseCookie("Counter");
	eraseCookie("dt_cnter");
	eraseCookie("tab_state");
	eraseCookie("tab");
	eraseCookie("searchTerms");
	eraseCookie("search_submission");
	
	//top.location = "/logout";
	// deploy url
	top.location = "/pyWebMarks/logout";
	//
}
