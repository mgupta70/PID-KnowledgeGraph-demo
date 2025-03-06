pidKG_schema = ''' Node properties:
- **Junction**
  - `alias`: STRING Example: "J55"
  - `tag`: STRING Example: "line_NN_513-line_NN_713"
  - `class`: INTEGER Min: -999, Max: -999
  - `center_x`: INTEGER Min: 643, Max: 5204
  - `center_y`: INTEGER Min: 798, Max: 3934
- **Symbol**
  - `alias`: STRING Example: "symbol_20"
  - `tag`: STRING Example: "OP-39294"
  - `class`: INTEGER Min: 1, Max: 32
  - `center_x`: INTEGER Min: 643, Max: 5216
  - `center_y`: INTEGER Min: 644, Max: 3979
Relationship properties:

The relationships:
(:Junction)-[:CONNECTED_TO]->(:Junction)
(:Junction)-[:CONNECTED_TO]->(:Symbol)
(:Symbol)-[:CONNECTED_TO]->(:Symbol)
(:Symbol)-[:CONNECTED_TO]->(:Junction)

Important Note - in graph, even though there are directions, the relationships are bidirectional.
'''

