import os
import hashlib
import requests

Known_Schemas = [
    "www.loc.gov/standards/alto/alto-v2.0.xsd",
    "www.loc.gov/standards/alto/v4/alto-4-0.xsd",
    "www.loc.gov/standards/alto/v4/alto-4-1.xsd",
    "www.loc.gov/standards/alto/v4/alto-4-2.xsd",
    "www.loc.gov/standards/alto/v4/alto-4-3.xsd",
    #"schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15/pagecontent.xsd",
    "schema.primaresearch.org/PAGE/gts/pagecontent/2016-07-15/pagecontent.xsd",
    "schema.primaresearch.org/PAGE/gts/pagecontent/2017-07-15/pagecontent.xsd",
    "schema.primaresearch.org/PAGE/gts/pagecontent/2018-07-15/pagecontent.xsd",
    "schema.primaresearch.org/PAGE/gts/pagecontent/2019-07-15/pagecontent.xsd"
]

here = os.path.dirname(__file__)
for xsd_path in Known_Schemas:
    new_path = os.path.join(here, "htrvx", "schemas", f"{hashlib.sha256(xsd_path.encode()).hexdigest()}.xsd")
    text = requests.get(f"http://{xsd_path}").text
    with open(new_path, "w") as f:
        f.write(text)
