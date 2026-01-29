
# API ARCHITECTURE

* Route file is the entry point for all the apis, 
  We will use route file for request and and response handling  
  In the route file we will call service function and only accept and return the response 
* Schemas are for validation of request and response structure
* we will write any busines logic and dbqueries in service


### steps to crete a api
 1. create a route file with that module name, naming convention - route_module.py
 2. create a response model in schema for response structure, but first create a Base response structure
 3. Now in the route's response_model wrap the specific model with in the base response
 4. now in the  route file call the service function and pass the required paramtere
 5. Do all the business logic  in service file.
 6. And db queries in the repository file

 Optional
 7. For common helper function we will create a file in helpers.helper.py 



# API LIST

## Category
 
 1. /categories ->list all the categories with text search, pagination
 2. /categories/{slug} -> fetch single category by slug
 3. /categories -> create {name, image, description}
 4. /categories/{slug} -> update {name, image, description}
 5. /categories/{slug} -> delete softdelete