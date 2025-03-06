examples = [
    {
        "question": "Count the symbols with class 16 that are directly linked to symbols with class 25",
        "query": """MATCH (s1:Symbol {{class: 16}})-[:CONNECTED_TO]-(s2:Symbol {{class: 25}}) RETURN COUNT(s1)"""
    },
    {
        "question": "What is the number of symbols with class 18 that have direct connections to symbols with class 4?",
        "query": "MATCH (s1:Symbol {{class: 18}})-[:CONNECTED_TO]-(s2:Symbol {{class: 4}}) RETURN COUNT(s1)"
    },
    {
        "question": "Count the number of 10 symbols that are directly connected to 18 symbols",
        "query": "MATCH (s1:Symbol {{class: 10}})-[:CONNECTED_TO]-(s2:Symbol {{class: 18}}) RETURN COUNT(s1)"
    }, 
    {
        "question":"How many items fall into the 18 classification?",
        "query": "MATCH (s:Symbol) WHERE s.class = 18 RETURN count(s)"
    },
    {
        "question":"Could you determine the total count of symbols of type 23?",
        "query": "MATCH (s:Symbol) WHERE s.class = 23 RETURN count(s)"
    },
    {
        "question":"What’s the number of entities in class 7?",
        "query": "MATCH (s:Symbol) WHERE s.class = 7 RETURN count(s)"
    },
    {
        "question":"Enumerate distinct symbols of class 32",
        "query": "MATCH (s:Symbol) WHERE s.class = 32 RETURN count(s)"
    },
    {
        "question":"Give the number of symbols listed under 11?",
        "query": "MATCH (s:Symbol) WHERE s.class = 11 RETURN count(s)"
    },
    {
        "question":"How many elements in class 21 are directly associated with elements in class 5?",
        "query": "MATCH (s1:Symbol)-[:CONNECTED_TO]-(s2:Symbol) WHERE s1.class = 21 AND s2.class = 5 RETURN COUNT(s1)"
    },
    {
        "question":"What’s the total number of 11 symbols connected to 7 symbols?",
        "query": "MATCH (s1:Symbol)-[:CONNECTED_TO]-(s2:Symbol) WHERE s1.class = 11 AND s2.class = 7 RETURN COUNT(s1)"
    },
    {
        "question":"How many entities belonging to 16 are linked directly to entities in 7?",
        "query": "MATCH (s1:Symbol)-[:CONNECTED_TO]-(s2:Symbol) WHERE s1.class = 16 AND s2.class = 7 RETURN COUNT(s1)"
    },
    {
        "question":"Can you provide the count of 31-class symbols connected directly to 28-class symbols?",
        "query": "MATCH (s1:Symbol)-[:CONNECTED_TO]-(s2:Symbol) WHERE s1.class = 31 AND s2.class = 28 RETURN COUNT(s1)"
    },
    {
        "question":"What’s the number of direct links between symbols of class 23 and class 5?",
        "query": "MATCH (s1:Symbol)-[:CONNECTED_TO]-(s2:Symbol) WHERE s1.class = 23 AND s2.class = 5 RETURN COUNT(s1)"
    },
    {
        "question":"Are there any symbols classified as 1 positioned between symbols of classes 2 and 3?",
        "query": "MATCH (s1:Symbol)-[:CONNECTED_TO]-(s2:Symbol)-[:CONNECTED_TO]-(s3:Symbol) WHERE s1.class = 2 AND s2.class = 1 AND s3.class = 7 RETURN COUNT(s2) > 0"
    },
    {
        "question":"Could you check if a symbol of class 8 serves as a link between class 19 and class 13?",
        "query": "MATCH (s1:Symbol)-[:CONNECTED_TO]-(s2:Symbol)-[:CONNECTED_TO]-(s3:Symbol) WHERE s1.class = 19 AND s2.class = 8 AND s3.class = 13 RETURN COUNT(s2) > 0"
    },
    {
        "question":"Can you find any symbol in class 21 that connects symbols of classes 8 and 10 at the same time?",
        "query": "MATCH (s1:Symbol)-[:CONNECTED_TO]-(s2:Symbol)-[:CONNECTED_TO]-(s3:Symbol) WHERE s1.class = 8 AND s2.class = 21 AND s3.class = 10 RETURN COUNT(s2) > 0"
    },
    {
        "question":"Can you determine if symbols of class 10 are situated between those of class 4 and class 12?",
        "query": "MATCH (s1:Symbol)-[:CONNECTED_TO]-(s2:Symbol)-[:CONNECTED_TO]-(s3:Symbol) WHERE s1.class = 4 AND s2.class = 10 AND s3.class = 12 RETURN COUNT(s2) > 0"
    },
    {
        "question":"Is it possible to identify symbols in class 29 on one side and class 17 on another side of class 25 symbol?",
        "query": "MATCH (s1:Symbol)-[:CONNECTED_TO]-(s2:Symbol)-[:CONNECTED_TO]-(s3:Symbol) WHERE s1.class = 29 AND s2.class = 25 AND s3.class = 17 RETURN COUNT(s2) > 0"
    },
    {
        "question":"Can you provide a list of tags for symbols in class 8 where the tags start with ZX?",
        "query": "MATCH (s:Symbol)WHERE s.class = 8 AND s.tag STARTS WITH 'ZX' RETURN s.tag"
    },
    {
        "question":"What are all the tags of class 7 symbols that have QW as their prefix?",
        "query": "MATCH (s:Symbol) WHERE s.class = 7 AND s.tag STARTS WITH 'QW' RETURN s.tag"
    },
    {
        "question":"Could you list the tags for class 22 symbols that begin with the string YKX?",
        "query": "MATCH (s:Symbol) WHERE s.class = 22 AND s.tag STARTS WITH 'YKX' RETURN s.tag"
    },
    {
        "question":"Fetch the tags of 28 symbols where each tag starts with the prefix MS.",
        "query": "MATCH (s:Symbol) WHERE s.class = 28 AND s.tag STARTS WITH 'MS' RETURN s.tag"
    },
    {
        "question":"Can you return the tags of all class 14 symbols that start with FU as their prefix?",
        "query": "MATCH (s:Symbol) WHERE s.class = 14 AND s.tag STARTS WITH 'FU' RETURN s.tag"
    }

]