###############################################################################
##
##  Copyright 2011 Tavendo GmbH
##
##  Licensed under the Apache License, Version 2.0 (the "License");
##  you may not use this file except in compliance with the License.
##  You may obtain a copy of the License at
##
##      http://www.apache.org/licenses/LICENSE-2.0
##
##  Unless required by applicable law or agreed to in writing, software
##  distributed under the License is distributed on an "AS IS" BASIS,
##  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
##  See the License for the specific language governing permissions and
##  limitations under the License.
##
###############################################################################

## CSS common for all reports
##
CSS_COMMON = """
body {
   background-color: #F4F4F4;
   color: #333;
   font-family: Segoe UI,Tahoma,Arial,Verdana,sans-serif;
}

p#intro {
   font-family: Cambria,serif;
   font-size: 1.1em;
   color: #444;
}

p#intro a {
   color: #444;
}

p#intro a:visited {
   color: #444;
}

.block {
   background-color: #e0e0e0;
   padding: 16px;
   margin: 20px;
}

p.case_text_block {
   border-radius: 10px;
   border: 1px solid #aaa;
   padding: 16px;
   margin: 4px 20px;
   color: #444;
}

p.case_desc {
}

p.case_expect {
}

p.case_outcome {
}

p.case_closing_beh {
}

pre.http_dump {
   font-family: Consolas, "Courier New", monospace;
   font-size: 0.8em;
   color: #333;
   border-radius: 10px;
   border: 1px solid #aaa;
   padding: 16px;
   margin: 4px 20px;
}

span.case_pickle {
   font-family: Consolas, "Courier New", monospace;
   font-size: 0.7em;
   color: #000;
}

p#case_result,p#close_result {
   border-radius: 10px;
   background-color: #e8e2d1;
   padding: 20px;
   margin: 20px;
}

h1 {
   margin-left: 60px;
}

h2 {
   margin-left: 30px;
}

h3 {
   margin-left: 50px;
}

a.up {
   float: right;
   border-radius: 16px;
   margin-top: 16px;
   margin-bottom: 10px;

   margin-right: 30px;
   padding-left: 10px;
   padding-right: 10px;
   padding-bottom: 2px;
   padding-top: 2px;
   background-color: #666;
   color: #fff;
   text-decoration: none;
   font-size: 0.8em;
}

a.up:visited {
}

a.up:hover {
   background-color: #028ec9;
}
"""

## CSS for Master report
##
CSS_MASTER_REPORT = """
table {
   border-collapse: collapse;
   border-spacing: 0px;
}

td {
   margin: 0;
   border: 1px solid #fff;
   padding-top: 6px;
   padding-bottom: 6px;
   padding-left: 16px;
   padding-right: 16px;
   font-size: 0.9em;
   color: #fff;
}

table#agent_case_results {
   border-collapse: collapse;
   border-spacing: 0px;
   border-radius: 10px;
   margin-left: 20px;
   margin-right: 20px;
   margin-bottom: 40px;
}

td.outcome_desc {
   width: 100%;
   color: #333;
   font-size: 0.8em;
}

tr.agent_case_result_row a {
   color: #eee;
}

td.agent {
   color: #fff;
   font-size: 1.0em;
   text-align: center;
   background-color: #048;
   font-size: 0.8em;
   word-wrap: break-word;
   padding: 4px;
   width: 140px;
}

td.case {
   background-color: #666;
   text-align: left;
   padding-left: 40px;
   font-size: 0.9em;
}

td.case_category {
   color: #fff;
   background-color: #000;
   text-align: left;
   padding-left: 20px;
   font-size: 1.0em;
}

td.case_subcategory {
   color: #fff;
   background-color: #333;
   text-align: left;
   padding-left: 30px;
   font-size: 0.9em;
}

td.close {
   width: 15px;
   padding: 6px;
   font-size: 0.7em;
   color: #fff;
   min-width: 0px;
}

td.case_ok {
   background-color: #0a0;
   text-align: center;
}

td.case_almost {
   background-color: #6d6;
   text-align: center;
}

td.case_non_strict, td.case_no_close {
   background-color: #9a0;
   text-align: center;
}

td.case_info {
   background-color: #4095BF;
   text-align: center;
}

td.case_failed {
   background-color: #900;
   text-align: center;
}

td.case_missing {
   color: #fff;
   background-color: #a05a2c;
   text-align: center;
}

span.case_duration {
   font-size: 0.7em;
   color: #fff;
}

*.unselectable {
   user-select: none;
   -moz-user-select: -moz-none;
   -webkit-user-select: none;
   -khtml-user-select: none;
}

div#toggle_button {
   position: fixed;
   bottom: 10px;
   right: 10px;
   background-color: rgba(60, 60, 60, 0.5);
   border-radius: 12px;
   color: #fff;
   font-size: 0.7em;
   padding: 5px 10px;
}

div#toggle_button:hover {
   background-color: #028ec9;
}
"""

## CSS for Agent/Case detail report
##
CSS_DETAIL_REPORT = """
p.case {
   color: #fff;
   border-radius: 10px;
   padding: 20px;
   margin: 12px 20px;
   font-size: 1.2em;
}

p.case_ok {
   background-color: #0a0;
}

p.case_non_strict, p.case_no_close {
   background-color: #9a0;
}

p.case_info {
   background-color: #4095BF;
}

p.case_failed {
   background-color: #900;
}

table {
   border-collapse: collapse;
   border-spacing: 0px;
   margin-left: 80px;
   margin-bottom: 12px;
   margin-top: 0px;
}

td
{
   margin: 0;
   font-size: 0.8em;
   border: 1px #fff solid;
   padding-top: 6px;
   padding-bottom: 6px;
   padding-left: 16px;
   padding-right: 16px;
   text-align: right;
}

td.right {
   text-align: right;
}

td.left {
   text-align: left;
}

tr.stats_header {
   color: #eee;
   background-color: #000;
}

tr.stats_row {
   color: #000;
   background-color: #fc3;
}

tr.stats_total {
   color: #fff;
   background-color: #888;
}

div#wirelog {
   margin-top: 20px;
   margin-bottom: 80px;
}

pre.wirelog_rx_octets {color: #aaa; margin: 0; background-color: #060; padding: 2px;}
pre.wirelog_tx_octets {color: #aaa; margin: 0; background-color: #600; padding: 2px;}
pre.wirelog_tx_octets_sync {color: #aaa; margin: 0; background-color: #606; padding: 2px;}

pre.wirelog_rx_frame {color: #fff; margin: 0; background-color: #0a0; padding: 2px;}
pre.wirelog_tx_frame {color: #fff; margin: 0; background-color: #a00; padding: 2px;}
pre.wirelog_tx_frame_sync {color: #fff; margin: 0; background-color: #a0a; padding: 2px;}

pre.wirelog_delay {color: #fff; margin: 0; background-color: #000; padding: 2px;}
pre.wirelog_kill_after {color: #fff; margin: 0; background-color: #000; padding: 2px;}

pre.wirelog_tcp_closed_by_me {color: #fff; margin: 0; background-color: #008; padding: 2px;}
pre.wirelog_tcp_closed_by_peer {color: #fff; margin: 0; background-color: #000; padding: 2px;}
"""

## JavaScript for master report
##
## Template vars:
##    agents_cnt => int => len(self.agents.keys())
##
JS_MASTER_REPORT = """
var isClosed = false;

function closeHelper(display,colspan) {
   // hide all close codes
   var a = document.getElementsByClassName("close_hide");
   for (var i in a) {
      if (a[i].style) {
         a[i].style.display = display;
      }
   }

   // set colspans
   var a = document.getElementsByClassName("close_flex");
   for (var i in a) {
      a[i].colSpan = colspan;
   }

   var a = document.getElementsByClassName("case_subcategory");
   for (var i in a) {
      a[i].colSpan = %(agents_cnt)d * colspan + 1;
   }
}

function toggleClose() {
   if (window.isClosed == false) {
      closeHelper("none",1);
      window.isClosed = true;
   } else {
      closeHelper("table-cell",2);
      window.isClosed = false;
   }
}
"""
