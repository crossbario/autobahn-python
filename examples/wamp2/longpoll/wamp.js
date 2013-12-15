function httppost(url, data) {
   var d = $.Deferred();
   var req = new XMLHttpRequest();

   req.onreadystatechange = function (evt) {

      console.log("onreadystatechange", evt, req.readyState);

      console.log(req.readyState);
      console.log(req.response);
      console.log(req.responseText);
      //console.log(req.status);
      console.log(req.responseType);

      if (req.readyState === 4) {

         if (req.status === 200) {
            d.resolve(req.response);
         } else {
            //d.reject(req.status, req.statusText);
         }

      }
   }

   req.open("POST", url, true);
   req.setRequestHeader("Content-type", "application/json; charset=utf-8");
   req.timeout = 500;

   req.ontimeout = function () {
      d.reject(500, "Request Timeout");
   }

   req.send(JSON.stringify(data));

   return d;
}