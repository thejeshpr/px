from django.shortcuts import render

def network_graph(request):
    graph_data = {
        "components": {
            {"id": "oci.aaa.vcn1", "type": "vcn", "details": "name:dummyvcn", "additional_info": {}},
            {"id": "oci.aaa.drg1", "type": "drg", "details": "name:dummydrg", "additional_info": {}},
            {"id": "oci.aaa.lpg1", "type": "lpg", "details": "name:dummylpg", "additional_info": {}},
            ...
        },
        "connections": [
            {"source": "oci.aaa.vcn1", "target": "oci.aaa.drg1", "label": "attachment_name"},
            {"source": "oci.aaa.vcn1", "target": "oci.aaa.lpg1", "label": "attachment_name"},
            ...
        ]
    }
    graph_data = {
        "components": [
            {"id": "compartment1", "type": "square", "details": "id:1234<br/>created by:user"},
            {"id": "compartment2", "type": "square"},
            {"id": "subnet1", "type": "diamond", "parent": "compartment1"},
            {"id": "subnet2", "type": "diamond", "parent": "compartment1"},
            {"id": "vcn1", "type": "circle"},
            {"id": "vcn2", "type": "circle"},
            {"id": "vcn3", "type": "circle"},
            {"id": "subnet3", "type": "diamond", "parent": "compartment2"},
            {"id": "subnet4", "type": "diamond", "parent": "compartment2"},
            {"id": "lb1", "type": "triangle", "parent": "compartment2"},
            {"id": "subnet5", "type": "diamond", "parent": "compartment2"},
            {"id": "subnet6", "type": "diamond", "parent": "compartment2"},

            {"id": "compartment3", "type": "square", "details": "id:4231"},
            {"id": "vcn31", "type": "circle"},
            {"id": "vcn32", "type": "circle"},
            {"id": "subnet31", "type": "diamond", "parent": "compartment3"},
            {"id": "subnet32", "type": "diamond", "parent": "compartment3"},
            {"id": "subnet33", "type": "diamond", "parent": "compartment3"},
            {"id": "subnet34", "type": "diamond", "parent": "compartment3"},
            {"id": "lb31", "type": "triangle"},

            {"id": "compartment4", "type": "square", "details": "id:4231"},
            {"id": "vcn41", "type": "circle"},
            {"id": "vcn42", "type": "circle"},
            {"id": "subnet41", "type": "diamond", "parent": "compartment3"},
            {"id": "subnet42", "type": "diamond", "parent": "compartment3"},
            {"id": "subnet43", "type": "diamond", "parent": "compartment3"},
            {"id": "subnet44", "type": "diamond", "parent": "compartment3"},
            {"id": "lb41", "type": "triangle"},
        ],
        "connections": [
            {"source": "compartment1", "target": "vcn1", "label": "vcns"},
            {"source": "compartment2", "target": "vcn2"},
            {"source": "compartment1", "target": "vcn3", "label": "vcns"},
            {"source": "vcn1", "target": "subnet1"},
            {"source": "vcn1", "target": "subnet2"},
            {"source": "vcn2", "target": "subnet3"},
            {"source": "vcn2", "target": "subnet4"},
            {"source": "subnet4", "target": "lb1"},
            {"source": "vcn3", "target": "subnet5"},
            {"source": "vcn2", "target": "subnet6"},

            {"source": "compartment3", "target": "vcn31"},
            {"source": "compartment3", "target": "vcn32"},
            {"source": "vcn31", "target": "subnet31"},
            {"source": "vcn31", "target": "subnet32"},
            {"source": "vcn32", "target": "subnet33"},
            {"source": "vcn32", "target": "subnet34"},
            {"source": "subnet31", "target": "lb31"},

            {"source": "compartment4", "target": "vcn41"},
            {"source": "compartment4", "target": "vcn42"},
            {"source": "vcn41", "target": "subnet41"},
            {"source": "vcn41", "target": "subnet42"},
            {"source": "vcn42", "target": "subnet43"},
            {"source": "vcn42", "target": "subnet44"},
            {"source": "subnet41", "target": "lb41"},

        ],
        "links": {
            "square": "https://www.google.com",
            "diamond": "https://www.github.com",
            "circle": "https://www.example.com"
        }
    }
    return render(request, "crawler/network_graph.html", {"graph_data": graph_data})