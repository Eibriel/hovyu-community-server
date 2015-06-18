[out:json];
node (-57, -74, -21.21, -53.272)
    ["place"]
    ["place"!="country"]
    ["place"!="state"];
out body;

[out:json];
node
	["place"]
	["is_in:country"="Argentina"];
out body;
