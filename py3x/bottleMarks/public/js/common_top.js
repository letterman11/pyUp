var search_submission = 6;
var stateOfBlur = 0;
var searchLayerSwitch = 0;
window.top.currTblCell;
var innerDoc;
window.top.rowCount = 0;
window.top.loadState = 0;
window.top.sameTab
window.top.init_tab = false;
window.top.cgi_out_exec = false;
var handle = parent.top.document;
window.top.bannerClicked;

function init()
{
	var startDate = parent.top.document.getElementById("searchDateStart")
	var endDate = parent.top.document.getElementById("searchDateEnd")

	innerFrame = top.document.getElementById('iframeTabTableResults');

	var bannerClicked = parseInt(getCookie("bannerClicked"));
	var rowsPerPage = parseInt(getCookie("rowsPerPage"));
	
	//if (!window.top.bannerClicked)
	//if (bannerClicked)
	innerFrame.src = "/pyWebMarks/tabTableView?&rowsPerPage=" + rowsPerPage;

    document.getElementById("selDates").style.display = 'inline-block';
    document.getElementById("selUpdates").style.display = 'none';
	
}



function modCheck(el)
{
//	alert(el)
		el.childNodes[1].checked = true;
}


function getCell(event)
{
	var tblCell = event.target;
	var tblCellUrl;
	
	//event.stopPropagation();
				
	var checkRadio = parent.document.querySelector('input[name="modlink"]:checked');
 
	if (tblCell.parentNode == '[object HTMLTableCellElement]')
	{
        tblCellUrl = tblCell;
		tblCell = tblCell.parentNode;
		window.top.currTblCell = tblCell;
	}

	window.top.currTblCell = tblCell;

	if (checkRadio)
	{
		event.preventDefault();
		var title = tblCell.textContent
		var url = tblCell.nextSibling.nextSibling.textContent

		if (checkRadio != null) { 
			switch(checkRadio.value) {
				case 'UPD' :
				checkRadio.checked = false;
				displayUpdateLayer(tblCell)
				break;
				case 'DEL' :
				checkRadio.checked = false;
				displayDelLayer(tblCell)
				break;
				default:
			}
		}
	}
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
        //document.cookie = name+"="+value+expires+"; path=/pyWebMarks";
        document.cookie = name+"="+encodeURIComponent(value)+expires+"; path=/pyWebMarks";
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

function bannerClick()
{	

	rowsPerPage = 	parent.top.document.search_form.rowsPerPage.value;
	setCookie("bannerClicked", "1")
	setCookie("rowsPerPage", rowsPerPage)

	window.location.replace ("/pyWebMarks?&rowsPerPage=" + rowsPerPage);
	
}

function jax_cgi_out(page,rowsPerPage,rowCount)
{
	top.document.getElementById("iframeTabTableResults").src = "/pyWebMarks/tabTableViewNav/" + page 
																				+ "/" + rowsPerPage ; 
	
	update_links(page,rowsPerPage,rowCount);

}

function update_links(page,rowsPerPage,rowCount)
{

	var div_pageLinkNavs = top.document.getElementById("pageLinkNavs");
	var html_links = "";
	
	var pageCnt =1;
	var currCnt = 1;
	
	html_links = "Pages: ";
	while (currCnt  < rowCount)
	{
		if (page == pageCnt)
			html_links += " <span style='font-size:16px; font-weight:bolder' id='curr_page'> " +  pageCnt + " </span>"
		else
			html_links += "<span> <A HREF='javascript:jax_cgi_out(" + pageCnt + " , " + rowsPerPage + "," + rowCount + " )'> " + pageCnt +  "</A> </span>"

		currCnt += rowsPerPage
		pageCnt +=1
	}

	div_pageLinkNavs.innerHTML = html_links;
	
}

function cgi_out_top(tab_parm)
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

    //added for first conditional to avoid error on server side
    //not an end
    var searchTab = 6; // added
    //add

	prevTab = parseInt(getCookie('tab'));	
	counter = parseInt(getCookie('Counter'));	
	date_flag = parseInt(getCookie('date_flag'));

	currTab = tab_parm.substr(4,2);

	window.top.init_tab = true;
	if (currTab != prevTab)
		window.top.sameTab = false;

	if(currTab == sort_date_indicator && date_flag == 1) {
	//	alert("A")
        sortCrit = sort_date_desc
        eraseCookie("date_flag")
        tab_parm = "tab=" + prevTab
        tab_parm = tab_parm ? tab_parm : searchTab
	    //alert( "tab " +tab_parm)	
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
		//*************************************
		window.top.sameTab = false;// take out
		//jax_cgi_out(1, window.top.rowCount);
		//*************************************
	}
	else if (currTab == prevTab) {
	//	alert("D")
		sortCrit = (counter++ % 2) ? sort_desc : sort_asc;
		setCookie('Counter',counter)
	}
	
    setSearchTerms();
    	
	var searchObj = packageSearchString();
	
	var rowsPerPage = handle.search_form.rowsPerPage.value;
//	alert("Inner rows per page " + rowsPerPage);
	
	window.top.rowCount = 0;
	window.top.cgi_out_exec = true;
	
	if (currTab == 6)
	{	
	    top.document.getElementById("iframeTabTableResults").src = "/pyWebMarks/tabTableView?" + tab_parm + 
						"&sortCrit=" + sortCrit + 
						"&rowsPerPage=" + encodeURIComponent(rowsPerPage) +
                        "&searchBoxTitle=" + encodeURIComponent(searchObj.searchBoxTitle) +
						"&searchBoxURL=" + encodeURIComponent(searchObj.searchBoxURL) +
						"&searchDateStart=" + encodeURIComponent(searchObj.searchStartDate) +
						"&searchDateEnd=" + encodeURIComponent(searchObj.searchEndDate) +
						"&searchtype=" + encodeURIComponent(searchObj.searchBoolType);
	}
	else
	{	
		top.document.getElementById("iframeTabTableResults").src = "/pyWebMarks/tabTableView?" + tab_parm + 
						"&rowsPerPage=" + encodeURIComponent(rowsPerPage) +
						"&sortCrit=" + sortCrit;
	}
	
	
}


function packageSearchString()
{
	var searchTermsTitle = parent.top.document.getElementById('searchBxTitle');
	var searchTermsURL = parent.top.document.getElementById('searchBxURL');

	var searchTermsBoolType  = parent.document.querySelector('input[name="searchtype"]:checked');

    //alert(searchTermsBoolType.value)

	var searchTermsStartDt = parent.top.document.getElementById('searchDateStart');
	var searchTermsEndDt = parent.top.document.getElementById('searchDateEnd');

	var searchObj = {
			searchBoxTitle: searchTermsTitle.value,
			searchBoolType: searchTermsBoolType.value,
			searchBoxURL: searchTermsURL.value,
			searchStartDate: searchTermsStartDt.value,
			searchEndDate: searchTermsEndDt.value,
	}

	return searchObj;
	
}

function setSearchTerms()
{      
       //var searchTermsTitle = parent.top.document.getElementById('searchBxTitle');
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
/*
	eraseCookie("rowsPerPage");
	eraseCookie("tab");
	eraseCookie("bannerClicked");
*/

	eraseCookie("wmSessionID");
	eraseCookie("wmUserName");
	eraseCookie("wmUserID");
	eraseCookie("Counter");
	eraseCookie("dt_cnter");
	eraseCookie("tab_state");
	eraseCookie("searchTerms");
	eraseCookie("search_submission");

	// vendor specific general Mojo cookie
	eraseCookie("mojolicious");
	// vendor specific general Mojo cookie	
//	top.location = "/logout";
	top.location = "/pyWebMarks/logout";
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

function displayUpdateLayer(tblCell)
{
     //layerUpdate
     var lU = parent.document.getElementById("updateL");

	 lU.style.overflow = 'auto';
     lU.style.display = 'block';

	 var titleSet = lU.querySelector('input[name="title_update"]')
	 var urlSet = lU.querySelector('textarea[name="url_update"]')
	 var bk_idSet = lU.querySelector('input[name="bk_id"]')

     titleSet.value = tblCell.textContent;
	 titleSet.value = titleSet.value.trim();
     urlSet.value = tblCell.nextSibling.nextSibling.textContent;
     urlSet.value =  urlSet.value.trim();  

     tblCell.style.border = 'solid';
		
	 var thTag = tblCell.parentNode.getElementsByTagName('th');
 
	 bk_idSet.value = thTag[0].textContent;
	 
 
}

function closeLayerUpdate(layer,update)
{
   lU = parent.document.getElementById(layer)
   lU.style.display = 'none'; 
   
   window.top.currTblCell.style.border = 'none';
   
   if(update == "YES")
	  window.document.formUpdate.submit()
	
	
}

function displayDelLayer(tblCell)
{
   var delL = parent.document.getElementById("delL")
   delL.style.display = 'block'

   var bk_idSet = delL.querySelector('input[name="bk_id"]')
   
   var thTag = tblCell.parentNode.getElementsByTagName('th');
   
	bk_idSet.value = thTag[0].textContent;

   var spDel = delL.getElementsByTagName('p')[0]
   spDel.innerHTML = tblCell.textContent; 

}

function closeLayerDel(layer,del)
{
   var ll = parent.document.getElementById(layer)
   ll.style.display = 'none'; 
   var title = ll.querySelector('input[name="title_update"]')
  
   window.top.currTblCell.style.border = 'none';
   
   if(del == "YES")
     window.document.formDelete.submit()

}


function swapSearchLayer()
{
 	
	if (searchLayerSwitch++ % 2) 
    {
     parent.document.getElementById("selDates").style.display = 'inline-block';
     parent.document.getElementById("selUpdates").style.display = 'none';
     parent.document.getElementById("selMods").style.backgroundColor = 'green';
     
    }
    else
    {
     parent.document.getElementById("selUpdates").style.display = 'inline-block';
     parent.document.getElementById("selMods").style.backgroundColor = 'yellow';
	 parent.document.getElementById("selDates").style.display = 'none';
    }
}