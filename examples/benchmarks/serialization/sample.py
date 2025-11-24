###############################################################################
#
# The MIT License (MIT)
#
# Copyright (c) typedef int GmbH
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
###############################################################################

"""
Sample JSON data structures for payload size variation in serialization benchmarks.

These structures are used to create different payload sizes:
- SMALL: Base vehicle telemetry only
- MEDIUM: Base + JSON_DATA1
- LARGE: Base + JSON_DATA1 + JSON_DATA2 + JSON_DATA3
- XL: SMALL + 16KB binary frame
- XXL: SMALL + 128KB binary frame
"""

from typing import Any, Dict, List

__all__ = ["JSON_DATA1", "JSON_DATA2", "JSON_DATA3"]


JSON_DATA1: Dict[str, Any] = {
    "data": [
        {
            "attributes": {
                "body": "The shortest article. Ever.",
                "created": "2015-05-22T14:56:29.000Z",
                "title": "JSON:API paints my bikeshed!",
                "updated": "2015-05-22T14:56:28.000Z",
            },
            "id": "1",
            "relationships": {"author": {"data": {"id": "42", "type": "people"}}},
            "type": "articles",
        }
    ],
    "included": [
        {
            "attributes": {"age": 80, "gender": "male", "name": "John"},
            "id": "42",
            "type": "people",
        }
    ],
    "widget": {
        "debug": "on",
        "image": {
            "alignment": "center",
            "hOffset": 250,
            "name": "sun1",
            "src": "Images/Sun.png",
            "vOffset": 250,
        },
        "text": {
            "alignment": "center",
            "data": "Click Here",
            "hOffset": 250,
            "name": "text1",
            "onMouseUp": "sun1.opacity = (sun1.opacity / 100) * 90;",
            "size": 36,
            "style": "bold",
            "vOffset": 100,
        },
        "window": {
            "height": 500,
            "name": "main_window",
            "title": "Sample Konfabulator Widget",
            "width": 500,
        },
    },
}


JSON_DATA2: Dict[str, List[Dict[str, Any]]] = {
    "actors": [
        {
            "name": "Tom Cruise",
            "age": 56,
            "Born At": "Syracuse, NY",
            "Birthdate": "July 3, 1962",
            "photo": "https://jsonformatter.org/img/tom-cruise.jpg",
            "wife": None,
            "weight": 67.5,
            "hasChildren": True,
            "hasGreyHair": False,
            "children": ["Suri", "Isabella Jane", "Connor"],
        },
        {
            "name": "Robert Downey Jr.",
            "age": 53,
            "Born At": "New York City, NY",
            "Birthdate": "April 4, 1965",
            "photo": "https://jsonformatter.org/img/Robert-Downey-Jr.jpg",
            "wife": "Susan Downey",
            "weight": 77.1,
            "hasChildren": True,
            "hasGreyHair": False,
            "children": ["Indio Falconer", "Avri Roel", "Exton Elias"],
        },
    ]
}


JSON_DATA3: Dict[str, List[Dict[str, Any]]] = {
    "nested": [
        {
            "id": "0001",
            "type": "donut",
            "name": "Cake",
            "ppu": 0.55,
            "batters": {
                "batter": [
                    {"id": "1001", "type": "Regular"},
                    {"id": "1002", "type": "Chocolate"},
                    {"id": "1003", "type": "Blueberry"},
                    {"id": "1004", "type": "Devil's Food"},
                ]
            },
            "topping": [
                {"id": "5001", "type": "None"},
                {"id": "5002", "type": "Glazed"},
                {"id": "5005", "type": "Sugar"},
                {"id": "5007", "type": "Powdered Sugar"},
                {"id": "5006", "type": "Chocolate with Sprinkles"},
                {"id": "5003", "type": "Chocolate"},
                {"id": "5004", "type": "Maple"},
            ],
        },
        {
            "id": "0002",
            "type": "donut",
            "name": "Raised",
            "ppu": 0.55,
            "batters": {"batter": [{"id": "1001", "type": "Regular"}]},
            "topping": [
                {"id": "5001", "type": "None"},
                {"id": "5002", "type": "Glazed"},
                {"id": "5005", "type": "Sugar"},
                {"id": "5003", "type": "Chocolate"},
                {"id": "5004", "type": "Maple"},
            ],
        },
        {
            "id": "0003",
            "type": "donut",
            "name": "Old Fashioned",
            "ppu": 0.55,
            "batters": {
                "batter": [
                    {"id": "1001", "type": "Regular"},
                    {"id": "1002", "type": "Chocolate"},
                ]
            },
            "topping": [
                {"id": "5001", "type": "None"},
                {"id": "5002", "type": "Glazed"},
                {"id": "5003", "type": "Chocolate"},
                {"id": "5004", "type": "Maple"},
            ],
        },
    ]
}
