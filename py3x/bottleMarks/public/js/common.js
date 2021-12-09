var search_submission = 6;
var stateOfBlur = 0;
var searchLayerSwitch = 0;

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
        document.cookie = name+"="+value+expires+"; path=/";
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
                return unescape( document.cookie.substring( len, end ) );

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
       //parent.top.document.getElementById('searchTerms').innerHTML = searchTerms.value;
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
	eraseCookie("PYwmSessionID");
	eraseCookie("PYwmUserID");
	eraseCookie("Counter");
	eraseCookie("dt_cnter");
	eraseCookie("tab_state");
	eraseCookie("searchTerms");
	eraseCookie("search_submission");

	// vendor specific general Mojo cookie
	eraseCookie("mojolicious");
	// vendor specific general Mojo cookie	
	top.location = "/logout";
}

function goLink(title,bk_id)
{

  var checkRadio = document.querySelector('input[name="modlink"]:checked'); 

  if (checkRadio != null) { 
     switch(checkRadio.value) {
		case 'UPD' :
        checkRadio.checked = false;
        //displayUpdateLaye(url,title,bk_id)
        displayUpdateLayer(title,bk_id)
		break;
		case 'DEL' :
        checkRadio.checked = false;
        //displayDelLayer(url,title,bk_id)
        displayDelLayer(title,bk_id)
		break;
        default:
     }
     //checkRadio.checked = false;
  } else {
     var url =  Array .from(document.querySelectorAll('td.title_cell')) .find(el => el.textContent.trim() === title).nextSibling.nextSibling.textContent 
     window.open(url, "_blank"); 
 }

}

function displayUpdateLayer(title,bk_id)
{
     //layerUpdate
     var lU = document.getElementById("updateL");

	 lU.style.overflow = 'auto';
     lU.style.display = 'block';

	 var titleSet = lU.querySelector('input[name="title_update"]')
	 var urlSet = lU.querySelector('textarea[name="url_update"]')
	 var bk_idSet = lU.querySelector('input[name="bk_id"]')

     titleSet.value = title;
     bk_idSet.value = bk_id

     urlSet.value =  Array .from(document.querySelectorAll('td.title_cell')) .find(el => el.textContent.trim() === title).nextSibling.nextSibling.textContent 

     Array.from(document.querySelectorAll('td.title_cell'))
      .find(el => el.textContent.trim() === title)
      .style.border = "solid";


}

function displayDelLayer(title,bk_id)
{
   var delL = document.getElementById("delL")
   delL.style.display = 'block'

   var bk_idSet = delL.querySelector('input[name="bk_id"]')
   bk_idSet.value = bk_id

//   alert("BKID " + bk_id)
   var spDel = delL.getElementsByTagName('p')[0]
   spDel.innerHTML = title; 

}

function closeLayer2(layer,del)
{
   var ll = document.getElementById(layer)
   ll.style.display = 'none'; 
   var title = ll.querySelector('input[name="title_update"]')
   if (title == null)
      title =  document.getElementById('spDel').innerHTML
   else
      title = title.value
  
   Array.from(document.querySelectorAll('td.title_cell'))
    .find(el => el.textContent.trim() === title)
    .style.border = "none";
   
   if(del == "YES")
     window.document.formDelete.submit()

}

function closeLayerUpdate(layer)
{
   lU = document.getElementById(layer)
   lU.style.display = 'none'; 
   window.document.formUpdate.submit()

}


function swapSearchLayer()
{
    if (searchLayerSwitch++ % 2) 
    {
     document.getElementById("selDates").style.display = 'none';
     document.getElementById("selUpdates").style.display = 'inline-block';
     document.getElementById("selMods").style.backgroundColor = 'yellow';
    }
    else
    {
     document.getElementById("selDates").style.display = 'inline-block';
     document.getElementById("selUpdates").style.display = 'none';
     document.getElementById("selMods").style.backgroundColor = 'green';
    }
}
