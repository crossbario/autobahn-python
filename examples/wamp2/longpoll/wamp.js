function httppost(url, data) {
   var d = $.Deferred();
   var req = new XMLHttpRequest();

   req.onreadystatechange = function (evt) {

      console.log("onreadystatechange", evt, req.readyState);

      console.log(req.readyState);
      console.log(req.response);
      console.log(req.responseText);
      console.log(req.responseType);

      if (req.readyState === 4) {

         if (req.status === 200) {
            var msg = JSON.parse(req.response);
            d.resolve(msg);

         } if (req.status === 204) {
            d.resolve();

         } else {
            //d.reject(req.status, req.statusText);
         }

      }
   }

   req.open("POST", url, true);
   req.setRequestHeader("Content-type", "application/json; charset=utf-8");
/*   
   req.timeout = 500;
   req.ontimeout = function () {
      d.reject(500, "Request Timeout");
   }
*/
   if (data !== undefined) {
      req.send(JSON.stringify(data));
   } else {
      req.send();
   }

   return d;
}

function session(url, onopen, onclose) {

}