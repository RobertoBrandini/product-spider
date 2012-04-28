<?php

# getURL Example
//getURL("http://shop.ebay.com/allcategories/all-categories", "proxy.tre-se.gov.br:3128");

//getURL("http://www.extra.com.br/Informatica/Notebook/?Filtro=C56_C57&paginaAtual=1&numPorPagina=400", null);

function getURL($targetUrl, $proxy = null) {
	$userAgent = 'Googlebot/2.1 (http://www.googlebot.com/bot.html)';

	$ch = curl_init();
	if ($proxy != null)
		curl_setopt($ch, CURLOPT_PROXY, $proxy);
//        curl_setopt($ch, CURLOPT_PROXY, "proxy.tre-se.gov.br:3128");
	curl_setopt($ch, CURLOPT_USERAGENT, $userAgent);
	curl_setopt($ch, CURLOPT_URL, $targetUrl);
	curl_setopt($ch, CURLOPT_FAILONERROR, true);
	curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);
	curl_setopt($ch, CURLOPT_AUTOREFERER, true);
	curl_setopt($ch, CURLOPT_RETURNTRANSFER,true);
	curl_setopt($ch, CURLOPT_TIMEOUT, 50);
	
	$html = curl_exec($ch);

	if (!$html) {
		echo "<br />cURL error number:" . curl_errno($ch);
		echo "<br />cURL error:" . curl_error($ch);
		exit;
	} else {
		echo $html;
	}
}

echo getURL("http://www.extra.com.br/Informatica/Notebook/?Filtro=C56_C57&paginaAtual=1&numPorPagina=400", null)

?>