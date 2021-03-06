var search_submission = 6;	

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
//	var sort_search_desc = 4;
//	var sort_search_asc = 5;
	var sort_date_indicator = 11;	
	var sort_crit; 
	var dt_cnter;
	var counter;
	var tab_state;
	var tab_var; 

	counter = parseInt(getCookie('Counter'));	
	dt_cnter = parseInt(getCookie('dt_cnter'));

/******************************************************/
	tab_state = getCookie('tab_state');
/******************************************************/
	tab_var = tab_parm.substr(4,2);
    
    if(search_submission == getCookie("search_submission"))
    {
	tab_parm = "tab=" +  search_submission;
	setCookie('tab_state',search_submission);	
   	eraseCookie("search_submission");
    }
    else if(tab_var == getCookie('tab_state'))
    {
	counter++;
	sort_crit = (counter % 2) ? sort_desc : sort_asc; 
	setCookie('Counter',counter);
    }
    else if(tab_var == sort_date_indicator)
    {
	tab_parm = "tab=" + tab_state; 

	if(dt_cnter == 0)
	{
		sort_crit = sort_date_desc;	
	}
	else
	{
		sort_crit = (dt_cnter % 2) ? sort_date_asc : sort_date_desc;
	}

	dt_cnter++;
	setCookie('tab_state',tab_state);	
	setCookie('dt_cnter',dt_cnter);
    } 
    else if(tab_var == getCookie('tab_state'))
    {
	counter++;
	sort_crit = (counter % 2) ? sort_desc : sort_asc; 
	setCookie('Counter',counter);
    } 
    else
    {
	setCookie('tab_state',tab_var);	
	setCookie('Counter',0);
	setCookie('dt_cnter',0);
	sort_crit = sort_asc;	
    }
	top.location = "/tabView?" + tab_parm + "&sortCrit=" + sort_crit;
}

function setSearchTerms()
{      
       var searchTerms = parent.top.document.getElementById('searchBx');
       //parent.top.document.getElementById('searchTerms').innerHTML = searchTerms.value;
       setCookie('searchTerms', searchTerms.value);
       setCookie('search_submission', search_submission);
}

function getSearchTerms()
{      
       var searchTerms = getCookie('searchTerms');
       parent.top.document.getElementById('searchTerms').innerHTML = searchTerms;
}

function topOpToSearch(topOp)
{      
   var searchBox = parent.top.document.getElementById('searchBx');
   searchBox.value = topOp; 
}


function logOut()
{
	eraseCookie("wmSessionID");
	eraseCookie("wmUserID");
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

function goLink(url,title,bk_id)
{

  var checkRadio = document.querySelector('input[name="modlink"]:checked'); 

  if (checkRadio != null) { 
     switch(checkRadio.value) {
		case 'UPD' :
        checkRadio.checked = false;
        displayUpdateLayer(url,title,bk_id)
		break;
		case 'DEL' :
        checkRadio.checked = false;
        displayDelLayer(url,title,bk_id)
		break;
        default:
     }
     //checkRadio.checked = false;
  } else {
    window.open(url, "_blank"); 
 }

}

function displayUpdateLayer(url,title,bk_id)
{
     //layerUpdate
     var lU = document.getElementById("updateL");
	 lU.style.overflow = 'auto';
     lU.style.display = 'block';
	 var titleSet = lU.querySelector('input[name="title_update"]')
	 var urlSet = lU.querySelector('textarea[name="url_update"]')
	 var bk_idSet = lU.querySelector('input[name="bk_id"]')
     titleSet.value = title;
     urlSet.value = url;	
     bk_idSet.value = bk_id

     Array.from(document.querySelectorAll('td.title_cell'))
      .find(el => el.textContent.trim() === title)
      .style.border = "solid";
}

function displayDelLayer(url,title,bk_id)
{
   var delL = document.getElementById("delL")
   delL.style.display = 'block'
   var bk_idSet = delL.querySelector('input[name="bk_id"]')
   bk_idSet.value = bk_id
   var spDel = delL.getElementsByTagName('p')[0]
   spDel.innerHTML = title; 

   Array.from(document.querySelectorAll('td.title_cell'))
    .find(el => el.textContent.trim() === title)
    .style.border = "solid";
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
